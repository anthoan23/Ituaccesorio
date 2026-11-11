from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_EMPLEADOS = "http://127.0.0.1:5000/empleados"
TIEMPO_ESPERA = 10

# [cedula]
DATOS_EMPLEADO = ["12345678"]


def test_eliminar_empleado(driver):
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
    fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']").click()

    espera.until(EC.visibility_of_element_located((By.ID, "modal-eliminar-empleado")))
    driver.find_element(By.ID, "btn-confirmar-eliminar-empleado").click()

    espera.until(
        EC.invisibility_of_element_located((By.ID, "modal-eliminar-empleado"))
    )
    espera.until(
        EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, f"#tabla-empleados tr[data-cedula='{DATOS_EMPLEADO[0]}']")
        )
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Empleado eliminado: {DATOS_EMPLEADO[0]}")
