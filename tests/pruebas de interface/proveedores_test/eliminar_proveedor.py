import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_PROVEEDORES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/proveedores"
TIEMPO_ESPERA = 10

# Nombre del proveedor que se va a eliminar
NOMBRE_PROVEEDOR = "Proveedor Editado"

# La columna 3 de la tabla es el nombre del proveedor
FILA_PROVEEDOR = (
    f"//*[@id='tabla-proveedores']//tr[td[3][normalize-space(.)='{NOMBRE_PROVEEDOR}']]"
)


def test_eliminar_proveedor(driver):
    driver.get(URL_PROVEEDORES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(EC.presence_of_element_located((By.XPATH, FILA_PROVEEDOR)))
    fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']").click()

    # El JS consulta los productos asociados y abre su propio modal de confirmación
    espera.until(
        EC.visibility_of_element_located((By.ID, "confirmacion-modal-proveedores"))
    )
    driver.find_element(By.ID, "btn-confirmar-accion-proveedores").click()

    espera.until(
        EC.invisibility_of_element_located((By.ID, "confirmacion-modal-proveedores"))
    )
    espera.until(EC.invisibility_of_element_located((By.XPATH, FILA_PROVEEDOR)))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Proveedor eliminado: {NOMBRE_PROVEEDOR}")
