import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_LOGIN = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/login"
TIEMPO_ESPERA = 10

# [usuario, contrasena]
# Credenciales que NO existen en la BD. Sin espacios (regla sinEspacios del
# formulario). Se asume ENTORNO_PRUEBA=true: el backend omite la validacion
# del reCAPTCHA. En produccion habria que resolver el captcha y enviar su token.
DATOS_LOGIN = ["usuario.inexistente", "clave_erronea"]


def test_credenciales_invalidas(driver):
    driver.get(URL_LOGIN)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Nota: el campo usuario limita a 15 caracteres, el valor queda truncado
    # pero sigue siendo un usuario inexistente.
    driver.find_element(By.ID, "login-nombre").send_keys(DATOS_LOGIN[0])
    driver.find_element(By.ID, "login-password").send_keys(DATOS_LOGIN[1])
    driver.find_element(
        By.CSS_SELECTOR, "#login-form button[type='submit']"
    ).click()

    # El JS de login (login.js) muestra el error del backend en su modal propio
    mensaje = espera.until(
        EC.visibility_of_element_located((By.ID, "feedback-login-message"))
    )
    assert "credenciales" in mensaje.text.lower()

    # No se redirige: seguimos en el login con el formulario presente
    espera.until(EC.presence_of_element_located((By.ID, "login-form")))
    assert "/login" in driver.current_url

    driver.find_element(
        By.CSS_SELECTOR, "#modal-feedback-login [data-close-modal]"
    ).click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-feedback-login")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Error mostrado por credenciales invalidas: {mensaje.text}")
