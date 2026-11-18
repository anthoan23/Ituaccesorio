import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_CARGOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/cargos"
TIEMPO_ESPERA = 10

# [nombre_actual, nombre_nuevo, descripcion_nueva]
DATOS_CARGO = ["Cargo Prueba", "Cargo Editado", "Descripcion de cargo editada"]


def test_modificar_cargo(driver):
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
    fila.find_element(By.CSS_SELECTOR, "button[data-action='editar']").click()

    espera.until(
        EC.visibility_of_element_located((By.ID, "modal-editar-cargo"))
    )
    nombre = driver.find_element(By.ID, "editar-nombre-cargo")
    nombre.clear()
    nombre.send_keys(DATOS_CARGO[1])
    descripcion = driver.find_element(By.ID, "editar-descripcion-cargo")
    descripcion.clear()
    descripcion.send_keys(DATOS_CARGO[2])
    driver.find_element(
        By.CSS_SELECTOR, "#form-editar-cargo button[type='submit']"
    ).click()

    espera.until(
        EC.invisibility_of_element_located((By.ID, "modal-editar-cargo"))
    )
    espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-cargos']//tr[td[2][normalize-space(.)='{DATOS_CARGO[1]}']]",
            )
        )
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Cargo modificado: {DATOS_CARGO[0]} -> {DATOS_CARGO[1]}")
