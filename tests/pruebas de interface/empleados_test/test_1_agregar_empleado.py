import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_EMPLEADOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/empleados"
TIEMPO_ESPERA = 10

# [cedula, nombre, apellido, celular, correo, direccion, cargo]
DATOS_EMPLEADO = [
    "12345679",
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
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == "Ituaccesorio - Empleados"
    assert espera.until(
        lambda d: d.find_element(By.CSS_SELECTOR, ".empleados-hero__title").text
    ) == "Empleados"
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Empleados"
    # textContent (texto del DOM), porque el CSS renderiza los th en mayusculas
    encabezados = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, ".table thead th")
    ]
    assert encabezados == ["Cédula", "Nombre", "Apellido", "Cargo", "Acciones"]

    # --- Boton 'Nuevo Empleado': texto y estilo verde ---
    boton_nuevo = espera.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '[data-open-modal="modal-registrar-empleado"]')
        )
    )
    assert boton_nuevo.text.strip() == "Nuevo Empleado"
    assert estilo_css(driver, boton_nuevo, "borderTopColor") == "rgb(34, 197, 94)", (
        "El borde de 'Nuevo Empleado' deberia ser verde"
    )
    assert estilo_css(driver, boton_nuevo, "color") == "rgb(34, 197, 94)", (
        "El texto de 'Nuevo Empleado' deberia ser verde"
    )
    boton_nuevo.click()

    # --- Modal 'Registrar nuevo empleado': titulo y campos ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-registrar-empleado")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-registrar-empleado-title").text == (
        "Registrar nuevo empleado"
    )
    labels = [
        span.get_attribute("textContent").strip()
        for span in driver.find_elements(By.CSS_SELECTOR, "#form-registrar-empleado label > span")
    ]
    assert labels[:5] == ["Cédula *", "Nombre *", "Apellido *", "Cargo *", "Celular *"]

    espera.until(
        lambda navegador: len(
            Select(navegador.find_element(By.ID, "reg-cargo-empleado")).options
        )
        > 1
    )

    # --- Boton 'Guardar empleado': fondo amarillo con texto oscuro ---
    boton_guardar = driver.find_element(By.ID, "modal-submit-btn")
    assert boton_guardar.text.strip() == "Guardar empleado"
    assert estilo_css(driver, boton_guardar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Guardar empleado' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_guardar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Guardar empleado' deberia ser oscuro"
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
    boton_guardar.click()

    espera.until(
        EC.invisibility_of_element_located((By.ID, "modal-registrar-empleado"))
    )

    # --- Feedback global de exito con el mensaje del servidor ---
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo="Aviso", mensaje="Empleado agregado exitosamente"
    )

    # --- Fila creada por el JS: filtrar para dejarla visible y verificarla ---
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
    assert DATOS_EMPLEADO[1] in fila.text

    boton_editar = fila.find_element(By.CSS_SELECTOR, "button[data-action='editar']")
    boton_ver = fila.find_element(By.CSS_SELECTOR, "button[data-action='ver']")
    boton_eliminar = fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']")
    assert boton_editar.get_attribute("aria-label") == "Modificar"
    assert boton_ver.get_attribute("aria-label") == "Ver"
    assert boton_eliminar.get_attribute("aria-label") == "Eliminar"
    assert estilo_css(driver, boton_editar, "borderTopColor") == "rgb(243, 197, 0)", (
        "El borde de editar deberia ser amarillo"
    )
    assert estilo_css(driver, boton_ver, "borderTopColor") == "rgb(0, 122, 255)", (
        "El borde de ver deberia ser azul"
    )
    assert estilo_css(driver, boton_eliminar, "borderTopColor") == "rgb(220, 38, 38)", (
        "El borde de eliminar deberia ser rojo"
    )
    svg_editar = boton_editar.find_element(By.TAG_NAME, "svg")
    svg_ver = boton_ver.find_element(By.TAG_NAME, "svg")
    svg_eliminar = boton_eliminar.find_element(By.TAG_NAME, "svg")
    assert estilo_css(driver, svg_editar, "color") == "rgb(243, 197, 0)", (
        "El icono de editar deberia ser amarillo"
    )
    assert estilo_css(driver, svg_ver, "color") == "rgb(0, 122, 255)", (
        "El icono de ver deberia ser azul"
    )
    assert estilo_css(driver, svg_eliminar, "color") == "rgb(220, 38, 38)", (
        "El icono de eliminar deberia ser rojo"
    )
    print(f"Empleado creado: {DATOS_EMPLEADO[0]} (feedback: {mensaje})")
