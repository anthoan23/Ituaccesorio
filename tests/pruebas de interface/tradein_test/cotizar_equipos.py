import os
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

URL_TRADEIN = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/trade-in"
TIEMPO_ESPERA = 10

# Etiquetas reales de las casillas de fallas (views/tradein.html / FALLAS_COTIZACION)
FALLAS_PRUEBA = ["LCD", "Mica"]

# PRERREQUISITO: equipos Apple en existencias y repuestos con costo en la BD
# (el backend deduce el costo del repuesto). El ID de inventario del equipo debe
# ser numérico porque /api/trade-in/cotizar lo valida con validar_numero (1-10 dígitos).


def test_cotizar_equipos(driver):
    driver.get(URL_TRADEIN)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Esperar a que el select de equipos tenga opciones cargadas
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#tradein-equipo option:not([value=''])")
        )
    )

    # Seleccionar el primer equipo (índice 0 = "Selecciona un equipo")
    equipo = Select(driver.find_element(By.ID, "tradein-equipo"))
    equipo.select_by_index(1)

    # Liberación del equipo: "Sí, está liberado"
    driver.find_element(By.CSS_SELECTOR, "input[name='liberado'][value='si']").click()

    # Marcar las fallas por su etiqueta visible (LCD y Mica)
    for etiqueta in FALLAS_PRUEBA:
        driver.find_element(
            By.XPATH,
            f"//label[contains(@class,'tradein-check')]"
            f"[span[normalize-space()='{etiqueta}']]/input",
        ).click()

    # Enviar el formulario de cotización
    driver.find_element(By.ID, "tradein-submit").click()

    # Esperar el resultado del fetch a /api/trade-in/cotizar
    espera.until(
        EC.text_to_be_present_in_element(
            (By.ID, "tradein-total-fallas"), str(len(FALLAS_PRUEBA))
        )
    )
    for etiqueta in FALLAS_PRUEBA:
        espera.until(
            EC.presence_of_element_located(
                (By.XPATH, f"//ul[@id='tradein-detalles']//li[contains(., '{etiqueta}')]")
            )
        )

    monto = driver.find_element(By.ID, "tradein-monto").text
    assert re.match(r"^\$\d[\d,]*\.\d{2}$", monto), f"Monto estimado inválido: {monto}"
    mensajes = driver.find_element(By.ID, "tradein-mensajes").text
    assert mensajes.strip(), "El panel de mensajes de la cotización quedó vacío."

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Cotización generada: {monto} | Total fallas: {len(FALLAS_PRUEBA)} "
        f"({', '.join(FALLAS_PRUEBA)})"
    )
