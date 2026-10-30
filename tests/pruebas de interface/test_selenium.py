import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

URL_EMPLEADOS = "http://127.0.0.1:5000/empleados"
TIEMPO_ESPERA = 10


def crear_empleado(driver, cedula):
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

    driver.find_element(By.ID, "reg-cedula-empleado").send_keys(cedula)
    driver.find_element(By.ID, "reg-nombre-empleado").send_keys("Empleado")
    driver.find_element(By.ID, "reg-apellido-empleado").send_keys("Prueba")
    driver.find_element(By.ID, "reg-celular-empleado").send_keys("0414123456")
    driver.find_element(By.ID, "reg-correo-empleado").send_keys(
        "empleado.prueba@example.com"
    )
    driver.find_element(By.ID, "reg-direccion-empleado").send_keys("Barquisimeto")
    Select(driver.find_element(By.ID, "reg-cargo-empleado")).select_by_visible_text(
        "Técnico"
    )
    driver.find_element(By.ID, "modal-submit-btn").click()

    espera.until(
        EC.invisibility_of_element_located((By.ID, "modal-registrar-empleado"))
    )
    fila = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, f"#tabla-empleados tr[data-cedula='{cedula}']")
        )
    )
    assert "Empleado" in fila.text
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Empleado creado: {cedula}")


def modificar_empleado(driver, cedula):
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, f"#tabla-empleados tr[data-cedula='{cedula}']")
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='editar']").click()

    espera.until(
        EC.visibility_of_element_located((By.ID, "modal-registrar-empleado"))
    )
    nombre = driver.find_element(By.ID, "reg-nombre-empleado")
    nombre.clear()
    nombre.send_keys("EmpleadoEditado")
    celular = driver.find_element(By.ID, "reg-celular-empleado")
    celular.clear()
    celular.send_keys("0414123456")
    driver.find_element(By.ID, "modal-submit-btn").click()

    espera.until(
        EC.invisibility_of_element_located((By.ID, "modal-registrar-empleado"))
    )
    espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-empleados']/tr[@data-cedula='{cedula}'][contains(., 'EmpleadoEditado')]",
            )
        )
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Empleado modificado: {cedula}")


def consultar_empleado(driver, cedula):
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, f"#tabla-empleados tr[data-cedula='{cedula}']")
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='ver']").click()

    espera.until(EC.visibility_of_element_located((By.ID, "modal-ver-empleado")))
    detalle_cedula = driver.find_element(By.ID, "detalle-cedula").text
    detalle_nombre = driver.find_element(By.ID, "detalle-nombre-completo").text
    assert detalle_cedula == cedula
    driver.find_element(
        By.CSS_SELECTOR, "#modal-ver-empleado [data-close-modal]"
    ).click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-ver-empleado")))
    print(f"Empleado consultado: {detalle_cedula} - {detalle_nombre}")


def eliminar_empleado(driver, cedula):
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, f"#tabla-empleados tr[data-cedula='{cedula}']")
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
            (By.CSS_SELECTOR, f"#tabla-empleados tr[data-cedula='{cedula}']")
        )
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Empleado eliminado: {cedula}")


def main():
    driver = webdriver.Firefox()
    cedula = str(random.randint(10000000, 99999999))
    try:
        driver.get(URL_EMPLEADOS)
        crear_empleado(driver, cedula)
        modificar_empleado(driver, cedula)
        consultar_empleado(driver, cedula)
        eliminar_empleado(driver, cedula)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
