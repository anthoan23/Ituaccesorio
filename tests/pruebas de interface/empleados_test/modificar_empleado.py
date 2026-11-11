from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_EMPLEADOS = "http://127.0.0.1:5000/empleados"
TIEMPO_ESPERA = 10

# [cedula, nombre_nuevo, celular]
DATOS_EMPLEADO = ["12345678", "EmpleadoEditado", "04141234567"]


def test_modificar_empleado(driver):
    driver.get(URL_EMPLEADOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                f"#tabla-empleados tr[data-cedula='{DATOS_EMPLEADO[0]}']",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='editar']").click()

    espera.until(
        EC.visibility_of_element_located((By.ID, "modal-registrar-empleado"))
    )
    nombre = driver.find_element(By.ID, "reg-nombre-empleado")
    nombre.clear()
    nombre.send_keys(DATOS_EMPLEADO[1])
    celular = driver.find_element(By.ID, "reg-celular-empleado")
    celular.clear()
    celular.send_keys(DATOS_EMPLEADO[2])
    driver.find_element(By.ID, "modal-submit-btn").click()

    espera.until(
        EC.invisibility_of_element_located((By.ID, "modal-registrar-empleado"))
    )
    espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-empleados']/tr[@data-cedula='{DATOS_EMPLEADO[0]}']"
                f"[contains(., '{DATOS_EMPLEADO[1]}')]",
            )
        )
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Empleado modificado: {DATOS_EMPLEADO[0]}")
