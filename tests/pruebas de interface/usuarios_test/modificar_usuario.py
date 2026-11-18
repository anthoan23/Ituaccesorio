import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# [nombre_actual, nombre_nuevo]
DATOS_USUARIO = ["Usuario Prueba", "Usuario Prueba Editado"]


def test_modificar_usuario(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-usuarios']//tr[td[2][normalize-space(.)='{DATOS_USUARIO[0]}']]",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='edit-usuario']").click()

    espera.until(EC.visibility_of_element_located((By.ID, "modal-admin-usuarios")))
    # El llenado del formulario es asincrono (carga la cedula segun el rol);
    # se espera la opcion de cedula seleccionada antes de editar
    espera.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "#form-usuario select[name='cedula_personal'] option[value]:not([value=''])[selected]",
            )
        )
    )
    nombre = driver.find_element(By.CSS_SELECTOR, "#form-usuario input[name='nombre']")
    nombre.clear()
    nombre.send_keys(DATOS_USUARIO[1])
    driver.find_element(By.CSS_SELECTOR, "#form-usuario button[type='submit']").click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-admin-usuarios")))
    espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-usuarios']//tr[td[2][normalize-space(.)='{DATOS_USUARIO[1]}']]",
            )
        )
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Usuario modificado: {DATOS_USUARIO[0]} -> {DATOS_USUARIO[1]}")
