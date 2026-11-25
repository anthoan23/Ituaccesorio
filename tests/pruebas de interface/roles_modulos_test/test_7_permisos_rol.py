import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# Rol al que se le editan los permisos (creado y modificado en las pruebas
# anteriores; se elimina al final de la cadena en test_8)
ROL_OBJETIVO = "Rol Editado"

# Feedback doble del guardado (usuarios.js): toast propio del modulo...
MENSAJE_TOAST = "Permisos actualizados correctamente"
# ...y FeedbackModal generico del interceptor de fetch para todo PUT exitoso
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


def test_modificar_permisos_rol(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-usuarios tr")))

    # El editor de permisos vive dentro del modal de usuarios
    driver.find_element(By.ID, "btn-admin-usuarios").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-admin-usuarios")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-usuarios-title").text == "Crear o editar usuario"
    assert driver.find_element(
        By.CSS_SELECTOR, "#permisos-rol-container .section-title"
    ).text == "Permisos del rol seleccionado"

    # --- Seleccionar el rol de prueba en el formulario ---
    select_rol = Select(driver.find_element(By.CSS_SELECTOR, "#form-usuario select[name='rol_id']"))
    espera.until(
        lambda d: any(
            o.get_attribute("textContent").strip() == ROL_OBJETIVO for o in select_rol.options
        ) or None
    )
    select_rol.select_by_visible_text(ROL_OBJETIVO)

    # La tabla de permisos por modulo se llena de forma asincrona
    casilla = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#permisos-grid .permiso-item input[data-permiso='registrar']")
        )
    )
    etiquetas_permisos = [
        label.get_attribute("textContent").strip().split("\n")[0]
        for label in driver.find_elements(By.CSS_SELECTOR, "#permisos-grid .permiso-checkboxes label")
    ][:3]
    assert etiquetas_permisos == ["Registrar", "Modificar", "Eliminar"]

    # --- Boton 'Guardar permisos': fondo amarillo con texto oscuro ---
    boton_guardar = driver.find_element(By.ID, "btn-guardar-permisos")
    assert boton_guardar.text.strip() == "Guardar permisos"
    assert estilo_css(driver, boton_guardar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Guardar permisos' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_guardar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Guardar permisos' deberia ser oscuro"
    )

    # Alterna el permiso "Registrar" del primer modulo listado
    estado_original = casilla.is_selected()
    casilla.click()
    estado_esperado = not estado_original
    boton_guardar.click()

    # --- Feedback: primero el toast del modulo y luego el modal global ---
    esperar_toast(driver, espera, MENSAJE_TOAST)
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo=FEEDBACK_TITULO, mensaje=FEEDBACK_MENSAJE
    )

    # La tabla de permisos se vuelve a pintar: esperar la fila vieja rota y releer
    espera.until(EC.staleness_of(casilla))
    casilla_nueva = driver.find_element(
        By.CSS_SELECTOR, "#permisos-grid .permiso-item input[data-permiso='registrar']"
    )
    assert casilla_nueva.is_selected() == estado_esperado, (
        "El permiso 'Registrar' deberia quedar alternado tras recargar la grilla"
    )
    print(f"Permisos del rol '{ROL_OBJETIVO}' actualizados (toast: {MENSAJE_TOAST} | feedback: {mensaje})")
