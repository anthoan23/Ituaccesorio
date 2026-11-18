import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# [nombre]
DATOS_USUARIO = ["Usuario Prueba"]


def test_consultar_usuario(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # La tabla de usuarios no tiene boton de detalle; se consultan los datos
    # directamente de la fila
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-usuarios']//tr[td[2][normalize-space(.)='{DATOS_USUARIO[0]}']]",
            )
        )
    )

    nombre = fila.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
    cedula = fila.find_element(By.CSS_SELECTOR, "td:nth-child(3)").text
    rol = fila.find_element(By.CSS_SELECTOR, "td:nth-child(4)").text
    assert nombre == DATOS_USUARIO[0]
    assert cedula.strip() != ""
    assert rol.strip() != ""
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Usuario consultado: {nombre} - cedula {cedula} - rol {rol}")
