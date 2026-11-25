import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

# Módulo de entregas: eliminar personal de delivery (pestaña "Personal Delivery")
# Requiere el registro editado por test_3_modificar_personal_delivery.py
# ("Personal Dos", cédula 30124556). Al eliminarlo, la BD queda como estaba.
# MECANISMO DE FEEDBACK: toast propio del módulo (#toast, Utils.mostrarToast);
# el interceptor global de fetch abre además su FeedbackModal sobre el DELETE.
URL_ENTREGAS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/entregas"
TIEMPO_ESPERA = 10

# Nombre completo del registro que la cadena crea/edita y aqui elimina
NOMBRE_COMPLETO = "Personal Dos"

TITULO_PAGINA = "Ituaccesorio - Entregas"


def esperar_toast(espera, mensaje):
    """Espera el toast propio del modulo (#toast con .is-visible), valida su
    texto y espera su desaparicion (se oculta solo a los ~3 segundos)."""
    def toast_visible(d):
        toast = d.find_element(By.ID, "toast")
        if "is-visible" in (toast.get_attribute("class") or ""):
            return toast.text.strip() or False
        return False

    texto = espera.until(toast_visible)
    assert texto == mensaje, f"Toast inesperado: '{texto}' (se esperaba '{mensaje}')"
    espera.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "#toast.is-visible")))
    # El interceptor global tambien abre su FeedbackModal: esperar su autocierre
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    return texto


def test_eliminar_personal_delivery(driver):
    driver.get(URL_ENTREGAS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    assert driver.title == TITULO_PAGINA

    # --- Cambiar a la pestaña Personal Delivery y localizar la fila ---
    driver.find_element(By.ID, "tab-personal").click()
    espera.until(lambda d: d.find_element(By.ID, "tab-personal").get_attribute("aria-selected") == "true")
    buscador = driver.find_element(By.CSS_SELECTOR, "#tab-panel-personal .table-controls__input")
    buscador.send_keys(NOMBRE_COMPLETO)
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-personal']//tr[td[2][normalize-space(.)='{NOMBRE_COMPLETO}']]",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar-personal']").click()

    # --- Modal de confirmacion: titulo, texto dinamico con el nombre y botones ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-eliminar")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-eliminar-title").text == "Eliminar registro"
    texto_confirmacion = driver.find_element(By.ID, "confirmar-mensaje").get_attribute("textContent")
    assert texto_confirmacion == (
        f"¿Estás seguro de que quieres eliminar a {NOMBRE_COMPLETO}?"
    ), f"El texto de confirmacion no menciona al personal: '{texto_confirmacion}'"

    boton_confirmar = driver.find_element(By.ID, "btn-confirmar-eliminar")
    assert boton_confirmar.text.strip() == "Confirmar"
    assert "ui-btn--danger" in boton_confirmar.get_attribute("class")
    assert estilo_css(driver, boton_confirmar, "backgroundColor") == "rgba(220, 38, 38, 0.2)", (
        "El fondo de 'Confirmar' deberia ser el rojo translucido del tema"
    )
    assert estilo_css(driver, boton_confirmar, "borderTopColor") == "rgba(220, 38, 38, 0.3)", (
        "El borde de 'Confirmar' deberia ser el rojo translucido del tema"
    )
    assert estilo_css(driver, boton_confirmar, "color") == "rgb(239, 68, 68)", (
        "El texto de 'Confirmar' deberia ser el rojo de peligro"
    )

    boton_cancelar = driver.find_element(By.CSS_SELECTOR, "#modal-eliminar [data-close-modal]")
    assert boton_cancelar.text.strip() == "Cancelar"
    assert "ui-btn--ghost" in boton_cancelar.get_attribute("class")
    assert estilo_css(driver, boton_cancelar, "color") == "rgb(255, 255, 255)", (
        "El texto de 'Cancelar' deberia ser blanco"
    )

    boton_confirmar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-eliminar")))

    # --- Toast propio del modulo con el mensaje del JS ---
    mensaje = esperar_toast(espera, "Delivery eliminado exitosamente")

    # La fila eliminada desaparece de la tabla
    espera.until(
        EC.invisibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-personal']//tr[td[2][normalize-space(.)='{NOMBRE_COMPLETO}']]",
            )
        )
    )
    print(f"Personal delivery eliminado: {NOMBRE_COMPLETO} (toast: {mensaje})")
