import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

URL_LOGIN = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/login"
TIEMPO_ESPERA = 10

# [usuario, contrasena]
# Credenciales que NO existen en la BD. Sin espacios (regla sinEspacios del
# formulario). Se asume ENTORNO_PRUEBA=true: el backend omite la validacion
# del reCAPTCHA. En produccion habria que resolver el captcha y enviar su token.
DATOS_LOGIN = ["usuario.inexistente", "clave_erronea"]

# Mensaje exacto que devuelve el backend (app/controllers/login.py) con
# credenciales invalidas
MENSAJE_ERROR = "Credenciales inválidas."


def test_credenciales_invalidas(driver):
    driver.get(URL_LOGIN)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Nota: el campo usuario limita a 15 caracteres, el valor queda truncado
    # pero sigue siendo un usuario inexistente.
    assert driver.title == "Login | Ituaccesorio"
    driver.find_element(By.ID, "login-nombre").send_keys(DATOS_LOGIN[0])
    driver.find_element(By.ID, "login-password").send_keys(DATOS_LOGIN[1])
    driver.find_element(
        By.CSS_SELECTOR, "#login-form button[type='submit']"
    ).click()

    # El JS de login (login.js) muestra el error del backend en su modal propio
    # "Mensaje" (#modal-feedback-login), no en el FeedbackModal global
    espera.until(EC.visibility_of_element_located((By.ID, "modal-feedback-login")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-feedback-login-title").text == "Mensaje"
    mensaje = driver.find_element(By.ID, "feedback-login-message")
    assert mensaje.text == MENSAJE_ERROR, (
        f"Mensaje de error inesperado: '{mensaje.text}' (se esperaba '{MENSAJE_ERROR}')"
    )

    # Boton 'Aceptar' que cierra el modal: fondo amarillo con texto oscuro
    boton_aceptar = driver.find_element(
        By.CSS_SELECTOR, "#modal-feedback-login [data-close-modal]"
    )
    assert boton_aceptar.text.strip() == "Aceptar"
    assert estilo_css(driver, boton_aceptar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Aceptar' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_aceptar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Aceptar' deberia ser oscuro"
    )
    boton_aceptar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-feedback-login")))

    # No se redirige: seguimos en el login con el formulario presente
    espera.until(EC.presence_of_element_located((By.ID, "login-form")))
    assert "/login" in driver.current_url
    print(f"Error mostrado por credenciales invalidas: {MENSAJE_ERROR}")
