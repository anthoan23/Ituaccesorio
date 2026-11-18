import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_BASE = os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')
URL_LOGIN = f"{URL_BASE}/login"
URL_INICIO = f"{URL_BASE}/"
TIEMPO_ESPERA = 10

# [usuario, contrasena]
# Credenciales que deben existir en la BD de la app (ajustar si difieren).
# Se asume ENTORNO_PRUEBA=true: el backend omite la validacion del reCAPTCHA.
# En produccion habria que resolver el captcha de Google y enviar su token.
DATOS_LOGIN = ["admin", "admin123"]


def test_cerrar_sesion(driver):
    driver.get(URL_LOGIN)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Flujo minimo de inicio de sesion dentro del propio test
    driver.find_element(By.ID, "login-nombre").send_keys(DATOS_LOGIN[0])
    driver.find_element(By.ID, "login-password").send_keys(DATOS_LOGIN[1])
    driver.find_element(
        By.CSS_SELECTOR, "#login-form button[type='submit']"
    ).click()
    espera.until(EC.not_(EC.url_contains("/login")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Cierre de sesion por la UI: boton del navbar con formulario GET /logout
    boton_logout = espera.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".drawer__logout"))
    )
    boton_logout.click()

    # El logout redirige de vuelta a la pagina de login
    espera.until(EC.url_to_be(URL_LOGIN))
    espera.until(EC.presence_of_element_located((By.ID, "login-form")))
    print("Sesion cerrada: redirigido a la pagina de login")
