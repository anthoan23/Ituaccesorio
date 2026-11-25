import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_PROVEEDORES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/proveedores"
TIEMPO_ESPERA = 10

# [rif, nombre, tipo, celular, correo, direccion]
DATOS_PROVEEDOR = [
    "J-80054321-1",
    "Proveedor Prueba",
    "Nacional",
    "04141234567",
    "proveedor.prueba@ituaccesorio.com",
    "Caracas",
]

# La columna 3 de la tabla es el nombre del proveedor
FILA_PROVEEDOR = f"//*[@id='tabla-proveedores']//tr[td[3][normalize-space(.)='{DATOS_PROVEEDOR[1]}']]"


def test_consultar_proveedor(driver):
    driver.get(URL_PROVEEDORES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(EC.presence_of_element_located((By.XPATH, FILA_PROVEEDOR)))
    fila.find_element(By.CSS_SELECTOR, "button[data-action='ver']").click()

    # El modal de detalle muestra los datos del proveedor y sus productos
    espera.until(EC.visibility_of_element_located((By.ID, "modal-proveedor-ver")))
    rif = driver.find_element(By.ID, "v-rif").text
    nombre = driver.find_element(By.ID, "v-nombre").text
    tipo = driver.find_element(By.ID, "v-tipo").text
    celular = driver.find_element(By.ID, "v-celular").text
    correo = driver.find_element(By.ID, "v-correo").text
    direccion = driver.find_element(By.ID, "v-direccion").text

    assert rif == DATOS_PROVEEDOR[0]
    assert nombre == DATOS_PROVEEDOR[1]
    assert tipo == DATOS_PROVEEDOR[2]
    assert celular == DATOS_PROVEEDOR[3]
    assert correo == DATOS_PROVEEDOR[4]
    assert direccion == DATOS_PROVEEDOR[5]

    driver.find_element(
        By.CSS_SELECTOR, "#modal-proveedor-ver [data-close-modal]"
    ).click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-proveedor-ver")))
    print(f"Proveedor consultado: {nombre} - {rif}")
