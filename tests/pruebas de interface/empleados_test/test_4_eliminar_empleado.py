import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_EMPLEADOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/empleados"
TIEMPO_ESPERA = 10

# [cedula] - el empleado que creo/modifico la cadena y aqui se elimina
DATOS_EMPLEADO = ["12345679"]


def test_eliminar_empleado(driver):
    driver.get(URL_EMPLEADOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Filtrar por cedula para que la fila quede visible y clickeable
    buscador = driver.find_element(
        By.CSS_SELECTOR, ".empleados-table-card .table-controls__input"
    )
    buscador.send_keys(DATOS_EMPLEADO[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                f"#tabla-empleados tr[data-cedula='{DATOS_EMPLEADO[0]}']",
            )
        )
    )

    # El texto de confirmacion es dinamico: incluye nombre y apellido de la fila
    nombre = fila.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text.strip()
    apellido = fila.find_element(By.CSS_SELECTOR, "td:nth-child(3)").text.strip()
    fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']").click()

    # --- Modal de confirmacion: titulo, texto y estilos de los botones ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-eliminar-empleado")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-eliminar-empleado-title").text == (
        "Eliminar empleado"
    )
    texto_confirmacion = driver.find_element(
        By.ID, "texto-confirmar-eliminar-empleado"
    ).text
    assert texto_confirmacion == f'¿Estás seguro de que quieres eliminar a "{nombre} {apellido}"?', (
        f"El texto de confirmacion no menciona al empleado: '{texto_confirmacion}'"
    )

    boton_confirmar = driver.find_element(By.ID, "btn-confirmar-eliminar-empleado")
    assert boton_confirmar.text.strip() == "Sí, eliminar"
    assert estilo_css(driver, boton_confirmar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Sí, eliminar' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_confirmar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Sí, eliminar' deberia ser oscuro"
    )

    boton_cancelar = driver.find_element(
        By.CSS_SELECTOR, "#modal-eliminar-empleado .ui-form__actions [data-close-modal]"
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

    espera.until(
        EC.invisibility_of_element_located((By.ID, "modal-eliminar-empleado"))
    )
    espera.until(
        EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, f"#tabla-empleados tr[data-cedula='{DATOS_EMPLEADO[0]}']")
        )
    )

    # --- Feedback global de exito con el mensaje del servidor ---
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo="Aviso", mensaje="Empleado eliminado exitosamente"
    )
    print(f"Empleado eliminado: {DATOS_EMPLEADO[0]} (feedback: {mensaje})")
