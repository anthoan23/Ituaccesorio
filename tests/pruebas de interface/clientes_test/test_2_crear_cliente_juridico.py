import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from helpers import estilo_css, quitar_hover

URL_CLIENTES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/clientes"
TIEMPO_ESPERA = 10

# [rif, razon_social, telefono] - el telefono es obligatorio en persona juridica.
# Este test se limpia solo: crea el cliente juridico y lo elimina al final.
DATOS_CLIENTE_JURIDICO = ["J-80077123-4", "Empresa Interfaz C.A.", "04149997766"]


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


def test_crear_cliente_juridico(driver):
    driver.get(URL_CLIENTES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-clientes tr .chip")))

    driver.find_element(By.ID, "btn-nuevo-cliente").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-cliente")))
    quitar_hover(driver)

    # El mismo modal de registro cambia los campos al elegir persona juridica
    Select(driver.find_element(By.ID, "tipo-cliente")).select_by_value("juridico")
    espera.until(EC.visibility_of_element_located((By.ID, "rif-input")))
    labels = [
        span.get_attribute("textContent").strip()
        for span in driver.find_elements(By.CSS_SELECTOR, "#campos-juridico label.field > span")
    ]
    assert labels == ["RIF *", "Razón Social *", "Teléfono *", "Correo", "Dirección"]

    driver.find_element(By.ID, "rif-input").send_keys(DATOS_CLIENTE_JURIDICO[0])
    # Validacion inline del RIF en tiempo real (JS: '✓ RIF disponible')
    # Se espera el texto exacto: mientras se escribe aparecen mensajes parciales
    error_rif = espera.until(
        lambda d: (
            d.find_element(By.ID, "rif-error")
            if d.find_element(By.ID, "rif-error").get_attribute("textContent").strip()
            == "✓ RIF disponible"
            else False
        )
    )
    assert error_rif.get_attribute("textContent").strip() == "✓ RIF disponible"
    assert estilo_css(driver, error_rif, "color") == "rgb(34, 197, 94)", (
        "La validacion de RIF disponible deberia mostrarse en verde"
    )

    driver.find_element(By.ID, "razon-social-input").send_keys(DATOS_CLIENTE_JURIDICO[1])
    driver.find_element(By.ID, "telefono-input").send_keys(DATOS_CLIENTE_JURIDICO[2])
    driver.find_element(By.CSS_SELECTOR, "#form-cliente button[type='submit']").click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-cliente")))

    # --- Toast propio del modulo con el mensaje del JS (no del servidor) ---
    esperar_toast(espera, "Cliente creado exitosamente.")

    # --- Fila creada: filtrar con el buscador de la tabla para dejarla visible ---
    buscador = driver.find_element(
        By.CSS_SELECTOR, ".clientes-table-card .table-controls__input"
    )
    buscador.send_keys("Empresa Interfaz")
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-clientes']//tr[td[3][normalize-space(.)='{DATOS_CLIENTE_JURIDICO[1]}']]",
            )
        )
    )
    assert fila.find_element(
        By.CSS_SELECTOR, "td:nth-child(2)"
    ).get_attribute("textContent").strip() == "Persona Jurídica"
    assert fila.find_element(
        By.CSS_SELECTOR, "td:nth-child(4)"
    ).get_attribute("textContent").strip() == DATOS_CLIENTE_JURIDICO[0]

    # --- Limpieza: eliminar el cliente juridico desde la interfaz ---
    fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-eliminar-cliente")))
    quitar_hover(driver)
    # El texto de confirmacion es dinamico: menciona la razon social
    texto_confirmacion = driver.find_element(
        By.ID, "texto-confirmar-eliminar-cliente"
    ).text
    assert texto_confirmacion == (
        f'¿Estás seguro de que quieres eliminar a "{DATOS_CLIENTE_JURIDICO[1]}"?'
    ), f"El texto de confirmacion no menciona al cliente: '{texto_confirmacion}'"

    boton_confirmar = driver.find_element(By.ID, "btn-confirmar-eliminar-cliente")
    assert boton_confirmar.text.strip() == "Sí, eliminar"
    assert estilo_css(driver, boton_confirmar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Sí, eliminar' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_confirmar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Sí, eliminar' deberia ser oscuro"
    )
    boton_confirmar.click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-eliminar-cliente")))

    # El toast de borrado menciona la razon social entre comillas
    esperar_toast(
        espera,
        f'Cliente "{DATOS_CLIENTE_JURIDICO[1]}" eliminado exitosamente.',
    )
    espera.until(
        EC.invisibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-clientes']//tr[td[3][normalize-space(.)='{DATOS_CLIENTE_JURIDICO[1]}']]",
            )
        )
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Cliente juridico creado y eliminado: {DATOS_CLIENTE_JURIDICO[0]} - "
        f"{DATOS_CLIENTE_JURIDICO[1]}"
    )
