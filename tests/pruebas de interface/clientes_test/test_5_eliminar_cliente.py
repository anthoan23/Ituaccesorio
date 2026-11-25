import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

URL_CLIENTES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/clientes"
TIEMPO_ESPERA = 10

# [cedula, nombre, apellido] - el cliente que la cadena crea/modifica y aqui elimina
DATOS_CLIENTE = ["71234567", "Cliente", "Interfaz Editado"]


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


def test_eliminar_cliente(driver):
    driver.get(URL_CLIENTES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Filtrar por cedula para que la fila quede visible y clickeable
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
    fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']").click()

    # --- Modal de confirmacion: titulo, texto dinamico y estilos de los botones ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-eliminar-cliente")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-eliminar-cliente-title").text == (
        "Eliminar cliente"
    )
    # El texto de confirmacion es dinamico: incluye nombre y apellido del cliente
    texto_confirmacion = driver.find_element(
        By.ID, "texto-confirmar-eliminar-cliente"
    ).text
    assert texto_confirmacion == (
        f'¿Estás seguro de que quieres eliminar a "{DATOS_CLIENTE[1]} {DATOS_CLIENTE[2]}"?'
    ), f"El texto de confirmacion no menciona al cliente: '{texto_confirmacion}'"

    boton_confirmar = driver.find_element(By.ID, "btn-confirmar-eliminar-cliente")
    assert boton_confirmar.text.strip() == "Sí, eliminar"
    assert estilo_css(driver, boton_confirmar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Sí, eliminar' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_confirmar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Sí, eliminar' deberia ser oscuro"
    )

    boton_cancelar = driver.find_element(
        By.CSS_SELECTOR, "#modal-eliminar-cliente .ui-form__actions [data-close-modal]"
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

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-eliminar-cliente")))

    # --- Toast propio del modulo: menciona el nombre completo del cliente ---
    esperar_toast(
        espera,
        f'Cliente "{DATOS_CLIENTE[1]} {DATOS_CLIENTE[2]}" eliminado exitosamente.',
    )

    espera.until(
        EC.invisibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-clientes']//tr[td[1][normalize-space(.)='{DATOS_CLIENTE[0]}']]",
            )
        )
    )
    # El interceptor global de fetch tambien abre el FeedbackModal generico
    # (titulo 'Acción exitosa'); esperar su autocierre para no pisar la cadena.
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Cliente eliminado: {DATOS_CLIENTE[0]} - "
        f"{DATOS_CLIENTE[1]} {DATOS_CLIENTE[2]}"
    )
