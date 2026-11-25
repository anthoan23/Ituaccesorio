import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

# Módulo de entregas: registrar una entrega (modal "Registrar entrega")
# PRERREQUISITO: al menos una factura pendiente (sin entrega asignada) en la BD
# y al menos un delivery registrado (el creado por crear_personal_delivery.py o
# cualquiera disponible en el select). En el select se elige la primera opción
# disponible de factura pendiente y de delivery.
URL_ENTREGAS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/entregas"
TIEMPO_ESPERA = 10

# Dirección de entrega de prueba (el validador filtra '.' y ',', por lo que en
# el formulario queda "Av Principal Barquisimeto"; la verificación usa
# "Barquisimeto" que no se ve afectado)
DATOS_ENTREGA = ["Av. Principal, Barquisimeto"]


def test_registrar_entrega(driver):
    driver.get(URL_ENTREGAS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # El botón pertenece a la pestaña Entregas (activa por defecto); su JS carga
    # las facturas pendientes y el select de delivery antes de abrir el modal
    driver.find_element(By.ID, "btn-nueva-entrega").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-entrega")))
    espera.until(
        lambda navegador: len(
            Select(navegador.find_element(By.ID, "factura-id")).options
        )
        > 1
    )
    espera.until(
        lambda navegador: len(
            Select(navegador.find_element(By.ID, "delivery-cedula")).options
        )
        > 1
    )
    # Primera factura pendiente (el índice 0 es la opción vacía)
    select_factura = Select(driver.find_element(By.ID, "factura-id"))
    select_factura.select_by_index(1)
    factura_id = select_factura.first_selected_option.get_attribute("value")
    # Delivery creado o primera opción disponible del select
    Select(driver.find_element(By.ID, "delivery-cedula")).select_by_index(1)
    direccion = driver.find_element(
        By.CSS_SELECTOR, "#form-entrega textarea[name='direccion']"
    )
    direccion.clear()
    direccion.send_keys(DATOS_ENTREGA[0])
    driver.find_element(
        By.CSS_SELECTOR, "#form-entrega button[type='submit']"
    ).click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-entrega")))
    # La fila debe contener la factura y la dirección registrada (excluye
    # entregas anteriores de la misma factura)
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//*[@id='tabla-entregas']//tr["
                f"td[2][contains(., '{factura_id}')] and "
                "td[5][contains(., 'Barquisimeto')]]",
            )
        )
    )
    assert "Barquisimeto" in fila.text
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Entrega registrada: factura {factura_id} con dirección {DATOS_ENTREGA[0]}")
