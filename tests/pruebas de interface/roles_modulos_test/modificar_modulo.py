import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# [nombre_actual, nombre_nuevo]
# El campo nombre no admite espacios (regla sinEspacios del validador)
DATOS_MODULO = ["ModuloPrueba", "ModuloEditado"]


def test_modificar_modulo(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    driver.find_element(By.ID, "tab-modulos").click()
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-modulos']//tr[td[1][normalize-space(.)='{DATOS_MODULO[0]}']]",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='edit-modulo']").click()

    espera.until(EC.visibility_of_element_located((By.ID, "modal-admin-modulos")))
    nombre = driver.find_element(By.CSS_SELECTOR, "#form-modulo input[name='nombre']")
    nombre.clear()
    nombre.send_keys(DATOS_MODULO[1])
    driver.find_element(By.CSS_SELECTOR, "#form-modulo button[type='submit']").click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-admin-modulos")))
    espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-modulos']//tr[td[1][normalize-space(.)='{DATOS_MODULO[1]}']]",
            )
        )
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Modulo modificado: {DATOS_MODULO[0]} -> {DATOS_MODULO[1]}")
