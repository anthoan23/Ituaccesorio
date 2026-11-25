import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

URL_CLIENTES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/clientes"
TIEMPO_ESPERA = 10

# [rif, razon_social, telefono]
# El telefono es obligatorio en el formulario de persona juridica
DATOS_CLIENTE_JURIDICO = ["J-80012345-1", "Empresa Prueba C.A.", "04149998877"]


def test_crear_cliente_juridico(driver):
    driver.get(URL_CLIENTES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-clientes tr")))

    driver.find_element(By.ID, "btn-nuevo-cliente").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-cliente")))

    # El mismo modal de registro cambia los campos al elegir persona juridica
    Select(driver.find_element(By.ID, "tipo-cliente")).select_by_value("juridico")
    espera.until(EC.visibility_of_element_located((By.ID, "rif-input")))

    driver.find_element(By.ID, "rif-input").send_keys(DATOS_CLIENTE_JURIDICO[0])
    driver.find_element(By.ID, "razon-social-input").send_keys(DATOS_CLIENTE_JURIDICO[1])
    driver.find_element(By.ID, "telefono-input").send_keys(DATOS_CLIENTE_JURIDICO[2])
    driver.find_element(By.CSS_SELECTOR, "#form-cliente button[type='submit']").click()

    # La columna 3 de la tabla muestra la razon social de la persona juridica
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-clientes']//tr[td[3][normalize-space(.)='{DATOS_CLIENTE_JURIDICO[1]}']]",
            )
        )
    )
    assert "Persona Jurídica" in fila.text
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Cliente juridico creado: {DATOS_CLIENTE_JURIDICO[0]} - {DATOS_CLIENTE_JURIDICO[1]}")
