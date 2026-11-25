import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

URL_CLIENTES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/clientes"
TIEMPO_ESPERA = 10

# [cedula, apellido_nuevo] - el cliente natural que creo test_1_crear_cliente_natural
DATOS_CLIENTE = ["71234567", "Interfaz Editado"]


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


def test_modificar_cliente(driver):
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
    fila.find_element(By.CSS_SELECTOR, "button[data-action='editar']").click()

    # --- Modal de edicion: el JS NO cambia el titulo ni el boton al editar ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-cliente")))
    quitar_hover(driver)
    # Hallazgo: el titulo sigue siendo 'Registrar cliente' tambien en edicion
    assert driver.find_element(By.ID, "modal-cliente-title").text == "Registrar cliente"
    # Al editar, el tipo de cliente y la cedula quedan bloqueados
    assert driver.find_element(By.ID, "tipo-cliente").get_attribute("disabled"), (
        "El tipo de cliente deberia quedar deshabilitado al editar"
    )
    cedula = driver.find_element(By.ID, "cedula-input")
    assert cedula.get_attribute("disabled"), (
        "La cedula deberia quedar deshabilitada al editar"
    )
    assert cedula.get_attribute("value") == DATOS_CLIENTE[0]
    # El JS marca la cedula bloqueada con un hint azul (no rojo)
    hint_cedula = driver.find_element(By.ID, "cedula-error")
    assert hint_cedula.get_attribute("textContent").strip() == "✓ Edición (no se puede modificar)"
    assert estilo_css(driver, hint_cedula, "color") == "rgb(96, 165, 250)", (
        "El hint de cedula en edicion deberia ser azul"
    )

    # El texto del submit tampoco cambia al editar
    boton_guardar = driver.find_element(By.CSS_SELECTOR, "#form-cliente button[type='submit']")
    assert boton_guardar.text.strip() == "Guardar cliente"
    assert estilo_css(driver, boton_guardar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Guardar cliente' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_guardar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Guardar cliente' deberia ser oscuro"
    )

    apellido = driver.find_element(By.CSS_SELECTOR, "#form-cliente input[name='apellido']")
    apellido.clear()
    apellido.send_keys(DATOS_CLIENTE[1])
    boton_guardar.click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-cliente")))

    # --- Toast propio del modulo con el mensaje del JS (no del servidor) ---
    esperar_toast(espera, "Cliente actualizado exitosamente.")

    # La tabla se re-renderiza: refrescar el filtro para ver la fila editada
    buscador.clear()
    buscador.send_keys(DATOS_CLIENTE[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-clientes']//tr[td[1][normalize-space(.)='{DATOS_CLIENTE[0]}']]"
                f"[td[4][normalize-space(.)='{DATOS_CLIENTE[1]}']]",
            )
        )
    )
    assert DATOS_CLIENTE[1] in fila.text
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Cliente modificado: cedula {DATOS_CLIENTE[0]} -> "
        f"apellido {DATOS_CLIENTE[1]} (toast: 'Cliente actualizado exitosamente.')"
    )
