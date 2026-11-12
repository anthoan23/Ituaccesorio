import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_CARGOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/cargos"
TIEMPO_ESPERA = 10

# [nombre]
DATOS_CARGO = ["Cargo Editado"]


def test_eliminar_cargo(driver):
    driver.get(URL_CARGOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-cargos']//tr[td[2][normalize-space(.)='{DATOS_CARGO[0]}']]",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']").click()

    espera.until(
        EC.visibility_of_element_located((By.ID, "modal-eliminar-cargo"))
    )
    driver.find_element(By.ID, "btn-confirmar-eliminar-cargo").click()

    espera.until(
        EC.invisibility_of_element_located((By.ID, "modal-eliminar-cargo"))
    )
    espera.until(
        EC.invisibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-cargos']//tr[td[2][normalize-space(.)='{DATOS_CARGO[0]}']]",
            )
        )
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Cargo eliminado: {DATOS_CARGO[0]}")
