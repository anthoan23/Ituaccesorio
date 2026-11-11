from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_EMPLEADOS = "http://127.0.0.1:5000/empleados"
TIEMPO_ESPERA = 10

# [cedula]
DATOS_EMPLEADO = ["12345678"]


def test_consultar_empleado(driver):
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
    fila.find_element(By.CSS_SELECTOR, "button[data-action='ver']").click()

    espera.until(EC.visibility_of_element_located((By.ID, "modal-ver-empleado")))
    detalle_cedula = driver.find_element(By.ID, "detalle-cedula").text
    detalle_nombre = driver.find_element(By.ID, "detalle-nombre-completo").text
    assert detalle_cedula == DATOS_EMPLEADO[0]
    driver.find_element(
        By.CSS_SELECTOR, "#modal-ver-empleado [data-close-modal]"
    ).click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-ver-empleado")))
    print(f"Empleado consultado: {detalle_cedula} - {detalle_nombre}")
