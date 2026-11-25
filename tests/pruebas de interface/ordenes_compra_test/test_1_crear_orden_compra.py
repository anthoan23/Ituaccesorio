import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_ORDENES_COMPRA = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/ordenes_compra"
TIEMPO_ESPERA = 10

# Prueba autocontenida: crea su propia orden temporal (ID autogenerado tipo
# OC000000X) con el primer empleado disponible, el primer proveedor CON
# productos (via API, solo lectura; el primer proveedor de la lista puede no
# tener productos) y el primer producto de ese proveedor (cantidad 2).
# No depende del orden de ejecucion ni muta la semilla. La orden se anula al
# final para dejar la BD como estaba.
#
# NOTA DE LA APP: el modelo genera el ID con MAX(ID_orden_compra)
# lexicografico; con IDs de longitudes mezcladas (p. ej. la orden entregada
# "OC000901" de 8 caracteres) el MAX siempre cae en ella y el ID generado se
# repite -> el alta falla con "Error al agregar la orden de compra". La suite
# debe correr contra una BD recien sembrada (docker-compose down -v).

TITULO_PAGINA = "Ituaccesorio - Órdenes de compra"


def test_crear_orden_compra(driver):
    import json
    import urllib.request

    base = os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')

    def api_get(ruta):
        with urllib.request.urlopen(f"{base}{ruta}", timeout=5) as respuesta:
            return json.loads(respuesta.read())

    # Proveedor con productos (solo lectura): el primero de la lista puede no tenerlos
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

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == TITULO_PAGINA
    assert espera.until(
        lambda d: d.find_element(By.CSS_SELECTOR, ".hero__title").text
    ) == "Órdenes de compra"
    # textContent: el CSS renderiza el eyebrow en mayusculas
    assert driver.find_element(By.CSS_SELECTOR, ".hero__eyebrow").get_attribute("textContent").strip() == (
        "Gestión de compras"
    )
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Órdenes de compra"

    # Encabezados de la tabla de pendientes (textContent: el CSS los pinta en mayusculas)
    encabezados = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, "#vista-pendientes .table thead th")
    ]
    assert encabezados == ["ID orden", "Proveedor", "Fecha", "Estado", "Costo total", "Acciones"]

    # --- Boton hero 'Registrar orden': texto y estilo primario (amarillo plano) ---
    boton_registrar = driver.find_element(By.ID, "btn-registrar-entrada")
    assert boton_registrar.text.strip() == "Registrar orden"
    assert estilo_css(driver, boton_registrar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Registrar orden' deberia ser el amarillo primario"
    )
    assert estilo_css(driver, boton_registrar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Registrar orden' deberia ser oscuro"
    )

    # La tabla de pendientes termina de cargar (fetch inicial)
    espera.until(
        lambda d: "Cargando" not in d.find_element(By.ID, "tabla-ordenes-pendientes").text
    )
    ids_antes = {
        fila.get_attribute("data-id")
        for fila in driver.find_elements(By.CSS_SELECTOR, "#tabla-ordenes-pendientes tr[data-id]")
    }

    # --- Abrir el modal de registro (los empleados se cargan por fetch) ---
    boton_registrar.click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-registrar-entrada")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-registrar-entrada-title").text == "Registrar orden de compra"

    # Labels del formulario (textContent: el CSS pinta los labels en mayusculas)
    labels = [
        label.get_attribute("textContent").strip()
        for label in driver.find_elements(By.CSS_SELECTOR, "#form-registrar-entrada label.field > span")
    ]
    assert labels == ["Empleado que registra *", "ID Proveedor", "Proveedor"]
    assert driver.find_element(
        By.CSS_SELECTOR, "#form-registrar-entrada .field--full > span"
    ).get_attribute("textContent").strip() == "Productos seleccionados"

    # Botones ghost del modal
    boton_buscar_proveedor = driver.find_element(By.ID, "btn-desplegar-proveedores")
    assert boton_buscar_proveedor.text.strip() == "Buscar proveedor"
    assert estilo_css(driver, boton_buscar_proveedor, "backgroundColor") == "rgba(255, 255, 255, 0.06)", (
        "El fondo de 'Buscar proveedor' deberia ser el ghost del tema oscuro"
    )
    boton_buscar_productos = driver.find_element(By.ID, "btn-desplegar-productos")
    assert boton_buscar_productos.text.strip() == "Agregar productos"
    assert boton_buscar_productos.get_attribute("disabled"), "Agregar productos debe llegar deshabilitado"

    espera.until(
        lambda d: len(Select(d.find_element(By.ID, "entrada-id-empleado")).options) > 1
    )
    Select(driver.find_element(By.ID, "entrada-id-empleado")).select_by_index(1)

    # --- Modal 'Seleccionar proveedor' ---
    boton_buscar_proveedor.click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-seleccionar-proveedor")))
    assert driver.find_element(By.ID, "modal-seleccionar-proveedor-title").text == "Seleccionar proveedor"
    encabezados_proveedores = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, "#modal-seleccionar-proveedor .table thead th")
    ]
    assert encabezados_proveedores == ["ID", "Nombre", "Teléfono", "Correo"]

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

    # Cargar los productos del proveedor es un POST: el interceptor global de
    # fetch abre el feedback-modal encima de los demas modales; se espera su
    # autocierre antes de volver a interactuar.
    espera.until(EC.visibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Modal 'Seleccionar productos' ---
    boton_buscar_productos = driver.find_element(By.ID, "btn-desplegar-productos")
    espera.until(lambda d: not boton_buscar_productos.get_attribute("disabled"))
    boton_buscar_productos.click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-seleccionar-productos")))
    assert driver.find_element(By.ID, "modal-seleccionar-productos-title").text == "Seleccionar productos"
    encabezados_productos = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, "#modal-seleccionar-productos .table thead th")
    ]
    assert encabezados_productos == ["Clase", "Marca", "Producto", "Costo"]

    fila_producto = espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#lista-productos tr[data-producto-id]"))
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
    assert boton_guardar.text.strip() == "Registrar orden"
    espera.until(lambda d: not boton_guardar.get_attribute("disabled"))
    boton_guardar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-registrar-entrada")))

    # --- Feedback global de exito: el JS muestra FeedbackModal con titulo
    # 'Éxito' y el mensaje propio del modulo (el interceptor global abre el
    # mismo modal un instante antes; se espera el titulo final del modulo) ---
    espera.until(
        lambda d: d.find_element(By.ID, "feedback-modal-title").text.strip() == "Éxito"
    )
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo="Éxito", mensaje="Orden de compra registrada exitosamente."
    )

    # --- La orden creada aparece en pendientes (la mas reciente es la primera) ---
    def fila_nueva(d):
        for fila in d.find_elements(By.CSS_SELECTOR, "#tabla-ordenes-pendientes tr[data-id]"):
            if fila.get_attribute("data-id") not in ids_antes:
                return fila
        return False

    fila_orden = espera.until(fila_nueva)
    id_orden = fila_orden.get_attribute("data-id")
    assert nombre_proveedor in fila_orden.text
    assert "Pendiente" in fila_orden.text

    # --- Limpieza: anular la orden creada para dejar la BD como estaba ---
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
        f"Orden de compra creada y anulada (limpieza): {id_orden} "
        f"(proveedor: {nombre_proveedor}, producto: {nombre_producto}, cantidad 2; feedback: {mensaje})"
    )
