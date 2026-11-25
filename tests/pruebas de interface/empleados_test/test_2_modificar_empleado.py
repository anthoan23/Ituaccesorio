import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_EMPLEADOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/empleados"
TIEMPO_ESPERA = 10

# [cedula, nombre_nuevo, celular] - el empleado que creo test_1_agregar_empleado
DATOS_EMPLEADO = ["12345679", "EmpleadoEditado", "04141234567"]


def test_modificar_empleado(driver):
    driver.get(URL_EMPLEADOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Filtrar por cedula para que la fila quede visible y clickeable
    buscador = driver.find_element(
        By.CSS_SELECTOR, ".empleados-table-card .table-controls__input"
    )
    buscador.send_keys(DATOS_EMPLEADO[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                f"#tabla-empleados tr[data-cedula='{DATOS_EMPLEADO[0]}']",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='editar']").click()

    # --- Al editar, el JS cambia el titulo y el texto del boton ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-registrar-empleado")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-registrar-empleado-title").text == (
        "Modificar empleado"
    )

    boton_guardar = driver.find_element(By.ID, "modal-submit-btn")
    assert boton_guardar.text.strip() == "Actualizar empleado"
    assert estilo_css(driver, boton_guardar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Actualizar empleado' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_guardar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Actualizar empleado' deberia ser oscuro"
    )

    nombre = driver.find_element(By.ID, "reg-nombre-empleado")
    nombre.clear()
    nombre.send_keys(DATOS_EMPLEADO[1])
    celular = driver.find_element(By.ID, "reg-celular-empleado")
    celular.clear()
    celular.send_keys(DATOS_EMPLEADO[2])
    boton_guardar.click()

    espera.until(
        EC.invisibility_of_element_located((By.ID, "modal-registrar-empleado"))
    )

    # --- Feedback global de exito con el mensaje del servidor ---
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo="Aviso", mensaje="Empleado actualizado exitosamente"
    )

    # La tabla se re-renderiza: refrescar el filtro para ver la fila editada
    buscador.clear()
    buscador.send_keys(DATOS_EMPLEADO[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-empleados']/tr[@data-cedula='{DATOS_EMPLEADO[0]}']"
                f"[contains(., '{DATOS_EMPLEADO[1]}')]",
            )
        )
    )
    assert DATOS_EMPLEADO[1] in fila.text
    print(f"Empleado modificado: {DATOS_EMPLEADO[0]} (feedback: {mensaje})")
