import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Módulo de entregas: modificar personal de delivery (pestaña "Personal Delivery")
# Requiere el registro creado por crear_personal_delivery.py
# ("Personal Delivery", cédula 30124556).
URL_ENTREGAS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/entregas"
TIEMPO_ESPERA = 10

# [nombre_actual, nombre_nuevo]
DATOS_PERSONAL = ["Personal Delivery", "Personal Editado"]


def test_modificar_personal_delivery(driver):
    driver.get(URL_ENTREGAS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # Cambiar a la pestaña Personal Delivery
    driver.find_element(By.ID, "tab-personal").click()
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-personal']//tr[td[2][normalize-space(.)='{DATOS_PERSONAL[0]}']]",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='editar-personal']").click()

    espera.until(EC.visibility_of_element_located((By.ID, "modal-personal")))
    # La cédula llega deshabilitada en edición; solo se cambia el nombre
    nombre = driver.find_element(By.ID, "personal-nombre")
    nombre.clear()
    nombre.send_keys(DATOS_PERSONAL[1])
    driver.find_element(
        By.CSS_SELECTOR, "#form-personal button[type='submit']"
    ).click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-personal")))
    espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-personal']//tr[td[2][normalize-space(.)='{DATOS_PERSONAL[1]}']]",
            )
        )
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Personal delivery modificado: {DATOS_PERSONAL[0]} -> {DATOS_PERSONAL[1]}")
