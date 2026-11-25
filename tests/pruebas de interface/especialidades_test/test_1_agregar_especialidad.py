import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, esperar_feedback

URL_ESPECIALIDADES = (
    f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/especialidades"
)
TIEMPO_ESPERA = 10

# [nombre, descripcion] - la cadena CRUD crea/modifica/elimina este registro
DATOS_ESPECIALIDAD = [
    "Especialidad Interfaz",
    "Descripcion de especialidad de interfaz",
]


def test_crear_especialidad(driver):
    driver.get(URL_ESPECIALIDADES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#tabla-especialidades tr[data-id]")
        )
    )

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == "Ituaccesorio - Especialidades"
    assert espera.until(
        lambda d: d.find_element(By.CSS_SELECTOR, ".especialidades-hero__title").text
    ) == "Especialidades"
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Especialidades"
    # textContent (texto del DOM), porque el CSS renderiza los th en mayusculas
    encabezados = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, ".table thead th")
    ]
    assert encabezados == ["ID", "Nombre", "Descripción", "Acciones"]

    # --- Boton 'Registrar especialidad': texto y estilo verde ---
    boton_registrar = driver.find_element(
        By.CSS_SELECTOR, "#form-especialidad button[type='submit']"
    )
    assert boton_registrar.text.strip() == "Registrar especialidad"
    assert estilo_css(driver, boton_registrar, "borderTopColor") == "rgb(34, 197, 94)", (
        "El borde de 'Registrar especialidad' deberia ser verde"
    )
    assert estilo_css(driver, boton_registrar, "color") == "rgb(34, 197, 94)", (
        "El texto de 'Registrar especialidad' deberia ser verde"
    )

    driver.find_element(
        By.CSS_SELECTOR, "#form-especialidad input[name='nombre_especialidad']"
    ).send_keys(DATOS_ESPECIALIDAD[0])
    driver.find_element(
        By.CSS_SELECTOR, "#form-especialidad textarea[name='descripcion_especialidad']"
    ).send_keys(DATOS_ESPECIALIDAD[1])
    boton_registrar.click()

    # --- Feedback global de exito con el mensaje del servidor ---
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo="Aviso", mensaje="Especialidad agregada exitosamente"
    )

    # --- Fila creada por el JS: filtrar para dejarla visible y verificarla ---
    buscador = driver.find_element(
        By.CSS_SELECTOR, ".especialidades-table-card .table-controls__input"
    )
    buscador.send_keys(DATOS_ESPECIALIDAD[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//*[@id='tabla-especialidades']//tr"
                f"[td[2][normalize-space(.)='{DATOS_ESPECIALIDAD[0]}']]",
            )
        )
    )
    assert DATOS_ESPECIALIDAD[1] in fila.text
    print(f"Especialidad creada: {DATOS_ESPECIALIDAD[0]} (feedback: {mensaje})")
