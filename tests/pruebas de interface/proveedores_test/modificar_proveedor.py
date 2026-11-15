import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_PROVEEDORES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/proveedores"
TIEMPO_ESPERA = 10

# [nombre_actual, nombre_nuevo]
DATOS_PROVEEDOR = ["Proveedor Prueba", "Proveedor Editado"]

# La columna 3 de la tabla es el nombre del proveedor
FILA_PROVEEDOR_ACTUAL = (
    f"//*[@id='tabla-proveedores']//tr[td[3][normalize-space(.)='{DATOS_PROVEEDOR[0]}']]"
)
FILA_PROVEEDOR_EDITADA = (
    f"//*[@id='tabla-proveedores']//tr[td[3][normalize-space(.)='{DATOS_PROVEEDOR[1]}']]"
)


def test_modificar_proveedor(driver):
    driver.get(URL_PROVEEDORES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(
        EC.presence_of_element_located((By.XPATH, FILA_PROVEEDOR_ACTUAL))
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='editar']").click()

    # El JS llena el formulario con los datos del proveedor antes de abrir el modal
    espera.until(EC.visibility_of_element_located((By.ID, "modal-proveedor-editar")))
    espera.until(
        lambda navegador: navegador.find_element(By.ID, "e-nombre").get_attribute(
            "value"
        )
        == DATOS_PROVEEDOR[0]
    )

    nombre = driver.find_element(By.ID, "e-nombre")
    nombre.clear()
    nombre.send_keys(DATOS_PROVEEDOR[1])
    driver.find_element(
        By.CSS_SELECTOR, "#form-proveedor-editar button[type='submit']"
    ).click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-proveedor-editar")))
    fila_editada = espera.until(
        EC.presence_of_element_located((By.XPATH, FILA_PROVEEDOR_EDITADA))
    )
    assert DATOS_PROVEEDOR[1] in fila_editada.text
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Proveedor modificado: {DATOS_PROVEEDOR[0]} -> {DATOS_PROVEEDOR[1]}")
