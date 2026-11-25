import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

# Módulo de entregas: consultar personal de delivery (pestaña "Personal Delivery")
# Requiere el registro creado por test_1_crear_personal_delivery.py
# ("Personal Delivery", cédula 30124556). No existe botón "ver" en la fila
# (solo editar/eliminar), por lo que se verifica el contenido de la fila.
URL_ENTREGAS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/entregas"
TIEMPO_ESPERA = 10

# [cedula, nombre_completo]
DATOS_PERSONAL = ["30124556", "Personal Delivery"]

TITULO_PAGINA = "Ituaccesorio - Entregas"


def test_consultar_personal_delivery(driver):
    driver.get(URL_ENTREGAS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    assert driver.title == TITULO_PAGINA
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Entregas"

    # --- Cambiar a la pestaña Personal Delivery ---
    driver.find_element(By.ID, "tab-personal").click()
    espera.until(lambda d: d.find_element(By.ID, "tab-personal").get_attribute("aria-selected") == "true")

    # --- Filtrar con el buscador de la tabla para que la fila quede visible ---
    buscador = driver.find_element(By.CSS_SELECTOR, "#tab-panel-personal .table-controls__input")
    buscador.send_keys(DATOS_PERSONAL[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-personal']//tr[td[1][contains(., '{DATOS_PERSONAL[0]}')]]",
            )
        )
    )
    cedula = fila.find_element(By.CSS_SELECTOR, "td:nth-child(1)").get_attribute("textContent").strip()
    nombre = fila.find_element(By.CSS_SELECTOR, "td:nth-child(2)").get_attribute("textContent").strip()
    assert cedula == DATOS_PERSONAL[0]
    assert nombre == DATOS_PERSONAL[1]

    # --- Iconos de la fila: editar (amarillo) y eliminar (rojo); no hay "ver" ---
    quitar_hover(driver)
    acciones = fila.find_elements(By.CSS_SELECTOR, "button[data-action]")
    assert len(acciones) == 2, "La fila de personal solo debe tener editar y eliminar"
    assert estilo_css(
        driver, fila.find_element(By.CSS_SELECTOR, "button[data-action='editar-personal']"), "borderTopColor"
    ) == "rgb(243, 197, 0)", "El icono 'editar' de la fila deberia ser amarillo"
    assert estilo_css(
        driver, fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar-personal']"), "borderTopColor"
    ) == "rgb(220, 38, 38)", "El icono 'eliminar' de la fila deberia ser rojo"
    print(f"Personal delivery consultado: {nombre} ({cedula})")
