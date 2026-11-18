import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

URL_PROVEEDORES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/proveedores"
TIEMPO_ESPERA = 10

# [rif, nombre, tipo, prefijo, sufijo, correo, limite_credito, direccion]
DATOS_PROVEEDOR = [
    "J-80054321-1",
    "Proveedor Prueba",
    "Nacional",
    "0414",
    "1234567",
    "proveedor.prueba@ituaccesorio.com",
    "1000",
    "Caracas",
]

# La columna 3 de la tabla es el nombre del proveedor
FILA_PROVEEDOR = f"//*[@id='tabla-proveedores']//tr[td[3][normalize-space(.)='{DATOS_PROVEEDOR[1]}']]"


def test_crear_proveedor(driver):
    driver.get(URL_PROVEEDORES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    driver.find_element(
        By.CSS_SELECTOR, "[data-open-modal='modal-proveedor-crear']"
    ).click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-proveedor-crear")))

    driver.find_element(By.ID, "c-id").send_keys(DATOS_PROVEEDOR[0])
    driver.find_element(By.ID, "c-nombre").send_keys(DATOS_PROVEEDOR[1])
    Select(driver.find_element(By.ID, "c-tipo")).select_by_visible_text(
        DATOS_PROVEEDOR[2]
    )
    Select(driver.find_element(By.ID, "c-celular-prefijo")).select_by_visible_text(
        DATOS_PROVEEDOR[3]
    )
    driver.find_element(By.ID, "c-celular-sufijo").send_keys(DATOS_PROVEEDOR[4])
    driver.find_element(By.ID, "c-correo").send_keys(DATOS_PROVEEDOR[5])
    driver.find_element(By.ID, "c-limite").send_keys(DATOS_PROVEEDOR[6])
    driver.find_element(By.ID, "c-direccion").send_keys(DATOS_PROVEEDOR[7])

    driver.find_element(
        By.CSS_SELECTOR, "#form-proveedor-crear button[type='submit']"
    ).click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-proveedor-crear")))
    fila = espera.until(EC.presence_of_element_located((By.XPATH, FILA_PROVEEDOR)))
    assert DATOS_PROVEEDOR[0] in fila.text
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Proveedor creado: {DATOS_PROVEEDOR[1]}")
