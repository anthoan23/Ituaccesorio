import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# [nombre_actual, nombre_nuevo] - el usuario que creo test_1_crear_usuario
DATOS_USUARIO = ["Usuario Interfaz", "Usuario Interfaz Editado"]


def esperar_toast(espera, mensaje):
    """Usuarios NO usa el FeedbackModal global para el exito: el JS muestra un
    toast propio (#toast, clase 'is-visible' que se quita sola a los ~2.4s).
    Espera el toast, valida su texto exacto y espera su desaparicion."""
    toast = espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#toast.is-visible"))
    )
    texto = toast.text.strip()
    assert texto == mensaje, f"Toast inesperado: '{texto}' (se esperaba '{mensaje}')"
    espera.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "#toast.is-visible")))
    return texto


def test_modificar_usuario(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Filtrar por nombre para que la fila quede visible y clickeable
    buscador = driver.find_element(
        By.CSS_SELECTOR, "#tab-panel-usuarios .table-controls__input"
    )
    buscador.send_keys(DATOS_USUARIO[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-usuarios']//tr[td[2][normalize-space(.)='{DATOS_USUARIO[0]}']]",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='edit-usuario']").click()

    # --- Modal de edicion: el JS NO cambia el titulo ni el texto del boton ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-admin-usuarios")))
    quitar_hover(driver)
    # Hallazgo: el titulo sigue siendo 'Crear o editar usuario' tambien al editar
    assert driver.find_element(By.ID, "modal-usuarios-title").text == (
        "Crear o editar usuario"
    )
    # El llenado del formulario es asincrono (carga la cedula segun el rol);
    # se espera la opcion de cedula seleccionada antes de editar
    espera.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "#form-usuario select[name='cedula_personal'] option[value]:not([value=''])[selected]",
            )
        )
    )
    # Hallazgo: al editar, la contraseña se vuelve opcional y el placeholder
    # del campo cambia
    password = driver.find_element(By.CSS_SELECTOR, "#form-usuario input[name='password']")
    assert password.get_attribute("placeholder") == "Dejar vacío para conservar"

    boton_guardar = driver.find_element(
        By.CSS_SELECTOR, "#form-usuario button[type='submit']"
    )
    assert boton_guardar.text.strip() == "Guardar usuario"
    assert estilo_css(driver, boton_guardar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Guardar usuario' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_guardar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Guardar usuario' deberia ser oscuro"
    )

    nombre = driver.find_element(By.CSS_SELECTOR, "#form-usuario input[name='nombre']")
    nombre.clear()
    nombre.send_keys(DATOS_USUARIO[1])
    boton_guardar.click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-admin-usuarios")))

    # --- Toast propio del modulo con el mensaje del JS (no del servidor) ---
    esperar_toast(espera, "Usuario actualizado.")

    # La tabla se re-renderiza: refrescar el filtro para ver la fila editada
    buscador.clear()
    buscador.send_keys(DATOS_USUARIO[1])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-usuarios']//tr[td[2][normalize-space(.)='{DATOS_USUARIO[1]}']]",
            )
        )
    )
    assert DATOS_USUARIO[1] in fila.text
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Usuario modificado: {DATOS_USUARIO[0]} -> {DATOS_USUARIO[1]} "
        f"(toast: 'Usuario actualizado.')"
    )
