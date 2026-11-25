import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, esperar_feedback, quitar_hover

from test_1_registrar_orden_entrega import (
    RECIBIDO_POR,
    TITULO_ENTREGAS,
    anular_orden_compra_ui,
    crear_orden_compra_ui,
)

URL_ORDENES_ENTREGAS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/ordenes_entregas"
TIEMPO_ESPERA = 10

# [recibido_inicial, recibido_editado]
RECIBIDO_EDITADO = "Empleado Receptor Editado"

# Prueba autocontenida: crea por la UI su propia orden temporal (ID
# autogenerado tipo OC000000X), registra su entrega en /ordenes_entregas y
# despues la edita desde el boton "editar" del historial (modal de edicion).
# El campo "Recibido por" tiene maxlength=20: el navegador recorta el texto
# tecleado, por eso el valor esperado se lee del propio input.
# No depende del orden de ejecucion ni muta la semilla. Al final elimina la
# entrega y anula la orden para dejar la BD como estaba.
#
# HALLAZGO DE LA APP: el boton "editar" de la tabla de pendientes NO abre un
# modal, muestra el aviso "Para editar la orden ve a la seccion de Ordenes de
# Compra" (FeedbackModal de exito); la edicion real vive en el historial.
#
# MECANISMO DE FEEDBACK: FeedbackModal global con titulo 'Éxito' (el JS del
# modulo pisa el mensaje generico del interceptor de fetch).


def test_editar_orden_entrega(driver):
    # ---- Paso 1: crear la orden de compra pendiente por la UI ----
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    id_orden, nombre_proveedor, _ = crear_orden_compra_ui(driver, espera)

    # ---- Paso 2: la pagina de recepcion de entregas ----
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
    fila = boton_entrega.find_element(By.XPATH, "./ancestor::tr")

    # --- El icono "editar" de pendientes avisa (no edita aqui) ---
    fila.find_element(By.CSS_SELECTOR, "button[data-action='editar']").click()
    espera.until(
        lambda d: d.find_element(By.ID, "feedback-modal-title").text.strip() == "Éxito"
    )
    _, mensaje_aviso = esperar_feedback(
        espera,
        tipo="success",
        titulo="Éxito",
        mensaje="Para editar la orden ve a la sección de Órdenes de Compra",
    )

    # --- Registrar la entrega de la orden ---
    boton_entrega.click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-registrar-entrega")))
    espera.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#entrega-productos-preview table"))
    )
    campo_recibido = driver.find_element(By.ID, "entrega-recibido-por")
    campo_recibido.clear()
    campo_recibido.send_keys(RECIBIDO_POR)
    driver.find_element(By.ID, "btn-confirmar-entrega").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-registrar-entrega")))
    esperar_feedback(
        espera, tipo="success", titulo="Éxito", mensaje="Entrega registrada exitosamente. Stock actualizado."
    )

    # ---- Paso 3: editar la entrega desde el historial ----
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

    # El formulario de edicion se precarga por fetch (GET, sin feedback-modal)
    fila_historial.find_element(By.CSS_SELECTOR, "button[data-action='editar-entrega']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-editar-entrega")))
    quitar_hover(driver)

    # --- Modal 'Editar entrega': titulo dinamico, labels y datos precargados ---
    assert driver.find_element(By.ID, "modal-editar-entrega-title").text == "Editar entrega"
    labels = [
        label.get_attribute("textContent").strip()
        for label in driver.find_elements(By.CSS_SELECTOR, "#form-editar-entrega label.field > span")
    ]
    assert labels == ["ID Entrega", "ID Orden", "Recibido por *", "Fecha de entrega *", "Hora de entrega"]
    espera.until(
        lambda d: d.find_element(By.ID, "editar-id-orden-entrega").get_attribute("value") == id_orden
    )
    espera.until(
        lambda d: d.find_element(By.ID, "editar-recibido-por").get_attribute("value") == RECIBIDO_POR
    )

    # --- Boton 'Actualizar entrega': fondo amarillo con texto oscuro ---
    boton_guardar = driver.find_element(By.ID, "btn-guardar-editar-entrega")
    assert boton_guardar.text.strip() == "Actualizar entrega"
    assert estilo_css(driver, boton_guardar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Actualizar entrega' deberia ser el amarillo primario"
    )
    assert estilo_css(driver, boton_guardar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Actualizar entrega' deberia ser oscuro"
    )

    campo_editado = driver.find_element(By.ID, "editar-recibido-por")
    campo_editado.clear()
    campo_editado.send_keys(RECIBIDO_EDITADO)
    valor_recibido = campo_editado.get_attribute("value")

    boton_guardar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-editar-entrega")))

    # --- Feedback global de exito con el mensaje propio del modulo ---
    espera.until(
        lambda d: d.find_element(By.ID, "feedback-modal-title").text.strip() == "Éxito"
    )
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo="Éxito", mensaje="Entrega actualizada exitosamente."
    )

    # El historial se recarga: la fila debe mostrar el nuevo receptor
    def fila_actualizada(d):
        for fila in d.find_elements(
            By.XPATH,
            "//*[@id='tabla-ordenes-entregas-historial']"
            f"//tr[td[2][normalize-space(.)='{id_orden}']]",
        ):
            if fila.find_element(By.CSS_SELECTOR, "td:nth-child(6)").text == valor_recibido:
                return fila
        return False

    fila_editada = espera.until(fila_actualizada)

    # ---- Limpieza: eliminar la entrega (la orden vuelve a Pendiente) y anularla ----
    fila_editada.find_element(By.CSS_SELECTOR, "button[data-action='eliminar-entrega']").click()
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
        f"Entrega editada y limpiada: orden {id_orden} (proveedor: {nombre_proveedor}) "
        f"recibido por '{RECIBIDO_POR}' -> '{valor_recibido}' (feedback: {mensaje}; "
        f"aviso editar pendientes: {mensaje_aviso})"
    )
