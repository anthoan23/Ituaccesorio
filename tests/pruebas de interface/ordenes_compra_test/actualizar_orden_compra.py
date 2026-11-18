import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

URL_ORDENES_COMPRA = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/ordenes_compra"
TIEMPO_ESPERA = 10

# Prueba autocontenida: crea por la UI su propia orden temporal (ID
# autogenerado tipo OC000000X, primer empleado + primer proveedor + primer
# producto, cantidad 2) y despues la edita desde su fila en pendientes
# (modal de actualizar), cambiando la cantidad a 3. No depende del orden de
# ejecucion ni muta la semilla.

CANTIDAD_INICIAL = "2"
CANTIDAD_NUEVA = "3"


def test_actualizar_orden_compra(driver):
    driver.get(URL_ORDENES_COMPRA)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # ---- Creacion de la orden temporal (flujo minimo) ----
    espera.until(
        lambda d: "Cargando" not in d.find_element(By.ID, "tabla-ordenes-pendientes").text
    )
    ids_antes = {
        fila.get_attribute("data-id")
        for fila in driver.find_elements(
            By.CSS_SELECTOR, "#tabla-ordenes-pendientes tr[data-id]"
        )
    }
    driver.find_element(By.ID, "btn-registrar-entrada").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-registrar-entrada")))
    espera.until(
        lambda d: len(Select(d.find_element(By.ID, "entrada-id-empleado")).options) > 1
    )
    Select(driver.find_element(By.ID, "entrada-id-empleado")).select_by_index(1)

    driver.find_element(By.ID, "btn-desplegar-proveedores").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-seleccionar-proveedor")))
    fila_proveedor = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#lista-proveedores tr[data-proveedor-id]")
        )
    )
    nombre_proveedor = fila_proveedor.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
    fila_proveedor.click()
    # El POST de productos del proveedor abre el feedback-modal: esperar su autocierre
    espera.until(EC.visibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    driver.find_element(By.ID, "btn-desplegar-productos").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-seleccionar-productos")))
    fila_producto = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#lista-productos tr[data-producto-id]")
        )
    )
    nombre_producto = fila_producto.find_element(By.CSS_SELECTOR, "td:nth-child(3)").text
    fila_producto.click()

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
        == CANTIDAD_INICIAL
    )

    boton_guardar = driver.find_element(By.ID, "btn-guardar-entrada")
    espera.until(lambda d: not boton_guardar.get_attribute("disabled"))
    boton_guardar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-registrar-entrada")))

    def fila_nueva(d):
        for fila in d.find_elements(
            By.CSS_SELECTOR, "#tabla-ordenes-pendientes tr[data-id]"
        ):
            if fila.get_attribute("data-id") not in ids_antes:
                return fila
        return False

    id_orden = espera.until(fila_nueva).get_attribute("data-id")
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # ---- Edicion desde el boton "editar" de la fila ----
    fila_orden = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, f"#tabla-ordenes-pendientes tr[data-id='{id_orden}']")
        )
    )
    fila_orden.find_element(By.CSS_SELECTOR, "button[data-action='editar']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-editar-orden")))

    # El JS recarga los productos del proveedor (POST) -> feedback-modal encima
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # El empleado de la orden se selecciona con un setTimeout de 300 ms
    espera.until(lambda d: d.find_element(By.ID, "editar-id-empleado").get_attribute("value"))

    espera.until(
        lambda d: d.find_element(
            By.CSS_SELECTOR, "#tabla-productos-seleccionados-editar .cantidad-valor"
        ).text
        == CANTIDAD_INICIAL
    )
    driver.find_element(
        By.CSS_SELECTOR,
        "#tabla-productos-seleccionados-editar button.btn-cantidad[data-op='mas']",
    ).click()
    espera.until(
        lambda d: d.find_element(
            By.CSS_SELECTOR, "#tabla-productos-seleccionados-editar .cantidad-valor"
        ).text
        == CANTIDAD_NUEVA
    )

    # Actualizar la orden (PUT /api/ordenes_compra/actualizar)
    boton_actualizar = driver.find_element(By.ID, "btn-guardar-editar")
    espera.until(lambda d: not boton_actualizar.get_attribute("disabled"))
    boton_actualizar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-editar-orden")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # ---- Verificacion del cambio en el detalle de la orden ----
    fila_orden = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, f"#tabla-ordenes-pendientes tr[data-id='{id_orden}']")
        )
    )
    fila_orden.find_element(By.CSS_SELECTOR, "button[data-action='ver']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-detalle-orden")))

    info_detalle = driver.find_element(By.ID, "detalle-orden-info")
    assert nombre_proveedor in info_detalle.text

    def fila_producto_detalle(d):
        for fila in d.find_elements(By.CSS_SELECTOR, "#detalle-orden-productos tr"):
            celdas = fila.find_elements(By.CSS_SELECTOR, "td")
            if len(celdas) >= 3 and celdas[1].text == nombre_producto:
                return celdas[2].text
        return False

    cantidad_detalle = espera.until(fila_producto_detalle)
    assert cantidad_detalle == CANTIDAD_NUEVA

    driver.find_element(
        By.CSS_SELECTOR, "#modal-detalle-orden button[data-close-modal]"
    ).click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-detalle-orden")))
    print(
        f"Orden actualizada: {id_orden} - {nombre_producto} "
        f"cantidad {CANTIDAD_INICIAL} -> {CANTIDAD_NUEVA}"
    )
