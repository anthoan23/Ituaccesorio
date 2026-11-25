import os
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def guardar_captura(driver, nombre="error"):
    os.makedirs("tests/pruebas de interface/evidencia", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = os.path.join("tests/pruebas de interface/evidencia", f"{nombre}_{timestamp}.png")
    try:
        driver.save_screenshot(ruta)
        print(f"Captura guardada en: {ruta}")
    except Exception as e:
        print(f"No se pudo guardar la captura: {e}")
    return ruta


def estilo_css(driver, elemento, propiedad):
    """Devuelve el valor computado de una propiedad CSS (camelCase, ej. 'color'
    o 'backgroundColor') tal como lo pinta el navegador, para compararlo directo
    contra el rgb/rgba esperado."""
    return driver.execute_script(
        "return getComputedStyle(arguments[0])[arguments[1]];",
        elemento,
        propiedad,
    )


def quitar_hover(driver):
    """Aparca el puntero en la esquina superior izquierda de la pagina para
    que ningun boton quede en estado :hover al verificar sus colores."""
    from selenium.webdriver.common.action_chains import ActionChains

    ActionChains(driver).move_to_element_with_offset(
        driver.find_element(By.TAG_NAME, "body"), 0, 0
    ).perform()


def esperar_feedback(espera, tipo="success", titulo="Aviso", mensaje=None):
    """Espera el modal global de feedback, valida lo que muestra y espera su
    autocierre (feedback-modal.js cierra el modal solo):
    - que el icono del tipo esperado (success/error) sea el visible,
    - el titulo (por defecto 'Aviso', los modulos usan FeedbackModal.show),
    - que el mensaje contenga el texto indicado (si se pasa).

    Devuelve (titulo, mensaje) mostrados."""
    espera.until(EC.visibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, f"#feedback-modal [data-feedback-icon='{tipo}']")
        )
    )
    titulo_mostrado = espera.until(
        lambda d: d.find_element(By.ID, "feedback-modal-title").text.strip() or False
    )
    texto = espera.until(
        lambda d: d.find_element(By.ID, "feedback-modal-message").text.strip() or False
    )
    if titulo is not None:
        assert titulo_mostrado == titulo, (
            f"Titulo de feedback inesperado: '{titulo_mostrado}' (se esperaba '{titulo}')"
        )
    if mensaje is not None:
        assert mensaje in texto, (
            f"Mensaje de feedback inesperado: '{texto}' (se esperaba '{mensaje}')"
        )
    # El modal se cierra solo; esperamos el cierre para no pisar la siguiente prueba.
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    return titulo_mostrado, texto
