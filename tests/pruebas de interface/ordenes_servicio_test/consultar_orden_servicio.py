import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

URL_ORDENES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/ordenes-servicio"
TIEMPO_ESPERA = 10

# ----------------------------------------------------------------------
# Prueba de interface: consultar el detalle de una orden de servicio
# desde /ordenes-servicio (modal "Detalle de orden" con orden + fotos +
# historial de revisiones).
# AUTOCONTENIDA: crea primero su propia orden temporal (flujo minimo) y
# luego abre el detalle de esa orden. El registro queda persistido en la
# BD (no se elimina al terminar).
# Requisitos: ENTORNO_PRUEBA=true (decoradores desactivados) y BD sembrada
# con modelos de telefono (el select #orden-modelo se llena por API).
# ----------------------------------------------------------------------

# [imei, modelo_custom, color, capacidad, patron, descripcion]
# El patron "L" se envia como trazo numerico 1-4-7-8-9 porque el campo
# solo acepta numeros del 1 al 9 separados por guiones.
DATOS_ORDEN = [
    "351111111111199",      # IMEI (15 digitos)
    "Modelo Custom Prueba", # modelo personalizado (se deja el select vacio)
    "Negro",                # color
    "128GB",                # capacidad
    "1-4-7-8-9",            # patron en forma de "L"
    "Pantalla rota",        # descripcion del problema
]

# Cliente natural [cedula, nombre, apellido, celular]
DATOS_CLIENTE = ["65432109", "Cliente", "Prueba", "04141234567"]


def test_consultar_orden_servicio(driver):
    # ---------------------------------------------------------------
    # PASO 1: crear la orden temporal sobre la que se va a consultar
    # ---------------------------------------------------------------
    driver.get(URL_ORDENES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(lambda d: len(Select(d.find_element(By.ID, "orden-modelo")).options) > 1)

    driver.find_element(By.ID, "btn-nueva-orden").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-nueva-orden")))

    driver.find_element(By.ID, "orden-id-equipo").send_keys(DATOS_ORDEN[0])
    driver.find_element(By.ID, "orden-modelo-custom").send_keys(DATOS_ORDEN[1])
    driver.find_element(By.ID, "orden-color").send_keys(DATOS_ORDEN[2])
    Select(driver.find_element(By.ID, "orden-capacidad")).select_by_visible_text(DATOS_ORDEN[3])
    driver.find_element(By.ID, "orden-patron").send_keys(DATOS_ORDEN[4])
    driver.find_element(By.ID, "orden-descripcion").send_keys(DATOS_ORDEN[5])

    driver.find_element(By.ID, "cliente-cedula").send_keys(DATOS_CLIENTE[0])
    driver.find_element(By.ID, "cliente-celular").send_keys(DATOS_CLIENTE[3])
    driver.find_element(By.ID, "cliente-nombre").send_keys(DATOS_CLIENTE[1])
    driver.find_element(By.ID, "cliente-apellido").send_keys(DATOS_CLIENTE[2])

    driver.find_element(By.CSS_SELECTOR, "#form-orden-servicio button[type='submit']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-revision-inicial")))
    driver.find_element(By.ID, "btn-confirmar-revision").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-revision-inicial")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//tbody[@id='tabla-ordenes']/tr[td[4][normalize-space(.)='{DATOS_ORDEN[0]}']][1]",
            )
        )
    )
    id_orden = fila.find_element(By.CSS_SELECTOR, "td.col-id").text.strip()

    # ---------------------------------------------------------------
    # PASO 2: abrir el detalle de la orden con el boton de la fila
    # ---------------------------------------------------------------
    fila.find_element(By.CSS_SELECTOR, "button[data-action='ver-detalle']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-detalle-orden")))
    # El detalle se carga por API; se espera a que se dibuje la informacion
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#modal-order-info .detail-group")
        )
    )

    # --- Verificar los datos del equipo y del cliente en el detalle ---
    info = driver.find_element(By.ID, "modal-order-info").text
    assert f"#{id_orden}" in info
    assert f"{DATOS_CLIENTE[1]} {DATOS_CLIENTE[2]}" in info
    assert DATOS_ORDEN[0] in info       # IMEI en el campo Equipo
    assert DATOS_ORDEN[1] in info       # modelo
    assert DATOS_ORDEN[5] in info       # descripcion del problema

    # --- Verificar que el historial de revisiones muestra el test #1 ---
    # (la creacion siempre registra la revision inicial)
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#modal-order-tests .tests-table-wrap")
        )
    )
    tests = driver.find_element(By.ID, "modal-order-tests").text
    assert "Test #1" in tests

    # --- Cerrar el modal de detalle ---
    driver.find_element(
        By.CSS_SELECTOR, "#modal-detalle-orden .ui-form__actions button[data-close-modal]"
    ).click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-detalle-orden")))

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Orden consultada: {id_orden} (IMEI {DATOS_ORDEN[0]}, test #1 visible en el historial)")
