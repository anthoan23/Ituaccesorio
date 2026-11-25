import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from helpers import estilo_css, quitar_hover

URL_CLIENTES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/clientes"
TIEMPO_ESPERA = 10

# [cedula, nombre, apellido, celular, correo, direccion]
# La cadena CRUD natural crea/modifica/consulta/elimina este registro.
DATOS_CLIENTE = [
    "71234567",
    "Cliente",
    "Interfaz",
    "04141234777",
    "cliente.interfaz@ituaccesorio.com",
    "Barquisimeto",
]


def esperar_toast(espera, mensaje):
    """Clientes NO usa el FeedbackModal global para el exito: el JS muestra un
    toast propio (#toast-mensaje, clase 'is-visible' que se quita sola a los
    ~3s). Espera el toast, valida su texto exacto y espera su desaparicion."""
    toast = espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#toast-mensaje.is-visible"))
    )
    texto = toast.text.strip()
    assert texto == mensaje, f"Toast inesperado: '{texto}' (se esperaba '{mensaje}')"
    espera.until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, "#toast-mensaje.is-visible"))
    )
    return texto


def test_crear_cliente_natural(driver):
    driver.get(URL_CLIENTES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # La tabla se llena por JS: esperar una fila real (con chip de ID)
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-clientes tr .chip")))

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == "Ituaccesorio - Clientes"
    assert espera.until(
        lambda d: d.find_element(By.CSS_SELECTOR, ".hero__title").text
    ) == "Administración de clientes"
    assert driver.find_element(By.CSS_SELECTOR, ".hero__eyebrow").text == "Gestión de clientes"
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Clientes"
    # textContent (texto del DOM), porque el CSS renderiza los th en mayusculas
    encabezados = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, ".table thead th")
    ]
    assert encabezados == [
        "ID", "Tipo", "Nombre", "Apellido / Razón Social",
        "Celular", "Correo", "Dirección", "Acciones",
    ]

    # --- Boton 'Nuevo cliente': fondo amarillo con texto oscuro (ui-btn--primary) ---
    boton_nuevo = driver.find_element(By.ID, "btn-nuevo-cliente")
    assert boton_nuevo.text.strip() == "Nuevo cliente"
    assert estilo_css(driver, boton_nuevo, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Nuevo cliente' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_nuevo, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Nuevo cliente' deberia ser oscuro"
    )
    boton_nuevo.click()

    # --- Modal 'Registrar cliente': titulo, acciones y campos natural ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-cliente")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-cliente-title").text == "Registrar cliente"
    boton_cancelar = driver.find_element(By.CSS_SELECTOR, "#form-cliente [data-close-modal]")
    assert boton_cancelar.text.strip() == "Cancelar"
    assert "ui-btn--ghost" in boton_cancelar.get_attribute("class")
    assert estilo_css(driver, boton_cancelar, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Cancelar' deberia ser el ghost del tema oscuro"

    # El formulario cambia los campos segun el tipo de cliente elegido
    Select(driver.find_element(By.ID, "tipo-cliente")).select_by_value("natural")
    espera.until(EC.visibility_of_element_located((By.ID, "cedula-input")))
    labels = [
        span.get_attribute("textContent").strip()
        for span in driver.find_elements(By.CSS_SELECTOR, "#campos-natural label.field > span")
    ]
    assert labels == ["Cédula *", "Nombre *", "Apellido *", "Celular *", "Correo", "Dirección"]

    driver.find_element(By.ID, "cedula-input").send_keys(DATOS_CLIENTE[0])
    # Validacion inline de la cedula en tiempo real (JS: '✓ Cédula disponible')
    # Se espera el texto exacto: mientras se escribe aparecen mensajes parciales
    error_cedula = espera.until(
        lambda d: (
            d.find_element(By.ID, "cedula-error")
            if d.find_element(By.ID, "cedula-error").get_attribute("textContent").strip()
            == "✓ Cédula disponible"
            else False
        )
    )
    assert error_cedula.get_attribute("textContent").strip() == "✓ Cédula disponible"
    assert estilo_css(driver, error_cedula, "color") == "rgb(34, 197, 94)", (
        "La validacion de cedula disponible deberia mostrarse en verde"
    )

    driver.find_element(
        By.CSS_SELECTOR, "#form-cliente input[name='nombre']"
    ).send_keys(DATOS_CLIENTE[1])
    driver.find_element(
        By.CSS_SELECTOR, "#form-cliente input[name='apellido']"
    ).send_keys(DATOS_CLIENTE[2])
    driver.find_element(
        By.CSS_SELECTOR, "#form-cliente input[name='celular']"
    ).send_keys(DATOS_CLIENTE[3])
    driver.find_element(
        By.CSS_SELECTOR, "#form-cliente input[name='correo']"
    ).send_keys(DATOS_CLIENTE[4])
    driver.find_element(
        By.CSS_SELECTOR, "#form-cliente input[name='direccion']"
    ).send_keys(DATOS_CLIENTE[5])
    driver.find_element(By.CSS_SELECTOR, "#form-cliente button[type='submit']").click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-cliente")))

    # --- Toast propio del modulo con el mensaje del JS (no del servidor) ---
    esperar_toast(espera, "Cliente creado exitosamente.")

    # --- Fila creada: filtrar con el buscador de la tabla para dejarla visible ---
    buscador = driver.find_element(
        By.CSS_SELECTOR, ".clientes-table-card .table-controls__input"
    )
    buscador.send_keys(DATOS_CLIENTE[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-clientes']//tr[td[1][normalize-space(.)='{DATOS_CLIENTE[0]}']]",
            )
        )
    )
    # textContent porque el CSS puede renderizar el badge en mayusculas
    assert fila.find_element(
        By.CSS_SELECTOR, "td:nth-child(2)"
    ).get_attribute("textContent").strip() == "Persona Natural"
    assert fila.find_element(
        By.CSS_SELECTOR, "td:nth-child(3)"
    ).get_attribute("textContent").strip() == DATOS_CLIENTE[1]
    assert fila.find_element(
        By.CSS_SELECTOR, "td:nth-child(4)"
    ).get_attribute("textContent").strip() == DATOS_CLIENTE[2]

    # El interceptor global de fetch tambien abre el FeedbackModal generico
    # (titulo 'Acción exitosa'); esperar su autocierre para no pisar la cadena.
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Cliente natural creado: {DATOS_CLIENTE[0]} - "
        f"{DATOS_CLIENTE[1]} {DATOS_CLIENTE[2]} (toast: 'Cliente creado exitosamente.')"
    )
