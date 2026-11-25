import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

URL_BASE = os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')
URL_LOGIN = f"{URL_BASE}/login"
URL_INICIO = f"{URL_BASE}/"
TIEMPO_ESPERA = 10

# [usuario, contrasena]
# Credenciales que deben existir en la BD de la app (ajustar si difieren).
# Se asume ENTORNO_PRUEBA=true: el backend omite la validacion del reCAPTCHA.
# En produccion habria que resolver el captcha de Google y enviar su token.
DATOS_LOGIN = ["admin", "admin123"]


def test_iniciar_sesion(driver):
    driver.get(URL_LOGIN)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificaciones visuales de la pagina de login ---
    assert driver.title == "Login | Ituaccesorio"
    assert driver.find_element(By.CSS_SELECTOR, ".phone__title").text == "BIENVENIDO"
    assert driver.find_element(By.ID, "login-nombre").get_attribute("placeholder") == "Email / Usuario"
    assert driver.find_element(By.ID, "login-password").get_attribute("placeholder") == "Contraseña"

    # En modo prueba el reCAPTCHA queda oculto (lo esconde el propio login.js)
    assert not driver.find_element(By.CSS_SELECTOR, ".phone__captcha-wrapper").is_displayed(), (
        "El captcha deberia estar oculto en modo prueba"
    )

    # --- Boton 'INICIAR SESIÓN': fondo degradado amarillo (fondo plano no hay) ---
    boton_login = driver.find_element(By.CSS_SELECTOR, "#login-form button[type='submit']")
    assert boton_login.text.strip() == "INICIAR SESIÓN"
    quitar_hover(driver)
    assert "linear-gradient" in estilo_css(driver, boton_login, "backgroundImage"), (
        "El fondo de 'INICIAR SESIÓN' deberia ser el degradado amarillo del tema"
    )
    assert driver.find_element(By.CSS_SELECTOR, ".phone__link--button").text.strip() == (
        "Crear una Cuenta Nueva"
    )

    driver.find_element(By.ID, "login-nombre").send_keys(DATOS_LOGIN[0])
    driver.find_element(By.ID, "login-password").send_keys(DATOS_LOGIN[1])
    boton_login.click()

    # El JS de login (login.js) redirige a "/" tras el exito: dashboard del admin
    espera.until(EC.not_(EC.url_contains("/login")))
    espera.until(EC.url_to_be(URL_INICIO))
    espera.until(EC.title_is("iTuAccesorio - Dashboard"))

    # Se salio de la pagina de login: el formulario ya no esta visible
    espera.until(EC.invisibility_of_element_located((By.ID, "login-form")))
    print(f"Sesion iniciada como: {DATOS_LOGIN[0]}")
