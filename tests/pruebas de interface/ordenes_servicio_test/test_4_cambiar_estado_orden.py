import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from helpers import esperar_feedback

from test_1_crear_orden_servicio import crear_orden_servicio_ui

URL_ORDENES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/ordenes-servicio"
TIEMPO_ESPERA = 10

# ----------------------------------------------------------------------
# Prueba de interface: cambiar el estado de una orden de servicio desde
# /ordenes-servicio.
# NOTA DE FLUJO: esta pagina no tiene un selector de estado propio; el
# unico cambio de estado que la UI admite sobre una orden nueva es
# "Pendiente" -> "Asignada" (modal "Asignar orden a tecnico", boton
# "Asignar" del encabezado de la tabla). El estado "En proceso" solo se
# alcanza desde el modulo Taller y esas ordenes se ocultan de esta tabla
# (el JS renderTablaOrdenes las filtra), por eso se verifica "Asignada".
# AUTOCONTENIDA: crea su propia orden temporal y luego cambia su estado
# seleccionandola manualmente en el modal. El registro queda persistido
# en la BD (no se elimina al terminar; la pagina no ofrece eliminacion
# de ordenes).
# MECANISMO DE FEEDBACK: ordenes_servicio.js no muestra feedback propio
# (consola); el visible es el del interceptor global de fetch.
# ----------------------------------------------------------------------


def test_cambiar_estado_orden(driver):
    # ---------------------------------------------------------------
    # PASO 1: crear la orden temporal pendiente
    # ---------------------------------------------------------------
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    fila = crear_orden_servicio_ui(driver, espera)
    id_orden = fila.find_element(By.CSS_SELECTOR, "td.col-id").text.strip()
    badge_inicial = fila.find_element(By.CSS_SELECTOR, "td.col-estado .badge")
    # textContent: el CSS pinta el badge en mayusculas
    estado_inicial = badge_inicial.get_attribute("textContent").strip()
    assert estado_inicial == "Pendiente"

    # ---------------------------------------------------------------
    # PASO 2: cambiar el estado desde el modal de asignacion del
    # encabezado (se abre sin fila preseleccionada)
    # ---------------------------------------------------------------
    driver.find_element(By.ID, "btn-asignar-tecnico").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-asignar-tecnico")))

    # Seleccionar la orden recien creada por su ID y el primer tecnico
    espera.until(
        lambda d: len(Select(d.find_element(By.ID, "select-orden-asignar")).options) > 1
    )
    Select(driver.find_element(By.ID, "select-orden-asignar")).select_by_value(id_orden)
    espera.until(lambda d: len(Select(d.find_element(By.ID, "modal-tecnico-select")).options) > 1)
    Select(driver.find_element(By.ID, "modal-tecnico-select")).select_by_index(1)

    driver.find_element(By.ID, "btn-asignar-orden").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-asignar-tecnico")))

    # --- Feedback visible: el del interceptor global (el JS del modulo va a consola) ---
    espera.until(
        lambda d: d.find_element(By.ID, "feedback-modal-title").text.strip() == "Acción exitosa"
    )
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo="Acción exitosa", mensaje="Registro realizado satisfactoriamente."
    )

    # --- Verificar el nuevo estado en la tabla ---
    fila_cambiada = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//tbody[@id='tabla-ordenes']//tr[td[1][normalize-space(.)='{id_orden}']]",
            )
        )
    )
    badge_final = fila_cambiada.find_element(By.CSS_SELECTOR, "td.col-estado .badge")
    estado_final = badge_final.get_attribute("textContent").strip()
    assert estado_final == "Asignada"
    assert "badge--asignada" in badge_final.get_attribute("class")

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Estado cambiado en {id_orden}: {estado_inicial} -> {estado_final} "
        f"(feedback del interceptor: {mensaje})"
    )
