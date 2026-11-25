import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_ORDENES_COMPRA = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/ordenes_compra"
TIEMPO_ESPERA = 10

# Prueba autocontenida: crea por la UI su propia orden temporal (ID
# autogenerado tipo OC000000X, primer empleado + primer proveedor CON
# productos + primer producto, cantidad 2) y despues la anula desde su fila en
# pendientes. El boton "eliminar" de la tabla dispara el modal de confirmacion
# (con el ID de la orden en el texto) y llama a /api/ordenes_compra/anular,
# que deja la orden con Estado = 'Anulada' y la saca de pendientes.
# No depende del orden de ejecucion ni muta la semilla.
#
# NOTA DE LA APP: el modelo genera el ID con MAX(ID_orden_compra)
# lexicografico; con IDs de longitudes mezcladas (p. ej. "OC000901") el alta
# falla -> la suite debe correr contra una BD recien sembrada.

TITULO_PAGINA = "Ituaccesorio - Órdenes de compra"


def test_anular_orden_compra(driver):
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

    # ---- Anulacion desde el boton "eliminar" de la fila ----
    fila_orden = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, f"#tabla-ordenes-pendientes tr[data-id='{id_orden}']")
        )
    )
    fila_orden.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-confirmar-eliminar-orden")))
    quitar_hover(driver)

    # --- Modal de confirmacion: titulo, texto dinamico con el ID y botones ---
    assert driver.find_element(By.ID, "modal-confirmar-eliminar-orden-title").text == "Confirmar eliminación"
    texto_confirmacion = driver.find_element(By.ID, "texto-confirmar-eliminar-orden").get_attribute("textContent")
    assert texto_confirmacion == (
        f'¿Seguro que deseas eliminar (anular) la orden "{id_orden}"? '
        f'Esta acción no se puede deshacer.'
    ), f"El texto de confirmacion no menciona la orden: '{texto_confirmacion}'"

    boton_confirmar = driver.find_element(By.ID, "btn-confirmar-eliminar-orden")
    assert boton_confirmar.text.strip() == "Eliminar"
    assert "ui-btn--danger" in boton_confirmar.get_attribute("class")
    assert estilo_css(driver, boton_confirmar, "borderTopColor") == "rgba(220, 38, 38, 0.3)", (
        "El borde de 'Eliminar' deberia ser el rojo translucido del tema"
    )
    assert estilo_css(driver, boton_confirmar, "color") == "rgb(239, 68, 68)", (
        "El texto de 'Eliminar' deberia ser el rojo de peligro"
    )

    boton_cancelar = driver.find_element(
        By.CSS_SELECTOR, "#modal-confirmar-eliminar-orden .ui-form__actions [data-close-modal]"
    )
    assert boton_cancelar.text.strip() == "Cancelar"
    assert "ui-btn--ghost" in boton_cancelar.get_attribute("class")
    assert estilo_css(driver, boton_cancelar, "backgroundColor") == "rgba(255, 255, 255, 0.06)", (
        "El fondo de 'Cancelar' deberia ser el ghost del tema oscuro"
    )
    assert estilo_css(driver, boton_cancelar, "color") == "rgb(255, 255, 255)", (
        "El texto de 'Cancelar' deberia ser blanco"
    )

    boton_confirmar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-confirmar-eliminar-orden")))

    # --- Feedback global de exito con el mensaje propio del modulo ---
    espera.until(
        lambda d: d.find_element(By.ID, "feedback-modal-title").text.strip() == "Éxito"
    )
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo="Éxito", mensaje="Orden eliminada exitosamente."
    )

    # La orden anulada desaparece de la tabla de pendientes
    espera.until(
        EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, f"#tabla-ordenes-pendientes tr[data-id='{id_orden}']")
        )
    )
    print(f"Orden de compra anulada: {id_orden} (proveedor: {nombre_proveedor}; feedback: {mensaje})")
