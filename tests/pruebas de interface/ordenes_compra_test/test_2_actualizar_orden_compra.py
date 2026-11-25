import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_ORDENES_COMPRA = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/ordenes_compra"
TIEMPO_ESPERA = 10

# Prueba autocontenida: crea por la UI su propia orden temporal (ID
# autogenerado tipo OC000000X, primer empleado + primer proveedor CON
# productos + primer producto, cantidad 2) y despues la edita desde su fila en
# pendientes (modal 'Editar orden de compra'), cambiando la cantidad a 3.
# No depende del orden de ejecucion ni muta la semilla. La orden se anula al
# final para dejar la BD como estaba.
#
# NOTA DE LA APP: el modelo genera el ID con MAX(ID_orden_compra)
# lexicografico; con IDs de longitudes mezcladas (p. ej. "OC000901") el alta
# falla -> la suite debe correr contra una BD recien sembrada.

CANTIDAD_INICIAL = "2"
CANTIDAD_NUEVA = "3"
TITULO_PAGINA = "Ituaccesorio - Órdenes de compra"


def test_actualizar_orden_compra(driver):
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
        == CANTIDAD_INICIAL
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

    # ---- Edicion desde el boton "editar" de la fila ----
    fila_orden = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, f"#tabla-ordenes-pendientes tr[data-id='{id_orden}']")
        )
    )
    fila_orden.find_element(By.CSS_SELECTOR, "button[data-action='editar']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-editar-orden")))
    quitar_hover(driver)

    # --- Modal 'Editar orden de compra': titulo, labels y datos precargados ---
    assert driver.find_element(By.ID, "modal-editar-orden-title").text == "Editar orden de compra"
    labels = [
        label.get_attribute("textContent").strip()
        for label in driver.find_elements(By.CSS_SELECTOR, "#form-editar-orden label.field > span")
    ]
    assert labels == ["ID Orden", "Empleado que registra *", "ID Proveedor", "Proveedor"]
    assert driver.find_element(By.ID, "editar-id-orden").get_attribute("value") == id_orden
    assert driver.find_element(By.ID, "editar-nombre-proveedor").get_attribute("value") == nombre_proveedor

    # El JS recarga los productos del proveedor (POST) -> feedback-modal encima
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # El empleado de la orden se selecciona con un setTimeout de 300 ms
    espera.until(lambda d: d.find_element(By.ID, "editar-id-empleado").get_attribute("value"))

    # Los productos precargados habilitan el boton de actualizacion
    espera.until(
        lambda d: d.find_element(
            By.CSS_SELECTOR, "#tabla-productos-seleccionados-editar .cantidad-valor"
        ).text
        == CANTIDAD_INICIAL
    )

    # --- Boton 'Actualizar orden': fondo amarillo con texto oscuro ---
    boton_actualizar = driver.find_element(By.ID, "btn-guardar-editar")
    assert boton_actualizar.text.strip() == "Actualizar orden"
    assert estilo_css(driver, boton_actualizar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Actualizar orden' deberia ser el amarillo primario"
    )
    assert estilo_css(driver, boton_actualizar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Actualizar orden' deberia ser oscuro"
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
    espera.until(lambda d: not boton_actualizar.get_attribute("disabled"))
    boton_actualizar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-editar-orden")))

    # --- Feedback global de exito con el mensaje propio del modulo ---
    espera.until(
        lambda d: d.find_element(By.ID, "feedback-modal-title").text.strip() == "Éxito"
    )
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo="Éxito", mensaje="Orden de compra actualizada exitosamente."
    )

    # ---- Verificacion del cambio en el detalle de la orden ----
    fila_orden = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, f"#tabla-ordenes-pendientes tr[data-id='{id_orden}']")
        )
    )
    fila_orden.find_element(By.CSS_SELECTOR, "button[data-action='ver']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-detalle-orden")))
    assert driver.find_element(By.ID, "modal-detalle-orden-title").text == "Detalle de orden"

    info_detalle = driver.find_element(By.ID, "detalle-orden-info")
    labels_detalle = [
        elemento.get_attribute("textContent").strip()
        for elemento in info_detalle.find_elements(By.CSS_SELECTOR, ".device-detail__label")
    ]
    assert labels_detalle == ["ID Orden", "Proveedor", "Fecha", "Estado", "Realizado por"]
    assert f"#{id_orden}" in info_detalle.text
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

    # --- Limpieza: anular la orden editada para dejar la BD como estaba ---
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
        f"Orden actualizada y anulada (limpieza): {id_orden} - {nombre_producto} "
        f"cantidad {CANTIDAD_INICIAL} -> {CANTIDAD_NUEVA} (feedback: {mensaje})"
    )
