import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Módulo de entregas: consultar personal de delivery (pestaña "Personal Delivery")
# Requiere el registro creado por crear_personal_delivery.py
# ("Personal Delivery", cédula 30124556). No existe botón "ver" en la fila
# (solo editar/eliminar), por lo que se verifica el contenido de la fila.
URL_ENTREGAS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/entregas"
TIEMPO_ESPERA = 10

# [cedula, nombre_completo]
DATOS_PERSONAL = ["30124556", "Personal Delivery"]


def test_consultar_personal_delivery(driver):
    driver.get(URL_ENTREGAS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # Cambiar a la pestaña Personal Delivery
    driver.find_element(By.ID, "tab-personal").click()
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-personal']//tr[td[2][normalize-space(.)='{DATOS_PERSONAL[1]}']]",
            )
        )
    )
    cedula = fila.find_element(By.CSS_SELECTOR, "td:nth-child(1)").text
    nombre = fila.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
    assert DATOS_PERSONAL[0] in cedula
    assert nombre == DATOS_PERSONAL[1]
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Personal delivery consultado: {nombre} ({cedula.strip()})")
