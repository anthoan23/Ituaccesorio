import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

URL_ORDENES_COMPRA = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/ordenes_compra"
URL_ORDENES_ENTREGAS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/ordenes_entregas"
TIEMPO_ESPERA = 10

# [recibido_por]
RECIBIDO_POR = "Empleado Receptor"

# Prueba autocontenida: crea por la UI una orden de compra pendiente (ID
# autogenerado tipo OC000000X, primer empleado + primer proveedor + primer
# producto) en /ordenes_compra y despues registra su entrega en
# /ordenes_entregas. No depende del orden de ejecucion ni muta la semilla.


def test_registrar_orden_entrega(driver):
    # ---- Paso 1: crear la orden de compra pendiente por la UI ----
    driver.get(URL_ORDENES_COMPRA)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(
        lambda d: "Cargando" not in d.find_element(By.ID, "tabla-ordenes-pendientes").text
    )
    ids_antes = {
        fila.get_attribute("data-id")
        for fila in driver.find_elements(
            By.CSS_SELECTOR, "#tabla-ordenes-pendientes tr[data-id]"
        )
    }
    driver.find_element(By.ID, "btn-registrar-entrada").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-registrar-entrada")))
    espera.until(
        lambda d: len(Select(d.find_element(By.ID, "entrada-id-empleado")).options) > 1
    )
    Select(driver.find_element(By.ID, "entrada-id-empleado")).select_by_index(1)

    driver.find_element(By.ID, "btn-desplegar-proveedores").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-seleccionar-proveedor")))
    fila_proveedor = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#lista-proveedores tr[data-proveedor-id]")
        )
    )
    nombre_proveedor = fila_proveedor.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
    fila_proveedor.click()
    # El POST de productos del proveedor abre el feedback-modal: esperar su autocierre
    espera.until(EC.visibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    driver.find_element(By.ID, "btn-desplegar-productos").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-seleccionar-productos")))
    fila_producto = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#lista-productos tr[data-producto-id]")
        )
    )
    fila_producto.click()
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#tabla-productos-seleccionados .cantidad-valor")
        )
    )

    boton_guardar = driver.find_element(By.ID, "btn-guardar-entrada")
    espera.until(lambda d: not boton_guardar.get_attribute("disabled"))
    boton_guardar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-registrar-entrada")))

    def fila_nueva(d):
        for fila in d.find_elements(
            By.CSS_SELECTOR, "#tabla-ordenes-pendientes tr[data-id]"
        ):
            if fila.get_attribute("data-id") not in ids_antes:
                return fila
        return False

    id_orden = espera.until(fila_nueva).get_attribute("data-id")
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # ---- Paso 2: registrar la entrega de esa orden ----
    driver.get(URL_ORDENES_ENTREGAS)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    boton_entrega = espera.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "#tabla-ordenes-entregas-pendientes "
                f"button[data-action='registrar-entrega'][data-id='{id_orden}']",
            )
        )
    )
    boton_entrega.click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-registrar-entrega")))
    # La vista previa de productos se llena por fetch
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#entrega-productos-preview table")
        )
    )

    campo_recibido = driver.find_element(By.ID, "entrega-recibido-por")
    campo_recibido.clear()
    campo_recibido.send_keys(RECIBIDO_POR)
    # La fecha ya viene precargada con el dia actual; se confirma tal cual
    driver.find_element(By.ID, "btn-confirmar-entrega").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-registrar-entrega")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # ---- Paso 3: la entrega pasa al historial de entregas ----
    driver.find_element(By.ID, "btn-entregadas").click()
    espera.until(
        lambda d: "Cargando"
        not in d.find_element(By.ID, "tabla-ordenes-entregas-historial").text
    )
    fila_historial = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//*[@id='tabla-ordenes-entregas-historial']"
                f"//tr[td[2][normalize-space(.)='{id_orden}']]",
            )
        )
    )
    recibido_mostrado = fila_historial.find_element(By.CSS_SELECTOR, "td:nth-child(6)").text
    assert recibido_mostrado == RECIBIDO_POR
    print(
        f"Entrega registrada: orden {id_orden} (proveedor: {nombre_proveedor}) "
        f"recibida por {RECIBIDO_POR}"
    )
