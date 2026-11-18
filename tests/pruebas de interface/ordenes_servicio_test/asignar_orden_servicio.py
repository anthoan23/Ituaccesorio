import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

URL_ORDENES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/ordenes-servicio"
TIEMPO_ESPERA = 10

# ----------------------------------------------------------------------
# Prueba de interface: asignar una orden de servicio a un tecnico
# desde /ordenes-servicio (boton "Asignar" de la fila + modal
# "Asignar orden a tecnico").
# AUTOCONTENIDA: crea primero su propia orden temporal (flujo minimo) y
# luego la asigna usando el boton de asignacion de su fila. El registro
# queda persistido en la BD (no se elimina al terminar).
# Requisitos: ENTORNO_PRUEBA=true (decoradores desactivados), BD sembrada
# con modelos de telefono y con al menos un tecnico registrado
# (el select #modal-tecnico-select se llena por API).
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


def test_asignar_orden_servicio(driver):
    # ---------------------------------------------------------------
    # PASO 1: crear la orden temporal pendiente que se va a asignar
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
    # PASO 2: asignar la orden con el boton "Asignar tecnico" de la fila
    # (el JS preselecciona esa orden en el modal)
    # ---------------------------------------------------------------
    fila.find_element(By.CSS_SELECTOR, "button[data-action='seleccionar-asignacion']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-asignar-tecnico")))

    # La orden pulsada debe venir preseleccionada en el modal
    assert driver.find_element(By.ID, "select-orden-asignar").get_attribute("value") == id_orden

    # Esperar a que el select de tecnicos se llene por API y elegir el primero
    espera.until(lambda d: len(Select(d.find_element(By.ID, "modal-tecnico-select")).options) > 1)
    Select(driver.find_element(By.ID, "modal-tecnico-select")).select_by_index(1)

    driver.find_element(By.ID, "btn-asignar-orden").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-asignar-tecnico")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificar el cambio de estado visible en la tabla ---
    fila_asignada = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//tbody[@id='tabla-ordenes']//tr[td[1][normalize-space(.)='{id_orden}']]",
            )
        )
    )
    estado = fila_asignada.find_element(By.CSS_SELECTOR, "td.col-estado").text.strip()
    assert estado == "Asignada"

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Orden asignada: {id_orden} -> estado '{estado}' en la tabla")
