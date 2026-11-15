import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

URL_ORDENES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/ordenes-servicio"
TIEMPO_ESPERA = 10

# ----------------------------------------------------------------------
# Prueba de interface: crear una orden de servicio desde /ordenes-servicio.
# AUTOCONTENIDA: registra una orden temporal (flujo minimo: modal "Nueva
# orden" + modal "Revision inicial" que el JS abre automaticamente).
# El registro queda persistido en la BD (no se elimina al terminar).
# Datos fijos: si el cliente o el equipo ya existen, el controlador/JS los
# reutiliza en lugar de duplicarlos.
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


def test_crear_orden_servicio(driver):
    driver.get(URL_ORDENES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # El select de modelos se llena por API; se espera a que tenga opciones
    espera.until(lambda d: len(Select(d.find_element(By.ID, "orden-modelo")).options) > 1)

    # --- Abrir el modal de nueva orden ---
    driver.find_element(By.ID, "btn-nueva-orden").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-nueva-orden")))

    # --- Datos del equipo ---
    driver.find_element(By.ID, "orden-id-equipo").send_keys(DATOS_ORDEN[0])
    driver.find_element(By.ID, "orden-modelo-custom").send_keys(DATOS_ORDEN[1])
    driver.find_element(By.ID, "orden-color").send_keys(DATOS_ORDEN[2])
    Select(driver.find_element(By.ID, "orden-capacidad")).select_by_visible_text(DATOS_ORDEN[3])
    driver.find_element(By.ID, "orden-patron").send_keys(DATOS_ORDEN[4])
    driver.find_element(By.ID, "orden-descripcion").send_keys(DATOS_ORDEN[5])

    # --- Datos del cliente natural (el JS lo reutiliza si ya existe) ---
    driver.find_element(By.ID, "cliente-cedula").send_keys(DATOS_CLIENTE[0])
    driver.find_element(By.ID, "cliente-celular").send_keys(DATOS_CLIENTE[3])
    driver.find_element(By.ID, "cliente-nombre").send_keys(DATOS_CLIENTE[1])
    driver.find_element(By.ID, "cliente-apellido").send_keys(DATOS_CLIENTE[2])

    # --- Guardar: el JS cierra este modal y abre el de revision inicial ---
    driver.find_element(By.CSS_SELECTOR, "#form-orden-servicio button[type='submit']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-revision-inicial")))

    # --- Confirmar la revision inicial (todos los componentes OK por defecto) ---
    driver.find_element(By.ID, "btn-confirmar-revision").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-revision-inicial")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificar que la orden aparece en la tabla (la mas reciente es la primera) ---
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//tbody[@id='tabla-ordenes']/tr[td[4][normalize-space(.)='{DATOS_ORDEN[0]}']][1]",
            )
        )
    )
    id_orden = fila.find_element(By.CSS_SELECTOR, "td.col-id").text.strip()
    estado = fila.find_element(By.CSS_SELECTOR, "td.col-estado").text.strip()
    cliente = fila.find_element(By.CSS_SELECTOR, "td.col-cliente").text.strip()
    modelo = fila.find_element(By.CSS_SELECTOR, "td.col-modelo").text.strip()

    assert estado == "Pendiente"
    assert cliente == f"{DATOS_CLIENTE[1]} {DATOS_CLIENTE[2]}"
    assert modelo == DATOS_ORDEN[1]

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Orden de servicio creada: {id_orden} (IMEI {DATOS_ORDEN[0]}, cliente {cliente})")
