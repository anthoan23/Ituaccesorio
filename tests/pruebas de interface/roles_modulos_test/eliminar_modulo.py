import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# [nombre]
DATOS_MODULO = ["ModuloEditado"]


def test_eliminar_modulo(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    driver.find_element(By.ID, "tab-modulos").click()
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-modulos']//tr[td[1][normalize-space(.)='{DATOS_MODULO[0]}']]",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='delete-modulo']").click()

    espera.until(EC.visibility_of_element_located((By.ID, "modal-confirmacion")))
    driver.find_element(By.ID, "confirmacion-btn").click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-confirmacion")))
    espera.until(
        EC.invisibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-modulos']//tr[td[1][normalize-space(.)='{DATOS_MODULO[0]}']]",
            )
        )
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Modulo eliminado: {DATOS_MODULO[0]}")
