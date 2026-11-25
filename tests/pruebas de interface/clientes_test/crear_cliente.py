import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

URL_CLIENTES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/clientes"
TIEMPO_ESPERA = 10

# [cedula, nombre, apellido, celular, correo, direccion]
DATOS_CLIENTE = ["65432109", "Cliente", "Prueba", "04141234567", "cliente.prueba@ituaccesorio.com", "Barquisimeto"]


def test_crear_cliente(driver):
    driver.get(URL_CLIENTES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-clientes tr")))

    driver.find_element(By.ID, "btn-nuevo-cliente").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-cliente")))

    # El formulario pide el tipo de cliente y oculta/muestra campos segun la eleccion
    Select(driver.find_element(By.ID, "tipo-cliente")).select_by_value("natural")
    espera.until(EC.visibility_of_element_located((By.ID, "cedula-input")))

    driver.find_element(By.ID, "cedula-input").send_keys(DATOS_CLIENTE[0])
    driver.find_element(
        By.CSS_SELECTOR, "#form-cliente input[name='nombre']"
    ).send_keys(DATOS_CLIENTE[1])
    driver.find_element(
        By.CSS_SELECTOR, "#form-cliente input[name='apellido']"
    ).send_keys(DATOS_CLIENTE[2])
    driver.find_element(
        By.CSS_SELECTOR, "#form-cliente input[name='celular']"
    ).send_keys(DATOS_CLIENTE[3])
    driver.find_element(
        By.CSS_SELECTOR, "#form-cliente input[name='correo']"
    ).send_keys(DATOS_CLIENTE[4])
    driver.find_element(
        By.CSS_SELECTOR, "#form-cliente input[name='direccion']"
    ).send_keys(DATOS_CLIENTE[5])
    driver.find_element(By.CSS_SELECTOR, "#form-cliente button[type='submit']").click()

    # La primera columna de la tabla es la cedula del cliente
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-clientes']//tr[td[1][normalize-space(.)='{DATOS_CLIENTE[0]}']]",
            )
        )
    )
    assert DATOS_CLIENTE[1] in fila.text
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Cliente creado: {DATOS_CLIENTE[0]} - {DATOS_CLIENTE[1]} {DATOS_CLIENTE[2]}")
