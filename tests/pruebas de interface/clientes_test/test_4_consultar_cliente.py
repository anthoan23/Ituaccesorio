import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css

URL_CLIENTES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/clientes"
TIEMPO_ESPERA = 10

# [cedula, nombre, apellido_editado, celular, correo, direccion]
# El cliente que la cadena creo y modifico en los tests anteriores
DATOS_CLIENTE = [
    "71234567",
    "Cliente",
    "Interfaz Editado",
    "04141234777",
    "cliente.interfaz@ituaccesorio.com",
    "Barquisimeto",
]


def test_consultar_cliente(driver):
    driver.get(URL_CLIENTES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Filtrar por cedula para que la fila quede visible y clickeable
    buscador = driver.find_element(
        By.CSS_SELECTOR, ".clientes-table-card .table-controls__input"
    )
    buscador.send_keys(DATOS_CLIENTE[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-clientes']//tr[td[1][normalize-space(.)='{DATOS_CLIENTE[0]}']]",
            )
        )
    )

    # La fila debe mostrar exactamente los datos registrados
    # (textContent, porque el CSS puede renderizar celdas en mayusculas)
    assert fila.find_element(
        By.CSS_SELECTOR, "td:nth-child(2)"
    ).get_attribute("textContent").strip() == "Persona Natural"
    assert fila.find_element(
        By.CSS_SELECTOR, "td:nth-child(3)"
    ).get_attribute("textContent").strip() == DATOS_CLIENTE[1]
    assert fila.find_element(
        By.CSS_SELECTOR, "td:nth-child(4)"
    ).get_attribute("textContent").strip() == DATOS_CLIENTE[2]
    assert fila.find_element(
        By.CSS_SELECTOR, "td:nth-child(5)"
    ).get_attribute("textContent").strip() == DATOS_CLIENTE[3]

    fila.find_element(By.CSS_SELECTOR, "button[data-action='ver']").click()

    # --- Modal 'Detalles del cliente': titulo, etiquetas y datos ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-ver-cliente")))
    assert driver.find_element(By.ID, "modal-ver-cliente-title").text == (
        "Detalles del cliente"
    )
    # textContent (texto del DOM), porque el CSS renderiza las etiquetas en mayusculas
    etiquetas = [
        label.get_attribute("textContent").strip()
        for label in driver.find_elements(
            By.CSS_SELECTOR, "#modal-ver-cliente .detalle-item label"
        )
    ]
    assert etiquetas == [
        "ID / Cédula",
        "Tipo",
        "Nombre / Razón Social",
        "Apellido / RIF",
        "Celular / Teléfono",
        "Correo electrónico",
        "Dirección",
    ]

    assert driver.find_element(By.ID, "detalle-cliente-id").text == DATOS_CLIENTE[0]
    assert driver.find_element(By.ID, "detalle-cliente-tipo").text == "Persona Natural"
    assert driver.find_element(By.ID, "detalle-cliente-nombre").text == (
        f"{DATOS_CLIENTE[1]} {DATOS_CLIENTE[2]}"
    )
    assert driver.find_element(By.ID, "detalle-cliente-apellido-rif").text == DATOS_CLIENTE[2]
    assert driver.find_element(By.ID, "detalle-cliente-celular").text == DATOS_CLIENTE[3]
    assert driver.find_element(By.ID, "detalle-cliente-correo").text == DATOS_CLIENTE[4]
    assert driver.find_element(By.ID, "detalle-cliente-direccion").text == DATOS_CLIENTE[5]

    # --- Boton 'Cerrar': estilo fantasma (ghost, colores del tema oscuro) ---
    boton_cerrar = driver.find_element(
        By.CSS_SELECTOR, "#modal-ver-cliente .ui-form__actions [data-close-modal]"
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
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-ver-cliente")))
    print(
        f"Cliente consultado: {DATOS_CLIENTE[0]} - "
        f"{DATOS_CLIENTE[1]} {DATOS_CLIENTE[2]}"
    )
