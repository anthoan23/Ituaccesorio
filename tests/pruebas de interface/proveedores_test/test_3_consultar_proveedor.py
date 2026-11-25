import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css

URL_PROVEEDORES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/proveedores"
TIEMPO_ESPERA = 10

# [rif, nombre, tipo, celular, correo, direccion]
# El proveedor que la cadena creo y modifico en los tests anteriores
DATOS_PROVEEDOR = [
    "J-80076543-2",
    "Proveedor Interfaz Editado",
    "Nacional",
    "04147654321",
    "proveedor.interfaz@ituaccesorio.com",
    "Barquisimeto",
]


def test_consultar_proveedor(driver):
    driver.get(URL_PROVEEDORES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Filtrar por nombre para que la fila quede visible y clickeable
    buscador = driver.find_element(
        By.CSS_SELECTOR, ".proveedores-grid .table-controls__input"
    )
    buscador.send_keys(DATOS_PROVEEDOR[1])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-proveedores']//tr[td[3][normalize-space(.)='{DATOS_PROVEEDOR[1]}']]",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='ver']").click()

    # --- Modal 'Consultar proveedor': titulo, etiquetas y datos ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-proveedor-ver")))
    assert driver.find_element(By.ID, "modal-proveedor-ver-title").text == (
        "Consultar proveedor"
    )
    # textContent (texto del DOM), porque el CSS renderiza las etiquetas en mayusculas
    etiquetas = [
        label.get_attribute("textContent").strip()
        for label in driver.find_elements(
            By.CSS_SELECTOR, "#modal-proveedor-ver .detail-label"
        )
    ]
    assert etiquetas == [
        "ID", "RIF", "Proveedor", "Tipo", "Teléfono",
        "Correo", "Límite crédito", "Dirección",
    ]

    rif = driver.find_element(By.ID, "v-rif").text
    nombre = driver.find_element(By.ID, "v-nombre").text
    tipo = driver.find_element(By.ID, "v-tipo").text
    celular = driver.find_element(By.ID, "v-celular").text
    correo = driver.find_element(By.ID, "v-correo").text
    direccion = driver.find_element(By.ID, "v-direccion").text
    limite = driver.find_element(By.ID, "v-limite").text

    assert rif == DATOS_PROVEEDOR[0]
    assert nombre == DATOS_PROVEEDOR[1]
    assert tipo == DATOS_PROVEEDOR[2]
    assert celular == DATOS_PROVEEDOR[3]
    assert correo == DATOS_PROVEEDOR[4]
    assert direccion == DATOS_PROVEEDOR[5]
    # El limite se formatea con separador de miles es-VE; solo verificamos que
    # los digitos escritos (1500) aparezcan en el valor mostrado
    assert limite.replace(".", "").replace(",", "") == "1500", (
        f"El limite de credito mostrado no corresponde: '{limite}'"
    )

    # --- Boton 'Cerrar': estilo fantasma (ghost, colores del tema oscuro) ---
    boton_cerrar = driver.find_element(
        By.CSS_SELECTOR, "#modal-proveedor-ver .ui-form__actions [data-close-modal]"
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
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-proveedor-ver")))
    print(f"Proveedor consultado: {nombre} - {rif}")
