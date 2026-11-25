import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# [nombre] - el usuario que la cadena creo/modifico y aqui elimina
DATOS_USUARIO = ["Usuario Interfaz Editado"]


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


def test_eliminar_usuario(driver):
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
    fila.find_element(By.CSS_SELECTOR, "button[data-action='delete-usuario']").click()

    # --- Modal de confirmacion: titulo, texto dinamico y estilos de los botones ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-confirmacion")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-confirmacion-title").text == (
        "Confirmar acción"
    )
    # El texto de confirmacion es dinamico: incluye el nombre del usuario
    mensaje = driver.find_element(By.ID, "confirmacion-mensaje").text
    assert mensaje == (
        f"¿Seguro que desea eliminar el usuario {DATOS_USUARIO[0]}? "
        "Esta acción no se puede deshacer."
    ), f"El texto de confirmacion no menciona al usuario: '{mensaje}'"

    boton_confirmar = driver.find_element(By.ID, "confirmacion-btn")
    assert boton_confirmar.text.strip() == "Confirmar"
    assert "ui-btn--danger" in boton_confirmar.get_attribute("class")
    assert estilo_css(driver, boton_confirmar, "color") == "rgb(239, 68, 68)", (
        "El texto de 'Confirmar' deberia ser el rojo de peligro del tema"
    )
    assert estilo_css(driver, boton_confirmar, "backgroundColor") == (
        "rgba(220, 38, 38, 0.2)"
    ), "El fondo de 'Confirmar' deberia ser rojo tenue"

    boton_cancelar = driver.find_element(
        By.CSS_SELECTOR, "#modal-confirmacion .ui-form__actions [data-close-modal]"
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

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-confirmacion")))

    # --- Toast propio del modulo con el mensaje generico del JS ---
    esperar_toast(espera, "Registro eliminado.")

    espera.until(
        EC.invisibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-usuarios']//tr[td[2][normalize-space(.)='{DATOS_USUARIO[0]}']]",
            )
        )
    )
    # El interceptor global de fetch tambien abre el FeedbackModal generico
    # (titulo 'Acción exitosa'); esperar su autocierre para no pisar la cadena.
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Usuario eliminado: {DATOS_USUARIO[0]} (toast: 'Registro eliminado.')")
