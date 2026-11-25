import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css

URL_EMPLEADOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/empleados"
TIEMPO_ESPERA = 10

# [cedula] - el empleado que creo/modifico la cadena de pruebas
DATOS_EMPLEADO = ["12345679"]


def test_consultar_empleado(driver):
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
    fila.find_element(By.CSS_SELECTOR, "button[data-action='ver']").click()

    # --- Modal 'Detalles del empleado': titulo, secciones y datos ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-ver-empleado")))
    assert driver.find_element(By.ID, "modal-ver-empleado-title").text == (
        "Detalles del empleado"
    )
    # textContent (texto del DOM), porque el CSS renderiza las etiquetas en mayusculas
    etiquetas = [
        label.get_attribute("textContent").strip()
        for label in driver.find_elements(
            By.CSS_SELECTOR, "#modal-ver-empleado .detalle-item label"
        )
    ]
    assert etiquetas == [
        "Cédula",
        "Nombre completo",
        "Cargo",
        "Celular",
        "Correo electrónico",
        "Dirección",
        "Especialidades",
    ]

    detalle_cedula = driver.find_element(By.ID, "detalle-cedula").text
    detalle_nombre = driver.find_element(By.ID, "detalle-nombre-completo").text
    assert detalle_cedula == DATOS_EMPLEADO[0]
    assert detalle_nombre.strip(), "El nombre completo del empleado llego vacio"

    # --- Boton 'Cerrar': estilo fantasma (ghost, colores del tema oscuro) ---
    boton_cerrar = driver.find_element(
        By.CSS_SELECTOR, "#modal-ver-empleado .ui-form__actions [data-close-modal]"
    )
    assert boton_cerrar.text.strip() == "Cerrar"
    assert "ui-btn--ghost" in boton_cerrar.get_attribute("class")
    assert estilo_css(driver, boton_cerrar, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Cerrar' deberia ser el ghost del tema oscuro"
    assert estilo_css(driver, boton_cerrar, "color") == "rgb(255, 255, 255)", (
        "El texto de 'Cerrar' deberia ser blanco"
    )

    boton_cerrar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-ver-empleado")))
    print(f"Empleado consultado: {detalle_cedula} - {detalle_nombre}")
