import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Módulo de entregas: registrar personal de delivery (pestaña "Personal Delivery")
# Nota: la cédula del delivery debe existir como empleado registrado en la BD
# (los campos del modal son libres: cédula, nombre y apellido).
URL_ENTREGAS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/entregas"
TIEMPO_ESPERA = 10

# [cedula, nombre, apellido]
DATOS_PERSONAL = ["30124556", "Personal", "Delivery"]


def test_crear_personal_delivery(driver):
    driver.get(URL_ENTREGAS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # Cambiar a la pestaña Personal Delivery para acceder al botón de registro
    driver.find_element(By.ID, "tab-personal").click()
    driver.find_element(By.ID, "btn-nuevo-personal").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-personal")))
    driver.find_element(By.ID, "personal-cedula").send_keys(DATOS_PERSONAL[0])
    driver.find_element(By.ID, "personal-nombre").send_keys(DATOS_PERSONAL[1])
    driver.find_element(By.ID, "personal-apellido").send_keys(DATOS_PERSONAL[2])
    driver.find_element(
        By.CSS_SELECTOR, "#form-personal button[type='submit']"
    ).click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-personal")))
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-personal']//tr[td[1][contains(., '{DATOS_PERSONAL[0]}')]]",
            )
        )
    )
    assert DATOS_PERSONAL[1] in fila.text
    assert DATOS_PERSONAL[2] in fila.text
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Personal delivery creado: {DATOS_PERSONAL[1]} {DATOS_PERSONAL[2]} ({DATOS_PERSONAL[0]})"
    )
