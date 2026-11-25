import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from helpers import estilo_css, quitar_hover

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# [nombre, password]
# La cedula y el rol se eligen de los selects del formulario (no son datos fijos).
# La cadena CRUD crea/modifica/consulta/elimina este registro.
DATOS_USUARIO = ["Usuario Interfaz", "clave12345"]


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


def test_crear_usuario(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # La tabla se llena por JS: esperar una fila real (con chip de ID)
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-usuarios tr .chip")))

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == "Ituaccesorio - Usuarios"
    assert espera.until(
        lambda d: d.find_element(By.CSS_SELECTOR, ".hero__title").text
    ) == "Gestión de usuarios y roles"
    assert driver.find_element(By.CSS_SELECTOR, ".hero__eyebrow").text == "Seguridad y acceso"
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Usuarios"
    # textContent (texto del DOM), porque el CSS renderiza los th en mayusculas
    encabezados = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, ".usuarios-table thead th")
    ]
    assert encabezados == ["ID", "Usuario", "Cédula", "Rol", "Acciones"]
    pestanas = [
        boton.text.strip()
        for boton in driver.find_elements(By.CSS_SELECTOR, ".tabs .tab")
    ]
    assert pestanas == ["Usuarios", "Roles", "Módulos"]

    # Barra de administracion: el boton de la pestaña activa es primario y los
    # demas quedan como ghost (el JS intercambia las clases al cambiar de tab)
    boton_usuarios = driver.find_element(By.ID, "btn-admin-usuarios")
    assert boton_usuarios.text.strip() == "Registrar usuarios"
    assert estilo_css(driver, boton_usuarios, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Registrar usuarios' deberia ser amarillo (tab activa)"
    )
    boton_roles = driver.find_element(By.ID, "btn-admin-roles")
    assert boton_roles.text.strip() == "Registrar roles"
    assert estilo_css(driver, boton_roles, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Registrar roles' deberia ser el ghost del tema oscuro"

    # --- Modal 'Crear o editar usuario': titulo y acciones ---
    boton_usuarios.click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-admin-usuarios")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-usuarios-title").text == (
        "Crear o editar usuario"
    )
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
    boton_limpiar = driver.find_element(
        By.CSS_SELECTOR, "#form-usuario [data-reset-form='usuario']"
    )
    assert boton_limpiar.text.strip() == "Limpiar"
    assert "ui-btn--ghost" in boton_limpiar.get_attribute("class")

    # El select de roles se llena al cargar la pagina (opcion 1 = primer rol real)
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#form-usuario select[name='rol_id'] option:nth-child(2)")
        )
    )
    Select(driver.find_element(By.CSS_SELECTOR, "#form-usuario select[name='rol_id']")).select_by_index(1)

    # El select de cedula solo se llena despues de elegir un rol; se toma la
    # primera opcion disponible (indice 1 = primer registro real)
    espera.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "#form-usuario select[name='cedula_personal'] option[value]:not([value=''])",
            )
        )
    )
    Select(driver.find_element(By.CSS_SELECTOR, "#form-usuario select[name='cedula_personal']")).select_by_index(1)

    driver.find_element(
        By.CSS_SELECTOR, "#form-usuario input[name='nombre']"
    ).send_keys(DATOS_USUARIO[0])
    driver.find_element(
        By.CSS_SELECTOR, "#form-usuario input[name='password']"
    ).send_keys(DATOS_USUARIO[1])
    boton_guardar.click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-admin-usuarios")))

    # --- Toast propio del modulo con el mensaje del JS (no del servidor) ---
    esperar_toast(espera, "Usuario creado.")

    # --- Fila creada: filtrar con el buscador de la tabla para dejarla visible ---
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
    assert fila.find_element(By.CSS_SELECTOR, "td:nth-child(4)").text.strip() != "", (
        "El rol asignado deberia verse en la fila"
    )

    # El interceptor global de fetch tambien abre el FeedbackModal generico
    # (titulo 'Acción exitosa'); esperar su autocierre para no pisar la cadena.
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Usuario creado: {DATOS_USUARIO[0]} (toast: 'Usuario creado.')")
