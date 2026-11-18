import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

URL_ORDENES_COMPRA = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/ordenes_compra"
URL_ORDENES_ENTREGAS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/ordenes_entregas"
TIEMPO_ESPERA = 10

# [recibido_inicial, recibido_editado]
RECIBIDO_INICIAL = "Empleado Receptor"
RECIBIDO_EDITADO = "Empleado Receptor Editado"

# Prueba autocontenida: crea por la UI su propia orden temporal (ID
# autogenerado tipo OC000000X), registra su entrega en /ordenes_entregas y
# despues la edita desde el boton "editar" del historial (modal de edicion).
# El campo "Recibido por" tiene maxlength=20: el navegador recorta el texto
# tecleado, por eso el valor esperado se lee del propio input. No depende del
# orden de ejecucion ni muta la semilla.


def test_editar_orden_entrega(driver):
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
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#entrega-productos-preview table")
        )
    )

    campo_recibido = driver.find_element(By.ID, "entrega-recibido-por")
    campo_recibido.clear()
    campo_recibido.send_keys(RECIBIDO_INICIAL)
    driver.find_element(By.ID, "btn-confirmar-entrega").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-registrar-entrega")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # ---- Paso 3: editar la entrega desde el historial ----
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

    # El formulario de edicion se precarga por fetch (GET, sin feedback-modal)
    fila_historial.find_element(By.CSS_SELECTOR, "button[data-action='editar-entrega']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-editar-entrega")))
    espera.until(
        lambda d: d.find_element(By.ID, "editar-id-orden-entrega").get_attribute("value")
        == id_orden
    )
    espera.until(
        lambda d: d.find_element(By.ID, "editar-recibido-por").get_attribute("value")
        == RECIBIDO_INICIAL
    )

    campo_editado = driver.find_element(By.ID, "editar-recibido-por")
    campo_editado.clear()
    campo_editado.send_keys(RECIBIDO_EDITADO)
    valor_recibido = campo_editado.get_attribute("value")

    driver.find_element(By.ID, "btn-guardar-editar-entrega").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-editar-entrega")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # El historial se recarga: la fila debe mostrar el nuevo receptor
    def fila_actualizada(d):
        for fila in d.find_elements(
            By.XPATH,
            "//*[@id='tabla-ordenes-entregas-historial']"
            f"//tr[td[2][normalize-space(.)='{id_orden}']]",
        ):
            if fila.find_element(By.CSS_SELECTOR, "td:nth-child(6)").text == valor_recibido:
                return fila
        return False

    espera.until(fila_actualizada)
    print(
        f"Entrega editada: orden {id_orden} (proveedor: {nombre_proveedor}) "
        f"recibido por '{RECIBIDO_INICIAL}' -> '{valor_recibido}'"
    )
