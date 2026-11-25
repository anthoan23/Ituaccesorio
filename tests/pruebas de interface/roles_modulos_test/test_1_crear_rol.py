import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# [nombre, descripcion] - la cadena CRUD crea/modifica/consulta/elimina este rol
DATOS_ROL = ["Rol Prueba", "Rol de prueba de interface"]

# Feedback del modulo (usuarios.js): toast #toast con texto propio.
# Ademas, el interceptor global de fetch (feedback-modal.js) abre el
# FeedbackModal con titulo y mensaje genericos para todo POST exitoso.
MENSAJE_TOAST = "Rol creado."
FEEDBACK_TITULO = "Acción exitosa"
FEEDBACK_MENSAJE = "Registro realizado satisfactoriamente."


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


def test_crear_rol(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-usuarios tr")))

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == "Ituaccesorio - Usuarios"
    assert driver.find_element(By.CSS_SELECTOR, ".hero__title").text == "Gestión de usuarios y roles"
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Usuarios"
    # textContent (texto del DOM): el CSS renderiza el eyebrow en mayusculas
    assert driver.find_element(By.CSS_SELECTOR, ".hero__eyebrow").get_attribute("textContent").strip() == (
        "Seguridad y acceso"
    )
    etiquetas_stats = [
        e.get_attribute("textContent").strip()
        for e in driver.find_elements(By.CSS_SELECTOR, ".stat-card__label")
    ]
    assert etiquetas_stats == ["Usuarios", "Roles", "Módulos"]
    pestanas = [
        t.get_attribute("textContent").strip()
        for t in driver.find_elements(By.CSS_SELECTOR, ".tab")
    ]
    assert pestanas == ["Usuarios", "Roles", "Módulos"]

    # --- Boton 'Registrar roles': arranca como ghost (la pestaña activa es usuarios) ---
    boton_roles = driver.find_element(By.ID, "btn-admin-roles")
    assert boton_roles.text.strip() == "Registrar roles"
    assert "ui-btn--ghost" in boton_roles.get_attribute("class")
    assert estilo_css(driver, boton_roles, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Registrar roles' deberia ser el ghost del tema oscuro"
    assert estilo_css(driver, boton_roles, "color") == "rgb(255, 255, 255)", (
        "El texto de 'Registrar roles' deberia ser blanco"
    )

    # --- La pestaña Roles activa el boton en amarillo (syncAdminButtonsWithTab) ---
    driver.find_element(By.ID, "tab-roles").click()
    assert "ui-btn--primary" in boton_roles.get_attribute("class")
    quitar_hover(driver)
    assert estilo_css(driver, boton_roles, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Registrar roles' activo deberia ser amarillo"
    )
    assert estilo_css(driver, boton_roles, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Registrar roles' activo deberia ser oscuro"
    )

    # Encabezados de la tabla de roles (textContent por el uppercase del CSS)
    encabezados = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, "#tab-panel-roles .table thead th")
    ]
    assert encabezados == ["Nombre", "Descripción", "Acciones"]

    boton_roles.click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-admin-roles")))
    quitar_hover(driver)

    # --- Modal 'Administrar roles': titulo, eyebrow y labels ---
    assert driver.find_element(By.ID, "modal-roles-title").text == "Administrar roles"
    assert driver.find_element(
        By.CSS_SELECTOR, "#modal-admin-roles .modal__eyebrow"
    ).get_attribute("textContent").strip() == "Roles"
    labels = [
        s.get_attribute("textContent").strip()
        for s in driver.find_elements(By.CSS_SELECTOR, "#form-rol .field > span")
    ]
    assert labels == ["Nombre *", "Descripción"]

    # --- Boton 'Guardar rol': fondo amarillo con texto oscuro; 'Limpiar' ghost ---
    boton_guardar = driver.find_element(By.CSS_SELECTOR, "#form-rol button[type='submit']")
    assert boton_guardar.text.strip() == "Guardar rol"
    assert estilo_css(driver, boton_guardar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Guardar rol' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_guardar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Guardar rol' deberia ser oscuro"
    )
    boton_limpiar = driver.find_element(
        By.CSS_SELECTOR, "#form-rol [data-reset-form='rol']"
    )
    assert boton_limpiar.text.strip() == "Limpiar"
    assert "ui-btn--ghost" in boton_limpiar.get_attribute("class")
    assert estilo_css(driver, boton_limpiar, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Limpiar' deberia ser el ghost del tema oscuro"

    driver.find_element(
        By.CSS_SELECTOR, "#form-rol input[name='nombre']"
    ).send_keys(DATOS_ROL[0])
    driver.find_element(
        By.CSS_SELECTOR, "#form-rol textarea[name='descripcion']"
    ).send_keys(DATOS_ROL[1])
    boton_guardar.click()

    # --- Feedback: primero el toast del modulo y luego el modal global ---
    esperar_toast(driver, espera, MENSAJE_TOAST)
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo=FEEDBACK_TITULO, mensaje=FEEDBACK_MENSAJE
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-admin-roles")))

    # --- Fila creada por el JS: filtrar en la tabla de roles para verla ---
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
    assert DATOS_ROL[1] in fila.text
    print(f"Rol creado: {DATOS_ROL[0]} (toast: {MENSAJE_TOAST} | feedback: {mensaje})")
