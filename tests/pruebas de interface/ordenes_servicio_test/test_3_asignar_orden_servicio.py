import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from helpers import estilo_css, esperar_feedback, quitar_hover

from test_1_crear_orden_servicio import crear_orden_servicio_ui

URL_ORDENES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/ordenes-servicio"
TIEMPO_ESPERA = 10

# ----------------------------------------------------------------------
# Prueba de interface: asignar una orden de servicio a un tecnico
# desde /ordenes-servicio (boton "Asignar" de la fila + modal
# "Asignar orden a tecnico").
# AUTOCONTENIDA: crea primero su propia orden temporal (flujo minimo) y
# luego la asigna usando el boton de asignacion de su fila. El registro
# queda persistido en la BD (no se elimina al terminar; la pagina no
# ofrece eliminacion de ordenes).
# MECANISMO DE FEEDBACK: ordenes_servicio.js no muestra feedback propio
# (consola); el visible es el del interceptor global de fetch.
# Requisitos: ENTORNO_PRUEBA=true (decoradores desactivados), BD sembrada
# con modelos de telefono y con al menos un tecnico registrado
# (el select #modal-tecnico-select se llena por API).
# ----------------------------------------------------------------------


def test_asignar_orden_servicio(driver):
    # ---------------------------------------------------------------
    # PASO 1: crear la orden temporal pendiente que se va a asignar
    # ---------------------------------------------------------------
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    fila = crear_orden_servicio_ui(driver, espera)
    id_orden = fila.find_element(By.CSS_SELECTOR, "td.col-id").text.strip()

    # ---------------------------------------------------------------
    # PASO 2: asignar la orden con el boton "Asignar tecnico" de la fila
    # (el JS preselecciona esa orden en el modal)
    # ---------------------------------------------------------------
    fila.find_element(By.CSS_SELECTOR, "button[data-action='seleccionar-asignacion']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-asignar-tecnico")))
    quitar_hover(driver)

    # --- Modal 'Asignar orden a tecnico': titulo, labels y botones ---
    assert driver.find_element(By.ID, "modal-asignar-tecnico-title").text == "Asignar orden a técnico"
    labels = [
        label.get_attribute("textContent").strip()
        for label in driver.find_elements(By.CSS_SELECTOR, "#form-asignar-tecnico label.field > span")
    ]
    assert labels == ["Orden pendiente", "Técnico"]

    # La orden pulsada debe venir preseleccionada en el modal
    assert driver.find_element(By.ID, "select-orden-asignar").get_attribute("value") == id_orden

    # --- Botones: 'Cancelar' ghost y 'Asignar' primario ---
    boton_cancelar = driver.find_element(By.CSS_SELECTOR, "#form-asignar-tecnico [data-close-modal]")
    assert boton_cancelar.text.strip() == "Cancelar"
    assert "ui-btn--ghost" in boton_cancelar.get_attribute("class")
    assert estilo_css(driver, boton_cancelar, "backgroundColor") == "rgba(255, 255, 255, 0.06)", (
        "El fondo de 'Cancelar' deberia ser el ghost del tema oscuro"
    )
    boton_asignar = driver.find_element(By.ID, "btn-asignar-orden")
    assert boton_asignar.text.strip() == "Asignar"
    assert estilo_css(driver, boton_asignar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Asignar' deberia ser el amarillo primario"
    )
    assert estilo_css(driver, boton_asignar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Asignar' deberia ser oscuro"
    )

    # Esperar a que el select de tecnicos se llene por API y elegir el primero
    espera.until(lambda d: len(Select(d.find_element(By.ID, "modal-tecnico-select")).options) > 1)
    Select(driver.find_element(By.ID, "modal-tecnico-select")).select_by_index(1)

    boton_asignar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-asignar-tecnico")))

    # --- Feedback visible: el del interceptor global (el JS del modulo va a consola) ---
    espera.until(
        lambda d: d.find_element(By.ID, "feedback-modal-title").text.strip() == "Acción exitosa"
    )
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo="Acción exitosa", mensaje="Registro realizado satisfactoriamente."
    )

    # --- Verificar el cambio de estado visible en la tabla ---
    fila_asignada = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//tbody[@id='tabla-ordenes']//tr[td[1][normalize-space(.)='{id_orden}']]",
            )
        )
    )
    badge_estado = fila_asignada.find_element(By.CSS_SELECTOR, "td.col-estado .badge")
    # textContent: el CSS pinta el badge en mayusculas
    assert badge_estado.get_attribute("textContent").strip() == "Asignada"
    assert "badge--asignada" in badge_estado.get_attribute("class")

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Orden asignada: {id_orden} -> estado "
        f"'{badge_estado.get_attribute('textContent').strip()}' en la tabla (feedback del interceptor: {mensaje})"
    )
