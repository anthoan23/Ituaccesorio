import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import esperar_feedback, quitar_hover

from test_1_registrar_orden_entrega import (
    TITULO_ENTREGAS,
    anular_orden_compra_ui,
    crear_orden_compra_ui,
    seleccionar_empleado_receptor,
)

URL_ORDENES_ENTREGAS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/ordenes_entregas"
TIEMPO_ESPERA = 10

# Prueba autocontenida: crea por la UI su propia orden temporal (ID
# autogenerado tipo OC000000X), registra su entrega en /ordenes_entregas y
# despues consulta el detalle desde el boton "ver" del historial (consulta
# /api/detalles_orden/<id_orden>). No depende del orden de ejecucion ni muta
# la semilla. Al final elimina la entrega y anula la orden para dejar la BD
# como estaba.
#
# MECANISMO DE FEEDBACK: FeedbackModal global con titulo 'Éxito' (el JS del
# modulo pisa el mensaje generico del interceptor de fetch).


def test_consultar_orden_entrega(driver):
    # ---- Paso 1: crear la orden de compra pendiente por la UI ----
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    id_orden, nombre_proveedor, nombre_producto = crear_orden_compra_ui(driver, espera)

    # ---- Paso 2: registrar la entrega de esa orden ----
    driver.get(URL_ORDENES_ENTREGAS)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    assert driver.title == TITULO_ENTREGAS
    boton_entrega = espera.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "#tabla-ordenes-entregas-pendientes "
                f"button[data-action='registrar-entrega'][data-id='{id_orden}']",
            )
        )
    )
    boton_entrega.click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-registrar-entrega")))
    espera.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#entrega-productos-preview table"))
    )
    recibido_por = seleccionar_empleado_receptor(driver, espera)
    driver.find_element(By.ID, "btn-confirmar-entrega").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-registrar-entrega")))
    esperar_feedback(
        espera, tipo="success", titulo="Éxito", mensaje="Entrega registrada exitosamente. Stock actualizado."
    )

    # ---- Paso 3: consultar la entrega en el historial ----
    driver.find_element(By.ID, "btn-entregadas").click()
    espera.until(
        lambda d: "Cargando" not in d.find_element(By.ID, "tabla-ordenes-entregas-historial").text
    )
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
    assert recibido_mostrado == recibido_por

    # --- Detalle de la orden desde el icono "ver" del historial ---
    fila_historial.find_element(By.CSS_SELECTOR, "button[data-action='ver-historial']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-detalle-orden")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-detalle-orden-title").text == "Detalle de orden"

    info_detalle = driver.find_element(By.ID, "detalle-orden-info")
    labels_detalle = [
        elemento.get_attribute("textContent").strip()
        for elemento in info_detalle.find_elements(By.CSS_SELECTOR, ".device-detail__label")
    ]
    assert labels_detalle == ["ID Orden", "Proveedor", "Fecha", "Estado", "Realizado por"]
    assert f"#{id_orden}" in info_detalle.text
    assert nombre_proveedor in info_detalle.text

    encabezados_detalle = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, "#modal-detalle-orden .table thead th")
    ]
    assert encabezados_detalle == ["Marca", "Producto", "Cantidad", "Costo", "Subtotal"]
    productos_detalle = driver.find_element(By.ID, "detalle-orden-productos").text
    assert nombre_producto in productos_detalle

    # Cerrar el modal de detalle
    driver.find_element(
        By.CSS_SELECTOR, "#modal-detalle-orden button[data-close-modal]"
    ).click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-detalle-orden")))

    # ---- Limpieza: eliminar la entrega (la orden vuelve a Pendiente) y anularla ----
    fila_historial = driver.find_element(
        By.XPATH,
        "//*[@id='tabla-ordenes-entregas-historial']"
        f"//tr[td[2][normalize-space(.)='{id_orden}']]",
    )
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
        f"Entrega consultada y limpiada: orden {id_orden} (proveedor: {nombre_proveedor}, "
        f"producto: {nombre_producto}, recibida por {recibido_por})"
    )
