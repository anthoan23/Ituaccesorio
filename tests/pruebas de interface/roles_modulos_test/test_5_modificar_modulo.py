import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# [nombre_actual, nombre_nuevo, descripcion_nueva]
# El campo nombre no admite espacios (regla sinEspacios del validador)
DATOS_MODULO = ["ModuloPrueba", "ModuloEditado", "Descripcion del modulo editada"]

# Feedback: toast "Módulo actualizado." + FeedbackModal generico del
# interceptor de fetch para todo PUT exitoso (feedback-modal.js)
MENSAJE_TOAST = "Módulo actualizado."
FEEDBACK_TITULO = "Acción exitosa"
FEEDBACK_MENSAJE = "Actualización realizada satisfactoriamente."


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


def test_modificar_modulo(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Los módulos viven en la pestaña "Módulos" de la vista de usuarios
    driver.find_element(By.ID, "tab-modulos").click()

    # Filtrar por nombre para que la fila quede visible y clickeable
    buscador = driver.find_element(By.CSS_SELECTOR, "#tab-panel-modulos .table-controls__input")
    buscador.send_keys(DATOS_MODULO[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-modulos']//tr[td[1][normalize-space(.)='{DATOS_MODULO[0]}']]",
            )
        )
    )

    # --- Boton editar de la fila: borde e icono amarillos ---
    boton_editar = fila.find_element(By.CSS_SELECTOR, "button[data-action='edit-modulo']")
    assert "icon-action--edit" in boton_editar.get_attribute("class")
    quitar_hover(driver)
    assert estilo_css(driver, boton_editar, "borderTopColor") == "rgb(243, 197, 0)", (
        "El borde del boton editar deberia ser amarillo"
    )
    svg_editar = boton_editar.find_element(By.TAG_NAME, "svg")
    assert estilo_css(driver, svg_editar, "color") == "rgb(243, 197, 0)", (
        "El icono de editar deberia ser amarillo"
    )
    boton_editar.click()

    # --- Modal 'Administrar módulos' en modo edicion: campos precargados ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-admin-modulos")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-modulos-title").text == "Administrar módulos"
    assert driver.find_element(By.CSS_SELECTOR, "#form-modulo input[name='nombre']").get_attribute("value") == (
        DATOS_MODULO[0]
    )
    # El JS puso el id del modulo en el campo oculto: el submit ira por PUT
    assert driver.find_element(By.CSS_SELECTOR, "#form-modulo input[name='id']").get_attribute("value") != "", (
        "El formulario deberia estar editando un modulo existente (id precargado)"
    )

    nombre = driver.find_element(By.CSS_SELECTOR, "#form-modulo input[name='nombre']")
    nombre.clear()
    nombre.send_keys(DATOS_MODULO[1])
    descripcion = driver.find_element(By.CSS_SELECTOR, "#form-modulo textarea[name='descripcion']")
    descripcion.clear()
    descripcion.send_keys(DATOS_MODULO[2])
    driver.find_element(By.CSS_SELECTOR, "#form-modulo button[type='submit']").click()

    # --- Feedback: toast del modulo + modal global del interceptor ---
    esperar_toast(driver, espera, MENSAJE_TOAST)
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo=FEEDBACK_TITULO, mensaje=FEEDBACK_MENSAJE
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-admin-modulos")))

    # La tabla se re-renderiza: refrescar el filtro para ver la fila editada
    buscador.clear()
    buscador.send_keys(DATOS_MODULO[1])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-modulos']//tr[td[1][normalize-space(.)='{DATOS_MODULO[1]}']]",
            )
        )
    )
    assert DATOS_MODULO[2] in fila.text
    print(f"Modulo modificado: {DATOS_MODULO[0]} -> {DATOS_MODULO[1]} (toast: {MENSAJE_TOAST} | feedback: {mensaje})")
