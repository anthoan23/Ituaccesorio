import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, esperar_feedback, quitar_hover

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
# despues la elimina desde el boton "eliminar" del historial (modal de
# confirmacion con el ID de la entrega en el texto). La eliminacion revierte
# el stock y devuelve la orden a Pendiente. No depende del orden de ejecucion
# ni muta la semilla. Al final anula la orden para dejar la BD como estaba.
#
# MECANISMO DE FEEDBACK: FeedbackModal global con titulo 'Éxito' (el JS del
# modulo pisa el mensaje generico del interceptor de fetch).


def test_eliminar_orden_entrega(driver):
    # ---- Paso 1: crear la orden de compra pendiente por la UI ----
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    id_orden, nombre_proveedor, _ = crear_orden_compra_ui(driver, espera)

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
    seleccionar_empleado_receptor(driver, espera)
    driver.find_element(By.ID, "btn-confirmar-entrega").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-registrar-entrega")))
    esperar_feedback(
        espera, tipo="success", titulo="Éxito", mensaje="Entrega registrada exitosamente. Stock actualizado."
    )

    # ---- Paso 3: eliminar la entrega desde el historial ----
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
    boton_eliminar = fila_historial.find_element(
        By.CSS_SELECTOR, "button[data-action='eliminar-entrega']"
    )
    id_entrega = boton_eliminar.get_attribute("data-id")
    boton_eliminar.click()

    # --- Modal de confirmacion: titulo, texto dinamico y botones ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-confirmar-eliminar-entrega")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-confirmar-eliminar-entrega-title").text == "Confirmar eliminación"
    texto_confirmacion = driver.find_element(By.ID, "texto-confirmar-eliminar-entrega").get_attribute("textContent")
    assert texto_confirmacion == (
        f'¿Seguro que deseas eliminar la entrega "{id_entrega}"? '
        f'Se revertirá el stock de los productos. Esta acción no se puede deshacer.'
    ), f"El texto de confirmacion no menciona la entrega: '{texto_confirmacion}'"

    boton_confirmar = driver.find_element(By.ID, "btn-confirmar-eliminar-entrega")
    assert boton_confirmar.text.strip() == "Eliminar"
    assert "ui-btn--danger" in boton_confirmar.get_attribute("class")
    assert estilo_css(driver, boton_confirmar, "borderTopColor") == "rgba(220, 38, 38, 0.3)", (
        "El borde de 'Eliminar' deberia ser el rojo translucido del tema"
    )
    assert estilo_css(driver, boton_confirmar, "color") == "rgb(239, 68, 68)", (
        "El texto de 'Eliminar' deberia ser el rojo de peligro"
    )

    boton_cancelar = driver.find_element(
        By.CSS_SELECTOR, "#modal-confirmar-eliminar-entrega .ui-form__actions [data-close-modal]"
    )
    assert boton_cancelar.text.strip() == "Cancelar"
    assert "ui-btn--ghost" in boton_cancelar.get_attribute("class")
    assert estilo_css(driver, boton_cancelar, "backgroundColor") == "rgba(255, 255, 255, 0.06)", (
        "El fondo de 'Cancelar' deberia ser el ghost del tema oscuro"
    )

    boton_confirmar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-confirmar-eliminar-entrega")))

    # --- Feedback global de exito con el mensaje propio del modulo ---
    espera.until(
        lambda d: d.find_element(By.ID, "feedback-modal-title").text.strip() == "Éxito"
    )
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo="Éxito", mensaje="Entrega eliminada exitosamente. Stock revertido."
    )

    # La entrega eliminada desaparece del historial
    espera.until(
        EC.invisibility_of_element_located(
            (
                By.XPATH,
                "//*[@id='tabla-ordenes-entregas-historial']"
                f"//tr[td[2][normalize-space(.)='{id_orden}']]",
            )
        )
    )

    # ---- Limpieza: anular la orden que volvio a Pendiente ----
    anular_orden_compra_ui(driver, espera, id_orden)
    print(
        f"Entrega eliminada y orden anulada (limpieza): {id_entrega} de la orden {id_orden} "
        f"(proveedor: {nombre_proveedor}); stock revertido; feedback: {mensaje}"
    )
