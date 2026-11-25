import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import quitar_hover

from test_1_crear_orden_servicio import DATOS_CLIENTE, DATOS_ORDEN, crear_orden_servicio_ui

URL_ORDENES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/ordenes-servicio"
TIEMPO_ESPERA = 10

# ----------------------------------------------------------------------
# Prueba de interface: consultar el detalle de una orden de servicio
# desde /ordenes-servicio (modal "Detalle de orden" con orden + fotos +
# historial de revisiones).
# AUTOCONTENIDA: crea primero su propia orden temporal (flujo minimo) y
# luego abre el detalle de esa orden. El registro queda persistido en la
# BD (no se elimina al terminar; la pagina no ofrece eliminacion de
# ordenes).
# MECANISMO DE FEEDBACK: ordenes_servicio.js no muestra feedback propio
# (consola); el visible al crear es el del interceptor global de fetch.
# ----------------------------------------------------------------------


def test_consultar_orden_servicio(driver):
    # ---------------------------------------------------------------
    # PASO 1: crear la orden temporal sobre la que se va a consultar
    # ---------------------------------------------------------------
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    fila = crear_orden_servicio_ui(driver, espera)
    id_orden = fila.find_element(By.CSS_SELECTOR, "td.col-id").text.strip()

    # ---------------------------------------------------------------
    # PASO 2: abrir el detalle de la orden con el boton de la fila
    # ---------------------------------------------------------------
    fila.find_element(By.CSS_SELECTOR, "button[data-action='ver-detalle']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-detalle-orden")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-detalle-orden-title").text == "Detalle de orden"

    # El detalle se carga por API; se espera a que se dibuje la informacion
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#modal-order-info .detail-group")
        )
    )

    # --- Labels del detalle (textContent: el CSS los pinta en mayusculas) ---
    labels_detalle = [
        elemento.get_attribute("textContent").strip()
        for elemento in driver.find_elements(By.CSS_SELECTOR, "#modal-order-info .detail-label")
    ]
    assert labels_detalle == [
        "ID Orden", "Estado", "Cliente", "Equipo", "Modelo", "Costo", "Descripción del problema"
    ]

    # --- Verificar los datos del equipo y del cliente en el detalle ---
    info = driver.find_element(By.ID, "modal-order-info").text
    assert f"#{id_orden}" in info
    assert f"{DATOS_CLIENTE[1]} {DATOS_CLIENTE[2]}" in info
    assert DATOS_ORDEN[0] in info       # IMEI en el campo Equipo
    assert DATOS_ORDEN[1] in info       # modelo
    assert DATOS_ORDEN[5] in info       # descripcion del problema

    # --- Verificar que el historial de revisiones muestra el test #1 ---
    # (la creacion siempre registra la revision inicial)
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#modal-order-tests .tests-table-wrap")
        )
    )
    tests = driver.find_element(By.ID, "modal-order-tests").text
    assert "Test #1" in tests

    # --- Cerrar el modal de detalle con el boton "Cerrar" (ghost) ---
    boton_cerrar = driver.find_element(
        By.CSS_SELECTOR, "#modal-detalle-orden .ui-form__actions button[data-close-modal]"
    )
    assert boton_cerrar.text.strip() == "Cerrar"
    boton_cerrar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-detalle-orden")))

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Orden consultada: {id_orden} (IMEI {DATOS_ORDEN[0]}, test #1 visible en el historial)")
