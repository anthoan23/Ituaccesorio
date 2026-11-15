import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

URL_ORDENES_COMPRA = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/ordenes_compra"
TIEMPO_ESPERA = 10

# Prueba autocontenida: crea su propia orden temporal (ID autogenerado tipo
# OC000000X) con el primer empleado, el primer proveedor y el primer producto
# disponibles (cantidad 2). No depende del orden de ejecucion ni muta la semilla.


def test_crear_orden_compra(driver):
    driver.get(URL_ORDENES_COMPRA)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # La tabla de pendientes termina de cargar (fetch inicial)
    espera.until(
        lambda d: "Cargando" not in d.find_element(By.ID, "tabla-ordenes-pendientes").text
    )
    ids_antes = {
        fila.get_attribute("data-id")
        for fila in driver.find_elements(
            By.CSS_SELECTOR, "#tabla-ordenes-pendientes tr[data-id]"
        )
    }

    # Abrir el modal de registro; los empleados se cargan por fetch
    driver.find_element(By.ID, "btn-registrar-entrada").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-registrar-entrada")))
    espera.until(
        lambda d: len(Select(d.find_element(By.ID, "entrada-id-empleado")).options) > 1
    )
    Select(driver.find_element(By.ID, "entrada-id-empleado")).select_by_index(1)

    # Primer proveedor disponible
    driver.find_element(By.ID, "btn-desplegar-proveedores").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-seleccionar-proveedor")))
    fila_proveedor = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#lista-proveedores tr[data-proveedor-id]")
        )
    )
    nombre_proveedor = fila_proveedor.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
    fila_proveedor.click()

    # Cargar los productos del proveedor es un POST: el interceptor global de
    # fetch abre el feedback-modal encima de los demas modales; se espera su
    # autocierre antes de volver a interactuar.
    espera.until(EC.visibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Primer producto del proveedor
    driver.find_element(By.ID, "btn-desplegar-productos").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-seleccionar-productos")))
    fila_producto = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#lista-productos tr[data-producto-id]")
        )
    )
    nombre_producto = fila_producto.find_element(By.CSS_SELECTOR, "td:nth-child(3)").text
    fila_producto.click()

    # Subir la cantidad a 2 con el boton "+"
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#tabla-productos-seleccionados .cantidad-valor")
        )
    )
    driver.find_element(
        By.CSS_SELECTOR, "#tabla-productos-seleccionados button.btn-cantidad[data-op='mas']"
    ).click()
    espera.until(
        lambda d: d.find_element(
            By.CSS_SELECTOR, "#tabla-productos-seleccionados .cantidad-valor"
        ).text
        == "2"
    )

    # Registrar la orden (POST /api/ordenes_compra/agregar)
    boton_guardar = driver.find_element(By.ID, "btn-guardar-entrada")
    espera.until(lambda d: not boton_guardar.get_attribute("disabled"))
    boton_guardar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-registrar-entrada")))

    # La orden creada aparece en pendientes con un ID que no existia
    def fila_nueva(d):
        for fila in d.find_elements(
            By.CSS_SELECTOR, "#tabla-ordenes-pendientes tr[data-id]"
        ):
            if fila.get_attribute("data-id") not in ids_antes:
                return fila
        return False

    fila_orden = espera.until(fila_nueva)
    id_orden = fila_orden.get_attribute("data-id")
    assert nombre_proveedor in fila_orden.text
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Orden de compra creada: {id_orden} "
        f"(proveedor: {nombre_proveedor}, producto: {nombre_producto}, cantidad 2)"
    )
