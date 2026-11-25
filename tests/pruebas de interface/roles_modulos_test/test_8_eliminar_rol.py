import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# [nombre] - el registro que la cadena crea/modifica y aqui elimina
DATOS_ROL = ["Rol Editado"]

# Feedback del borrado: toast "Registro eliminado." (usuarios.js) + FeedbackModal
# generico del interceptor de fetch para todo DELETE exitoso (feedback-modal.js)
MENSAJE_TOAST = "Registro eliminado."
FEEDBACK_TITULO = "Acción exitosa"
FEEDBACK_MENSAJE = "Eliminación realizada satisfactoriamente."


def esperar_toast(driver, espera, mensaje):
    """Espera el toast (#toast) con el mensaje del modulo y comprueba que sigue
    visible (clase .is-visible): mostrarToast lo oculta a los 2.4 s pero el
    texto permanece en el DOM."""
    espera.until(EC.text_to_be_present_in_element((By.ID, "toast"), mensaje))
    toast = driver.find_element(By.ID, "toast")
    assert "is-visible" in (toast.get_attribute("class") or ""), (
        f"El toast deberia estar visible con el mensaje '{mensaje}'"
    )
    return mensaje


def test_eliminar_rol(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Los roles viven en la pestaña "Roles" de la vista de usuarios
    driver.find_element(By.ID, "tab-roles").click()

    # Filtrar por nombre para que la fila quede visible y clickeable
    buscador = driver.find_element(By.CSS_SELECTOR, "#tab-panel-roles .table-controls__input")
    buscador.send_keys(DATOS_ROL[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-roles']//tr[td[1][normalize-space(.)='{DATOS_ROL[0]}']]",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='delete-rol']").click()

    # --- Modal de confirmacion: titulo, texto dinamico y estilos de los botones ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-confirmacion")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-confirmacion-title").text == "Confirmar acción"
    texto_confirmacion = driver.find_element(By.ID, "confirmacion-mensaje").text
    assert texto_confirmacion == (
        f"¿Seguro que desea eliminar el rol {DATOS_ROL[0]}? Esta acción no se puede deshacer."
    ), f"El texto de confirmacion no menciona el rol: '{texto_confirmacion}'"

    boton_confirmar = driver.find_element(By.ID, "confirmacion-btn")
    assert boton_confirmar.text.strip() == "Confirmar"
    assert "ui-btn--danger" in boton_confirmar.get_attribute("class")
    assert estilo_css(driver, boton_confirmar, "backgroundColor") == "rgba(220, 38, 38, 0.2)", (
        "El fondo de 'Confirmar' deberia ser el rojo translucido de peligro"
    )
    assert estilo_css(driver, boton_confirmar, "color") == "rgb(239, 68, 68)", (
        "El texto de 'Confirmar' deberia ser rojo peligro"
    )

    boton_cancelar = driver.find_element(
        By.CSS_SELECTOR, "#modal-confirmacion .ui-form__actions [data-close-modal]"
    )
    assert boton_cancelar.text.strip() == "Cancelar"
    assert "ui-btn--ghost" in boton_cancelar.get_attribute("class")
    assert estilo_css(driver, boton_cancelar, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Cancelar' deberia ser el ghost del tema oscuro"
    assert estilo_css(driver, boton_cancelar, "color") == "rgb(255, 255, 255)", (
        "El texto de 'Cancelar' deberia ser blanco"
    )

    boton_confirmar.click()

    # --- Feedback: toast del modulo + modal global del interceptor ---
    esperar_toast(driver, espera, MENSAJE_TOAST)
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo=FEEDBACK_TITULO, mensaje=FEEDBACK_MENSAJE
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-confirmacion")))

    # El rol desaparece de la tabla (el filtro sigue activo)
    espera.until(
        EC.invisibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-roles']//tr[td[1][normalize-space(.)='{DATOS_ROL[0]}']]",
            )
        )
    )
    print(f"Rol eliminado: {DATOS_ROL[0]} (toast: {MENSAJE_TOAST} | feedback: {mensaje})")
