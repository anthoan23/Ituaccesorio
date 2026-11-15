import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_TRADEIN = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/trade-in"
TIEMPO_ESPERA = 10

# PRERREQUISITO: la BD debe tener equipos Apple (marca Apple, clase Telefono y
# existencias > 0) porque el select de /trade-in se llena al renderizar la vista.


def test_listar_equipos(driver):
    driver.get(URL_TRADEIN)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # El select de equipos es server-side; presence_of_all_elements_located
    # sigue esperando mientras la lista de opciones quede vacía.
    opciones = espera.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "#tradein-equipo option:not([value=''])")
        )
    )
    assert len(opciones) >= 1, "No hay equipos cargados en el select de /trade-in."

    # El panel de resultado y el botón de cotizar deben estar presentes
    espera.until(EC.presence_of_element_located((By.ID, "tradein-resultado")))
    assert driver.find_element(By.ID, "tradein-submit").is_displayed()

    radios_liberado = driver.find_elements(By.CSS_SELECTOR, "input[name='liberado']")
    casillas_fallas = driver.find_elements(By.CSS_SELECTOR, "input[name='fallas']")
    assert len(radios_liberado) == 2, "Faltan las opciones de liberación del equipo."
    assert len(casillas_fallas) >= 1, "No hay casillas de fallas en la página."

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Equipos listados en /trade-in: {len(opciones)} opción(es). "
        f"Primera: {opciones[0].text}"
    )
