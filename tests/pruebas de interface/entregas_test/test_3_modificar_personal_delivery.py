import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

# Módulo de entregas: modificar personal de delivery (pestaña "Personal Delivery")
# Requiere el registro creado por test_1_crear_personal_delivery.py
# ("Personal Delivery", cédula 30124556).
# OJO: el input de nombre tiene maxlength=15, por eso el nuevo nombre
# ("Personal Dos", 12 caracteres) cabe completo; el nombre completo editado
# queda "Personal Dos".
# MECANISMO DE FEEDBACK: toast propio del módulo (#toast, Utils.mostrarToast);
# el interceptor global de fetch abre además su FeedbackModal sobre el PUT.
URL_ENTREGAS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/entregas"
TIEMPO_ESPERA = 10

# [nombre_actual, nombre_nuevo] (el nombre completo pasa de "Personal Delivery" a "Personal Dos")
NOMBRE_ACTUAL = "Personal"
NOMBRE_NUEVO = "Personal Dos"
NOMBRE_COMPLETO_ACTUAL = "Personal Delivery"
NOMBRE_COMPLETO_NUEVO = "Personal Dos"

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


def test_modificar_personal_delivery(driver):
    driver.get(URL_ENTREGAS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    assert driver.title == TITULO_PAGINA

    # --- Cambiar a la pestaña Personal Delivery y localizar la fila ---
    driver.find_element(By.ID, "tab-personal").click()
    espera.until(lambda d: d.find_element(By.ID, "tab-personal").get_attribute("aria-selected") == "true")
    buscador = driver.find_element(By.CSS_SELECTOR, "#tab-panel-personal .table-controls__input")
    buscador.send_keys(NOMBRE_ACTUAL)
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-personal']//tr[td[2][normalize-space(.)='{NOMBRE_COMPLETO_ACTUAL}']]",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='editar-personal']").click()

    # --- Modal en modo edicion: titulo dinamico 'Editar delivery' y cedula bloqueada ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-personal")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-personal-title").text == "Editar delivery"
    campo_cedula = driver.find_element(By.ID, "personal-cedula")
    assert campo_cedula.get_attribute("disabled"), "La cedula debe llegar deshabilitada en edicion"
    assert campo_cedula.get_attribute("value") == "30124556"

    # --- Boton 'Guardar delivery' en modo edicion: amarillo primario ---
    boton_guardar = driver.find_element(By.CSS_SELECTOR, "#form-personal button[type='submit']")
    assert boton_guardar.text.strip() == "Guardar delivery"
    assert estilo_css(driver, boton_guardar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Guardar delivery' deberia ser el amarillo primario"
    )
    assert estilo_css(driver, boton_guardar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Guardar delivery' deberia ser oscuro"
    )

    # Solo se cambia el nombre (maxlength=15: "Personal Dos" cabe completo)
    nombre = driver.find_element(By.ID, "personal-nombre")
    nombre.clear()
    nombre.send_keys(NOMBRE_NUEVO)
    boton_guardar.click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-personal")))

    # --- Toast propio del modulo con el mensaje del JS ---
    mensaje = esperar_toast(espera, "Delivery actualizado exitosamente")

    # La tabla se re-renderiza: refrescar el filtro y verificar el nuevo nombre
    buscador.clear()
    buscador.send_keys(NOMBRE_NUEVO)
    fila_editada = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-personal']//tr[td[2][normalize-space(.)='{NOMBRE_COMPLETO_NUEVO}']]",
            )
        )
    )
    cedula_editada = fila_editada.find_element(By.CSS_SELECTOR, "td:nth-child(1)").get_attribute("textContent").strip()
    assert cedula_editada == "30124556"
    print(
        f"Personal delivery modificado: '{NOMBRE_COMPLETO_ACTUAL}' -> "
        f"'{NOMBRE_COMPLETO_NUEVO}' (toast: {mensaje})"
    )
