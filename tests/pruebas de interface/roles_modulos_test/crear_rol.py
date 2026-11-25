import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# [nombre, descripcion]
DATOS_ROL = ["Rol Prueba", "Rol de prueba de interface"]


def test_crear_rol(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-usuarios tr")))

    # Los roles viven en la pestaña "Roles" de la vista de usuarios
    driver.find_element(By.ID, "tab-roles").click()
    driver.find_element(By.ID, "btn-admin-roles").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-admin-roles")))

    driver.find_element(
        By.CSS_SELECTOR, "#form-rol input[name='nombre']"
    ).send_keys(DATOS_ROL[0])
    driver.find_element(
        By.CSS_SELECTOR, "#form-rol textarea[name='descripcion']"
    ).send_keys(DATOS_ROL[1])
    driver.find_element(By.CSS_SELECTOR, "#form-rol button[type='submit']").click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-admin-roles")))
    # La columna 1 de la tabla de roles es el nombre y la 2 la descripcion
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-roles']//tr[td[1][normalize-space(.)='{DATOS_ROL[0]}']]",
            )
        )
    )
    assert DATOS_ROL[1] in fila.text
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Rol creado: {DATOS_ROL[0]}")
