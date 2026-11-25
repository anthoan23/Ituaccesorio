import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, esperar_feedback

URL_CARGOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/cargos"
TIEMPO_ESPERA = 10

# [nombre, descripcion] - la cadena CRUD crea/modifica/elimina este registro
DATOS_CARGO = ["Cargo Interfaz", "Descripcion de cargo de interfaz"]


def test_crear_cargo(driver):
    driver.get(URL_CARGOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#tabla-cargos tr[data-id]")
        )
    )

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == "Ituaccesorio - Cargos"
    assert espera.until(
        lambda d: d.find_element(By.CSS_SELECTOR, ".cargos-hero__title").text
    ) == "Cargos"
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Cargos"
    # textContent (texto del DOM), porque el CSS renderiza los th en mayusculas
    encabezados = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, ".table thead th")
    ]
    assert encabezados == ["ID", "Nombre", "Descripción", "Acciones"]

    # --- Boton 'Registrar nuevo cargo': texto y estilo verde ---
    boton_registrar = driver.find_element(By.CSS_SELECTOR, "#form-cargo button[type='submit']")
    assert boton_registrar.text.strip() == "Registrar nuevo cargo"
    assert estilo_css(driver, boton_registrar, "borderTopColor") == "rgb(34, 197, 94)", (
        "El borde de 'Registrar nuevo cargo' deberia ser verde"
    )
    assert estilo_css(driver, boton_registrar, "color") == "rgb(34, 197, 94)", (
        "El texto de 'Registrar nuevo cargo' deberia ser verde"
    )

    driver.find_element(
        By.CSS_SELECTOR, "#form-cargo input[name='nombre_cargo']"
    ).send_keys(DATOS_CARGO[0])
    driver.find_element(
        By.CSS_SELECTOR, "#form-cargo textarea[name='descripcion_cargo']"
    ).send_keys(DATOS_CARGO[1])
    boton_registrar.click()

    # --- Feedback global de exito con el mensaje del servidor ---
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo="Aviso", mensaje="Cargo agregado exitosamente"
    )

    # --- Fila creada por el JS: filtrar para dejarla visible y verificarla ---
    buscador = driver.find_element(
        By.CSS_SELECTOR, ".cargos-table-card .table-controls__input"
    )
    buscador.send_keys(DATOS_CARGO[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-cargos']//tr[td[2][normalize-space(.)='{DATOS_CARGO[0]}']]",
            )
        )
    )
    assert DATOS_CARGO[1] in fila.text
    print(f"Cargo creado: {DATOS_CARGO[0]} (feedback: {mensaje})")
