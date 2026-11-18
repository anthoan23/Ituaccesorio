import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_CLIENTES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/clientes"
TIEMPO_ESPERA = 10

# [cedula, nombre]
DATOS_CLIENTE = ["65432109", "Cliente Editado"]


def test_eliminar_cliente(driver):
    driver.get(URL_CLIENTES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-clientes']//tr[td[1][normalize-space(.)='{DATOS_CLIENTE[0]}']]",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']").click()

    espera.until(EC.visibility_of_element_located((By.ID, "modal-eliminar-cliente")))
    driver.find_element(By.ID, "btn-confirmar-eliminar-cliente").click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-eliminar-cliente")))
    espera.until(
        EC.invisibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-clientes']//tr[td[1][normalize-space(.)='{DATOS_CLIENTE[0]}']]",
            )
        )
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Cliente eliminado: {DATOS_CLIENTE[0]} - {DATOS_CLIENTE[1]}")
