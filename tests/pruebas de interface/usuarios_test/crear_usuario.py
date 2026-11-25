import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# [nombre, password]
# La cedula y el rol se eligen de los selects del formulario (no son datos fijos)
DATOS_USUARIO = ["Usuario Prueba", "clave12345"]


def test_crear_usuario(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-usuarios tr")))

    driver.find_element(By.ID, "btn-admin-usuarios").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-admin-usuarios")))

    # El select de roles se llena al cargar la pagina (opcion 1 = primer rol real)
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#form-usuario select[name='rol_id'] option:nth-child(2)")
        )
    )
    Select(driver.find_element(By.CSS_SELECTOR, "#form-usuario select[name='rol_id']")).select_by_index(1)

    # El select de cedula solo se llena despues de elegir un rol; se toma la
    # primera opcion disponible (indice 0 = "Seleccione un empleado/cliente...")
    espera.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "#form-usuario select[name='cedula_personal'] option[value]:not([value=''])",
            )
        )
    )
    Select(driver.find_element(By.CSS_SELECTOR, "#form-usuario select[name='cedula_personal']")).select_by_index(1)

    driver.find_element(
        By.CSS_SELECTOR, "#form-usuario input[name='nombre']"
    ).send_keys(DATOS_USUARIO[0])
    driver.find_element(
        By.CSS_SELECTOR, "#form-usuario input[name='password']"
    ).send_keys(DATOS_USUARIO[1])
    driver.find_element(By.CSS_SELECTOR, "#form-usuario button[type='submit']").click()

    # La columna 2 de la tabla es el nombre del usuario y la 4 el rol asignado
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-usuarios']//tr[td[2][normalize-space(.)='{DATOS_USUARIO[0]}']]",
            )
        )
    )
    assert fila.find_element(By.CSS_SELECTOR, "td:nth-child(4)").text.strip() != ""
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Usuario creado: {DATOS_USUARIO[0]}")
