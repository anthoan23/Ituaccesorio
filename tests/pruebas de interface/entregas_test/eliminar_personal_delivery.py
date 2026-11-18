import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Módulo de entregas: eliminar personal de delivery (pestaña "Personal Delivery")
# Requiere el registro editado por modificar_personal_delivery.py
# ("Personal Editado", cédula 30124556).
URL_ENTREGAS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/entregas"
TIEMPO_ESPERA = 10

# [nombre_completo]
DATOS_PERSONAL = ["Personal Editado"]


def test_eliminar_personal_delivery(driver):
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
    fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar-personal']").click()

    espera.until(EC.visibility_of_element_located((By.ID, "modal-eliminar")))
    driver.find_element(By.ID, "btn-confirmar-eliminar").click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-eliminar")))
    espera.until(
        EC.invisibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-personal']//tr[td[2][normalize-space(.)='{DATOS_PERSONAL[0]}']]",
            )
        )
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Personal delivery eliminado: {DATOS_PERSONAL[0]}")
