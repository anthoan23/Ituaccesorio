import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_CARGOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/cargos"
TIEMPO_ESPERA = 10

# [nombre, descripcion]
DATOS_CARGO = ["Cargo Prueba", "Descripcion de cargo de prueba"]


def test_crear_cargo(driver):
    driver.get(URL_CARGOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#tabla-cargos tr[data-id]")
        )
    )

    driver.find_element(
        By.CSS_SELECTOR, "#form-cargo input[name='nombre_cargo']"
    ).send_keys(DATOS_CARGO[0])
    driver.find_element(
        By.CSS_SELECTOR, "#form-cargo textarea[name='descripcion_cargo']"
    ).send_keys(DATOS_CARGO[1])
    driver.find_element(By.CSS_SELECTOR, "#form-cargo button[type='submit']").click()

    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-cargos']//tr[td[2][normalize-space(.)='{DATOS_CARGO[0]}']]",
            )
        )
    )
    assert DATOS_CARGO[1] in fila.text
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Cargo creado: {DATOS_CARGO[0]}")
