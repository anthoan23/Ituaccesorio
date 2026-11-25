import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_CARGOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/cargos"
TIEMPO_ESPERA = 10

# [nombre] - el registro que la cadena crea/modifica y aqui elimina
DATOS_CARGO = ["Cargo Interfaz Editado"]


def test_eliminar_cargo(driver):
    driver.get(URL_CARGOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Filtrar por nombre para que la fila quede visible y clickeable
    buscador = driver.find_element(
        By.CSS_SELECTOR, ".cargos-table-card .table-controls__input"
    )
    buscador.send_keys(DATOS_CARGO[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-cargos']//tr[td[2][normalize-space(.)='{DATOS_CARGO[0]}']]",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']").click()

    # --- Modal de confirmacion: titulo, texto dinamico y estilos de los botones ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-eliminar-cargo")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-eliminar-cargo-title").text == "Eliminar cargo"
    texto_confirmacion = driver.find_element(By.ID, "texto-confirmar-eliminar-cargo").text
    assert texto_confirmacion == (
        f'¿Estás seguro de que quieres eliminar el cargo "{DATOS_CARGO[0]}"?'
    ), f"El texto de confirmacion no menciona el cargo: '{texto_confirmacion}'"

    boton_confirmar = driver.find_element(By.ID, "btn-confirmar-eliminar-cargo")
    assert boton_confirmar.text.strip() == "Sí, eliminar"
    assert estilo_css(driver, boton_confirmar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Sí, eliminar' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_confirmar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Sí, eliminar' deberia ser oscuro"
    )

    boton_cancelar = driver.find_element(
        By.CSS_SELECTOR, "#modal-eliminar-cargo .ui-form__actions [data-close-modal]"
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

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-eliminar-cargo")))
    espera.until(
        EC.invisibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-cargos']//tr[td[2][normalize-space(.)='{DATOS_CARGO[0]}']]",
            )
        )
    )

    # --- Feedback global de exito con el mensaje del servidor ---
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo="Aviso", mensaje="Cargo eliminado exitosamente"
    )
    print(f"Cargo eliminado: {DATOS_CARGO[0]} (feedback: {mensaje})")
