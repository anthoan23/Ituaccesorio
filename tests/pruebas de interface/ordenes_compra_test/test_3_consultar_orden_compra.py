import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from helpers import esperar_feedback, quitar_hover

URL_ORDENES_COMPRA = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/ordenes_compra"
TIEMPO_ESPERA = 10

# Prueba autocontenida: crea por la UI su propia orden temporal (ID
# autogenerado tipo OC000000X, primer empleado + primer proveedor CON
# productos + primer producto, cantidad 2) y despues consulta su detalle desde
# la tabla de pendientes (modal 'Detalle de orden'). No depende del orden de
# ejecucion ni muta la semilla. La orden se anula al final para dejar la BD
# como estaba.
#
# NOTA DE LA APP: el modelo genera el ID con MAX(ID_orden_compra)
# lexicografico; con IDs de longitudes mezcladas (p. ej. "OC000901") el alta
# falla -> la suite debe correr contra una BD recien sembrada.

TITULO_PAGINA = "Ituaccesorio - Órdenes de compra"


def test_consultar_orden_compra(driver):
    import json
    import urllib.request

    base = os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')

    def api_get(ruta):
        with urllib.request.urlopen(f"{base}{ruta}", timeout=5) as respuesta:
            return json.loads(respuesta.read())

    # Proveedor con productos (solo lectura)
    proveedor_con_productos = None
    for proveedor in api_get("/api/proveedores")["proveedores"]:
        productos = api_get(f"/api/productos_proveedor/{proveedor['id']}").get("productos", [])
        if productos:
            proveedor_con_productos = proveedor
            break
    assert proveedor_con_productos, "No hay proveedores con productos en la BD"

    driver.get(URL_ORDENES_COMPRA)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    assert driver.title == TITULO_PAGINA
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Órdenes de compra"

    # ---- Creacion de la orden temporal (flujo minimo) ----
    espera.until(
        lambda d: "Cargando" not in d.find_element(By.ID, "tabla-ordenes-pendientes").text
    )
    ids_antes = {
        fila.get_attribute("data-id")
        for fila in driver.find_elements(By.CSS_SELECTOR, "#tabla-ordenes-pendientes tr[data-id]")
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
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                f"#lista-proveedores tr[data-proveedor-id='{proveedor_con_productos['id']}']",
            )
        )
    )
    nombre_proveedor = fila_proveedor.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
    fila_proveedor.click()
    # El POST de productos del proveedor abre el feedback-modal: esperar su autocierre
    espera.until(EC.visibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    boton_productos = driver.find_element(By.ID, "btn-desplegar-productos")
    espera.until(lambda d: not boton_productos.get_attribute("disabled"))
    boton_productos.click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-seleccionar-productos")))
    fila_producto = espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#lista-productos tr[data-producto-id]"))
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
        == "2"
    )

    boton_guardar = driver.find_element(By.ID, "btn-guardar-entrada")
    espera.until(lambda d: not boton_guardar.get_attribute("disabled"))
    boton_guardar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-registrar-entrada")))
    esperar_feedback(espera, tipo="success", titulo="Éxito", mensaje="Orden de compra registrada exitosamente.")

    def fila_nueva(d):
        for fila in d.find_elements(By.CSS_SELECTOR, "#tabla-ordenes-pendientes tr[data-id]"):
            if fila.get_attribute("data-id") not in ids_antes:
                return fila
        return False

    id_orden = espera.until(fila_nueva).get_attribute("data-id")

    # ---- Consulta del detalle desde el boton "ver" de la fila ----
    fila_orden = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, f"#tabla-ordenes-pendientes tr[data-id='{id_orden}']")
        )
    )
    fila_orden.find_element(By.CSS_SELECTOR, "button[data-action='ver']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-detalle-orden")))
    quitar_hover(driver)

    # --- Modal 'Detalle de orden': titulo, labels y datos de la orden ---
    assert driver.find_element(By.ID, "modal-detalle-orden-title").text == "Detalle de orden"
    info_detalle = driver.find_element(By.ID, "detalle-orden-info")
    labels_detalle = [
        elemento.get_attribute("textContent").strip()
        for elemento in info_detalle.find_elements(By.CSS_SELECTOR, ".device-detail__label")
    ]
    assert labels_detalle == ["ID Orden", "Proveedor", "Fecha", "Estado", "Realizado por"]
    assert f"#{id_orden}" in info_detalle.text
    assert nombre_proveedor in info_detalle.text
    assert "Pendiente" in info_detalle.text

    # Encabezados de la tabla de productos del detalle
    encabezados_detalle = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, "#modal-detalle-orden .table thead th")
    ]
    assert encabezados_detalle == ["Marca", "Producto", "Cantidad", "Costo", "Subtotal"]

    # El producto creado se lista en el detalle con su cantidad
    def fila_producto_detalle(d):
        for fila in d.find_elements(By.CSS_SELECTOR, "#detalle-orden-productos tr"):
            celdas = fila.find_elements(By.CSS_SELECTOR, "td")
            if len(celdas) >= 3 and celdas[1].text == nombre_producto:
                return fila
        return False

    fila_detalle = espera.until(fila_producto_detalle)
    assert fila_detalle.find_element(By.CSS_SELECTOR, "td:nth-child(3)").text == "2"

    # Cerrar el modal de detalle
    driver.find_element(
        By.CSS_SELECTOR, "#modal-detalle-orden button[data-close-modal]"
    ).click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-detalle-orden")))

    # --- Limpieza: anular la orden consultada para dejar la BD como estaba ---
    fila_orden = driver.find_element(By.CSS_SELECTOR, f"#tabla-ordenes-pendientes tr[data-id='{id_orden}']")
    fila_orden.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-confirmar-eliminar-orden")))
    driver.find_element(By.ID, "btn-confirmar-eliminar-orden").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-confirmar-eliminar-orden")))
    esperar_feedback(espera, tipo="success", titulo="Éxito", mensaje="Orden eliminada exitosamente.")
    espera.until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, f"#tabla-ordenes-pendientes tr[data-id='{id_orden}']"))
    )
    print(
        f"Orden consultada y anulada (limpieza): {id_orden} "
        f"(proveedor: {nombre_proveedor}, producto: {nombre_producto})"
    )
