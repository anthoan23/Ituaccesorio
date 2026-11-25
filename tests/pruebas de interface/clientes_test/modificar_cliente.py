import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_CLIENTES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/clientes"
TIEMPO_ESPERA = 10

# [cedula, nombre_nuevo]
DATOS_CLIENTE = ["65432109", "Cliente Editado"]


def test_modificar_cliente(driver):
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
    fila.find_element(By.CSS_SELECTOR, "button[data-action='editar']").click()

    espera.until(EC.visibility_of_element_located((By.ID, "modal-cliente")))
    nombre = driver.find_element(By.CSS_SELECTOR, "#form-cliente input[name='nombre']")
    nombre.clear()
    nombre.send_keys(DATOS_CLIENTE[1])
    driver.find_element(By.CSS_SELECTOR, "#form-cliente button[type='submit']").click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-cliente")))
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-clientes']//tr[td[1][normalize-space(.)='{DATOS_CLIENTE[0]}']]",
            )
        )
    )
    assert fila.find_element(By.CSS_SELECTOR, "td:nth-child(3)").text == DATOS_CLIENTE[1]
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Cliente modificado: cedula {DATOS_CLIENTE[0]} -> nombre {DATOS_CLIENTE[1]}")
