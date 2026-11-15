import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

URL_ORDENES_COMPRA = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/ordenes_compra"
TIEMPO_ESPERA = 10

# Prueba autocontenida: crea por la UI su propia orden temporal (ID
# autogenerado tipo OC000000X, primer empleado + primer proveedor + primer
# producto, cantidad 2) y despues la anula desde su fila en pendientes.
# El boton "eliminar" de la tabla dispara el modal de confirmacion y llama a
# /api/ordenes_compra/anular, que deja la orden con Estado = 'Anulada'.
# No depende del orden de ejecucion ni muta la semilla.


def test_anular_orden_compra(driver):
    driver.get(URL_ORDENES_COMPRA)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # ---- Creacion de la orden temporal (flujo minimo) ----
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
    driver.find_element(
        By.CSS_SELECTOR, "#tabla-productos-seleccionados button.btn-cantidad[data-op='mas']"
    ).click()
    espera.until(
        lambda d: d.find_element(
            By.CSS_SELECTOR, "#tabla-productos-seleccionados .cantidad-valor"
        ).text
        == "2"
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

    # ---- Anulacion desde el boton "eliminar" de la fila ----
    fila_orden = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, f"#tabla-ordenes-pendientes tr[data-id='{id_orden}']")
        )
    )
    fila_orden.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-confirmar-eliminar-orden")))
    texto_confirmacion = driver.find_element(By.ID, "texto-confirmar-eliminar-orden").text
    assert id_orden in texto_confirmacion

    driver.find_element(By.ID, "btn-confirmar-eliminar-orden").click()
    espera.until(
        EC.invisibility_of_element_located((By.ID, "modal-confirmar-eliminar-orden"))
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # La orden anulada desaparece de la tabla de pendientes
    espera.until(
        EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, f"#tabla-ordenes-pendientes tr[data-id='{id_orden}']")
        )
    )
    print(f"Orden de compra anulada: {id_orden} (proveedor: {nombre_proveedor})")
