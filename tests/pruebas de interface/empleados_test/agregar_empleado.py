from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

URL_EMPLEADOS = "http://127.0.0.1:5001/empleados"
TIEMPO_ESPERA = 10

# [cedula, nombre, apellido, celular, correo, direccion, cargo]
DATOS_EMPLEADO = [
    "12345678",
    "Empleado",
    "Prueba",
    "04141234567",
    "empleado.prueba@example.com",
    "Barquisimeto",
    "Técnico",
]


def test_crear_empleado(driver):
    driver.get(URL_EMPLEADOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '[data-open-modal="modal-registrar-empleado"]')
        )
    ).click()
    espera.until(
        EC.visibility_of_element_located((By.ID, "modal-registrar-empleado"))
    )
    espera.until(
        lambda navegador: len(
            Select(navegador.find_element(By.ID, "reg-cargo-empleado")).options
        )
        > 1
    )

    driver.find_element(By.ID, "reg-cedula-empleado").send_keys(DATOS_EMPLEADO[0])
    driver.find_element(By.ID, "reg-nombre-empleado").send_keys(DATOS_EMPLEADO[1])
    driver.find_element(By.ID, "reg-apellido-empleado").send_keys(DATOS_EMPLEADO[2])
    driver.find_element(By.ID, "reg-celular-empleado").send_keys(DATOS_EMPLEADO[3])
    driver.find_element(By.ID, "reg-correo-empleado").send_keys(DATOS_EMPLEADO[4])
    driver.find_element(By.ID, "reg-direccion-empleado").send_keys(DATOS_EMPLEADO[5])
    Select(driver.find_element(By.ID, "reg-cargo-empleado")).select_by_visible_text(
        DATOS_EMPLEADO[6]
    )
    driver.find_element(By.ID, "modal-submit-btn").click()

    espera.until(
        EC.invisibility_of_element_located((By.ID, "modal-registrar-empleado"))
    )
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                f"#tabla-empleados tr[data-cedula='{DATOS_EMPLEADO[0]}']",
            )
        )
    )
    assert DATOS_EMPLEADO[1] in fila.text
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Empleado creado: {DATOS_EMPLEADO[0]}")
