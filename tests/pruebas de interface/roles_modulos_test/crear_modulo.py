import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# [nombre, descripcion]
# El campo nombre no admite espacios (regla sinEspacios del validador), por eso
# el nombre de prueba va sin espacio
DATOS_MODULO = ["ModuloPrueba", "Modulo de prueba de interface"]


def test_crear_modulo(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-usuarios tr")))

    # Los modulos viven en la pestaña "Modulos" de la vista de usuarios
    driver.find_element(By.ID, "tab-modulos").click()
    driver.find_element(By.ID, "btn-admin-modulos").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-admin-modulos")))

    driver.find_element(
        By.CSS_SELECTOR, "#form-modulo input[name='nombre']"
    ).send_keys(DATOS_MODULO[0])
    driver.find_element(
        By.CSS_SELECTOR, "#form-modulo textarea[name='descripcion']"
    ).send_keys(DATOS_MODULO[1])
    driver.find_element(By.CSS_SELECTOR, "#form-modulo button[type='submit']").click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-admin-modulos")))
    # La columna 1 de la tabla de modulos es el nombre y la 2 la descripcion
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-modulos']//tr[td[1][normalize-space(.)='{DATOS_MODULO[0]}']]",
            )
        )
    )
    assert DATOS_MODULO[1] in fila.text
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Modulo creado: {DATOS_MODULO[0]}")
