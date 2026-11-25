import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_ESPECIALIDADES = (
    f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/especialidades"
)
TIEMPO_ESPERA = 10

# [nombre_actual, nombre_nuevo, descripcion_nueva]
DATOS_ESPECIALIDAD = [
    "Especialidad Interfaz",
    "Especialidad Interfaz Editada",
    "Descripcion de especialidad editada",
]


def test_modificar_especialidad(driver):
    driver.get(URL_ESPECIALIDADES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Filtrar por nombre para que la fila quede visible y clickeable
    buscador = driver.find_element(
        By.CSS_SELECTOR, ".especialidades-table-card .table-controls__input"
    )
    buscador.send_keys(DATOS_ESPECIALIDAD[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//*[@id='tabla-especialidades']//tr"
                f"[td[2][normalize-space(.)='{DATOS_ESPECIALIDAD[0]}']]",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='editar']").click()

    # --- Modal 'Modificar especialidad': titulo y campos precargados ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-editar-especialidad")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-editar-especialidad-title").text == (
        "Modificar especialidad"
    )
    assert driver.find_element(By.ID, "editar-nombre-especialidad").get_attribute("value") == (
        DATOS_ESPECIALIDAD[0]
    )

    # --- Boton 'Guardar cambios': fondo amarillo con texto oscuro ---
    boton_guardar = driver.find_element(
        By.CSS_SELECTOR, "#form-editar-especialidad button[type='submit']"
    )
    assert boton_guardar.text.strip() == "Guardar cambios"
    assert estilo_css(driver, boton_guardar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Guardar cambios' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_guardar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Guardar cambios' deberia ser oscuro"
    )

    # --- Boton 'Cancelar': estilo fantasma (ghost, colores del tema oscuro) ---
    boton_cancelar = driver.find_element(
        By.CSS_SELECTOR, "#modal-editar-especialidad .ui-form__actions [data-close-modal]"
    )
    assert boton_cancelar.text.strip() == "Cancelar"
    assert "ui-btn--ghost" in boton_cancelar.get_attribute("class")
    assert estilo_css(driver, boton_cancelar, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Cancelar' deberia ser el ghost del tema oscuro"

    nombre = driver.find_element(By.ID, "editar-nombre-especialidad")
    nombre.clear()
    nombre.send_keys(DATOS_ESPECIALIDAD[1])
    descripcion = driver.find_element(By.ID, "editar-descripcion-especialidad")
    descripcion.clear()
    descripcion.send_keys(DATOS_ESPECIALIDAD[2])
    boton_guardar.click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-editar-especialidad")))

    # --- Feedback global de exito con el mensaje del servidor ---
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo="Aviso", mensaje="Especialidad actualizada exitosamente"
    )

    # La tabla se re-renderiza: refrescar el filtro para ver la fila editada
    buscador.clear()
    buscador.send_keys(DATOS_ESPECIALIDAD[1])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//*[@id='tabla-especialidades']//tr"
                f"[td[2][normalize-space(.)='{DATOS_ESPECIALIDAD[1]}']]",
            )
        )
    )
    assert DATOS_ESPECIALIDAD[2] in fila.text
    print(
        f"Especialidad modificada: {DATOS_ESPECIALIDAD[0]} -> {DATOS_ESPECIALIDAD[1]}"
        f" (feedback: {mensaje})"
    )
