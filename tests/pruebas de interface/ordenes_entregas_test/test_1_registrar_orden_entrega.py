import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_ORDENES_COMPRA = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/ordenes_compra"
URL_ORDENES_ENTREGAS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/ordenes_entregas"
TIEMPO_ESPERA = 10

# [recibido_por]
RECIBIDO_POR = "Empleado Receptor"

# Prueba autocontenida: crea por la UI una orden de compra pendiente (ID
# autogenerado tipo OC000000X, primer empleado + primer proveedor CON
# productos + primer producto) en /ordenes_compra y despues registra su
# entrega en /ordenes_entregas. No depende del orden de ejecucion ni muta la
# semilla. Al final elimina la entrega y anula la orden para dejar la BD como
# estaba.
#
# NOTA DE LA APP: el modelo genera el ID con MAX(ID_orden_compra)
# lexicografico; con IDs de longitudes mezcladas (p. ej. "OC000901") el alta
# falla -> la suite debe correr contra una BD recien sembrada.
#
# MECANISMO DE FEEDBACK: FeedbackModal global con titulo 'Éxito' (el JS del
# modulo pisa el mensaje generico del interceptor de fetch).

TITULO_ENTREGAS = "Ituaccesorio - Órdenes de Entregas / Recepción"


def crear_orden_compra_ui(driver, espera):
    """Crea una orden de compra pendiente por la UI y devuelve
    (id_orden, nombre_proveedor, nombre_producto)."""
    import json
    import urllib.request

    base = os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')

    def api_get(ruta):
        with urllib.request.urlopen(f"{base}{ruta}", timeout=5) as respuesta:
            return json.loads(respuesta.read())

    # Proveedor con productos (solo lectura): el primero de la lista puede no tenerlos
    proveedor = None
    for candidato in api_get("/api/proveedores")["proveedores"]:
        productos = api_get(f"/api/productos_proveedor/{candidato['id']}").get("productos", [])
        if productos:
            proveedor = candidato
            break
    assert proveedor, "No hay proveedores con productos en la BD"

    driver.get(URL_ORDENES_COMPRA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
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
            (By.CSS_SELECTOR, f"#lista-proveedores tr[data-proveedor-id='{proveedor['id']}']")
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
    return id_orden, nombre_proveedor, nombre_producto


def anular_orden_compra_ui(driver, espera, id_orden):
    """Anula por la UI la orden creada (limpieza final)."""
    driver.get(URL_ORDENES_COMPRA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, f"#tabla-ordenes-pendientes tr[data-id='{id_orden}']")
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-confirmar-eliminar-orden")))
    driver.find_element(By.ID, "btn-confirmar-eliminar-orden").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-confirmar-eliminar-orden")))
    esperar_feedback(espera, tipo="success", titulo="Éxito", mensaje="Orden eliminada exitosamente.")
    espera.until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, f"#tabla-ordenes-pendientes tr[data-id='{id_orden}']"))
    )


def test_registrar_orden_entrega(driver):
    # ---- Paso 1: crear la orden de compra pendiente por la UI ----
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    id_orden, nombre_proveedor, nombre_producto = crear_orden_compra_ui(driver, espera)

    # ---- Paso 2: la pagina de recepcion de entregas ----
    driver.get(URL_ORDENES_ENTREGAS)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == TITULO_ENTREGAS
    assert espera.until(
        lambda d: d.find_element(By.CSS_SELECTOR, ".hero__title").text
    ) == "Órdenes de Entregas de Proveedores"
    # textContent: el CSS renderiza el eyebrow en mayusculas
    assert driver.find_element(By.CSS_SELECTOR, ".hero__eyebrow").get_attribute("textContent").strip() == (
        "Gestión de recepción"
    )
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Órdenes de Entregas"

    # Boton hero 'Actualizar' con estilo ghost
    boton_actualizar = driver.find_element(By.ID, "btn-actualizar")
    assert boton_actualizar.text.strip() == "Actualizar"
    assert estilo_css(driver, boton_actualizar, "backgroundColor") == "rgba(255, 255, 255, 0.06)", (
        "El fondo de 'Actualizar' deberia ser el ghost del tema oscuro"
    )

    # Conmutador de vistas: pendientes activa por defecto
    assert driver.find_element(By.ID, "btn-pendientes").text.strip() == "Pendientes de entrega"
    assert driver.find_element(By.ID, "btn-entregadas").text.strip() == "Historial de entregas"
    assert "is-active" in driver.find_element(By.ID, "btn-pendientes").get_attribute("class")

    encabezados = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, "#vista-pendientes .table thead th")
    ]
    assert encabezados == ["ID orden", "Proveedor", "Fecha", "Hora", "Estado", "Costo total", "Acciones"]

    # --- Fila de la orden: iconos ver (azul), editar (amarillo) y registrar entrega (verde) ---
    boton_entrega = espera.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "#tabla-ordenes-entregas-pendientes "
                f"button[data-action='registrar-entrega'][data-id='{id_orden}']",
            )
        )
    )
    fila = boton_entrega.find_element(By.XPATH, "./ancestor::tr")
    botones_fila = {
        accion: fila.find_element(By.CSS_SELECTOR, f"button[data-action='{accion}']")
        for accion in ("ver", "editar", "registrar-entrega")
    }
    quitar_hover(driver)
    assert estilo_css(driver, botones_fila["ver"], "borderTopColor") == "rgb(0, 122, 255)", (
        "El icono 'ver' de la fila deberia ser azul"
    )
    assert estilo_css(driver, botones_fila["editar"], "borderTopColor") == "rgb(243, 197, 0)", (
        "El icono 'editar' de la fila deberia ser amarillo"
    )
    assert estilo_css(driver, botones_fila["registrar-entrega"], "borderTopColor") == "rgb(34, 197, 94)", (
        "El icono 'registrar entrega' de la fila deberia ser verde"
    )

    # --- Modal 'Registrar entrega' ---
    boton_entrega.click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-registrar-entrega")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-registrar-entrega-title").text == "Registrar entrega"
    labels = [
        label.get_attribute("textContent").strip()
        for label in driver.find_elements(By.CSS_SELECTOR, "#form-registrar-entrega label.field > span")
    ]
    assert labels == ["Recibido por *", "Fecha de entrega *"]

    # La vista previa de productos se llena por fetch
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#entrega-productos-preview table")))
    assert driver.find_element(
        By.CSS_SELECTOR, "#entrega-productos-preview .entrega-preview-header"
    ).get_attribute("textContent").strip() == "Productos a recibir"
    encabezados_preview = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, "#entrega-productos-preview thead th")
    ]
    assert encabezados_preview == ["Producto", "Cantidad", "Costo unitario", "Subtotal"]

    boton_confirmar = driver.find_element(By.ID, "btn-confirmar-entrega")
    assert boton_confirmar.text.strip() == "Registrar entrega"
    assert estilo_css(driver, boton_confirmar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Registrar entrega' deberia ser el amarillo primario"
    )
    assert estilo_css(driver, boton_confirmar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Registrar entrega' deberia ser oscuro"
    )

    campo_recibido = driver.find_element(By.ID, "entrega-recibido-por")
    campo_recibido.clear()
    campo_recibido.send_keys(RECIBIDO_POR)
    # La fecha ya viene precargada con el dia actual; se confirma tal cual
    boton_confirmar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-registrar-entrega")))

    # --- Feedback global de exito con el mensaje propio del modulo ---
    espera.until(
        lambda d: d.find_element(By.ID, "feedback-modal-title").text.strip() == "Éxito"
    )
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo="Éxito", mensaje="Entrega registrada exitosamente. Stock actualizado."
    )

    # ---- Paso 3: la entrega pasa al historial de entregas ----
    driver.find_element(By.ID, "btn-entregadas").click()
    assert "is-active" in driver.find_element(By.ID, "btn-entregadas").get_attribute("class")
    assert "is-hidden" in driver.find_element(By.ID, "vista-pendientes").get_attribute("class")
    espera.until(
        lambda d: "Cargando" not in d.find_element(By.ID, "tabla-ordenes-entregas-historial").text
    )
    encabezados_historial = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, "#vista-entregadas .table thead th")
    ]
    assert encabezados_historial == [
        "ID entrega", "ID orden", "Proveedor", "Fecha entrega", "Hora", "Recibido por", "Acciones"
    ]
    fila_historial = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//*[@id='tabla-ordenes-entregas-historial']"
                f"//tr[td[2][normalize-space(.)='{id_orden}']]",
            )
        )
    )
    recibido_mostrado = fila_historial.find_element(By.CSS_SELECTOR, "td:nth-child(6)").text
    assert recibido_mostrado == RECIBIDO_POR

    # Iconos del historial: ver (azul), editar (amarillo), eliminar (rojo)
    quitar_hover(driver)
    assert estilo_css(
        driver, fila_historial.find_element(By.CSS_SELECTOR, "button[data-action='ver-historial']"), "borderTopColor"
    ) == "rgb(0, 122, 255)", "El icono 'ver' del historial deberia ser azul"
    assert estilo_css(
        driver, fila_historial.find_element(By.CSS_SELECTOR, "button[data-action='editar-entrega']"), "borderTopColor"
    ) == "rgb(243, 197, 0)", "El icono 'editar' del historial deberia ser amarillo"
    assert estilo_css(
        driver, fila_historial.find_element(By.CSS_SELECTOR, "button[data-action='eliminar-entrega']"), "borderTopColor"
    ) == "rgb(220, 38, 38)", "El icono 'eliminar' del historial deberia ser rojo"

    # ---- Limpieza: eliminar la entrega (la orden vuelve a Pendiente) y anularla ----
    fila_historial.find_element(By.CSS_SELECTOR, "button[data-action='eliminar-entrega']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-confirmar-eliminar-entrega")))
    driver.find_element(By.ID, "btn-confirmar-eliminar-entrega").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-confirmar-eliminar-entrega")))
    esperar_feedback(espera, tipo="success", titulo="Éxito", mensaje="Entrega eliminada exitosamente. Stock revertido.")
    espera.until(
        EC.invisibility_of_element_located(
            (By.XPATH, "//*[@id='tabla-ordenes-entregas-historial']//tr[td[2][normalize-space(.)='" + id_orden + "']]")
        )
    )
    anular_orden_compra_ui(driver, espera, id_orden)
    print(
        f"Entrega registrada y limpiada: orden {id_orden} (proveedor: {nombre_proveedor}, "
        f"producto: {nombre_producto}) recibida por {RECIBIDO_POR}; feedback: {mensaje}"
    )
