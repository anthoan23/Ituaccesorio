import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# [nombre_actual, nombre_nuevo]
DATOS_ROL = ["Rol Prueba", "Rol Editado"]


def test_modificar_rol(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    driver.find_element(By.ID, "tab-roles").click()
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-roles']//tr[td[1][normalize-space(.)='{DATOS_ROL[0]}']]",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='edit-rol']").click()

    espera.until(EC.visibility_of_element_located((By.ID, "modal-admin-roles")))
    nombre = driver.find_element(By.CSS_SELECTOR, "#form-rol input[name='nombre']")
    nombre.clear()
    nombre.send_keys(DATOS_ROL[1])
    driver.find_element(By.CSS_SELECTOR, "#form-rol button[type='submit']").click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-admin-roles")))
    espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-roles']//tr[td[1][normalize-space(.)='{DATOS_ROL[1]}']]",
            )
        )
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Rol modificado: {DATOS_ROL[0]} -> {DATOS_ROL[1]}")
