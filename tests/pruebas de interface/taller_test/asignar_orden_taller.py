import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

URL_ORDENES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/ordenes-servicio"
URL_TALLER = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/taller"
TIEMPO_ESPERA = 10

# ----------------------------------------------------------------------
# Prueba de interface: asignar (tomar) una orden pendiente desde el
# modulo Taller (/taller, boton "Tomar orden" de la fila).
# AUTOCONTENIDA: crea primero su propia orden temporal en
# /ordenes-servicio (flujo minimo) y luego la toma en el taller. El
# registro queda persistido en la BD (no se elimina al terminar).
# NOTAS:
# - taller.js obtiene el id del empleado logueado del localStorage/JWT
#   para habilitar tomar/revisar/reparar/liberar; en modo prueba no hay
#   login, por lo que se simula con execute_script antes de usar los
#   botones (el servidor toma el empleado real de la sesion).
# - El endpoint /api/taller/asignar-orden usa g.user.get("cedula"),
#   incompatible con el usuario SimpleNamespace de ENTORNO_PRUEBA
#   (falla con 500); la prueba sigue el flujo real de la UI y requiere
#   una sesion real (token JWT) para completar la asignacion.
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


def test_asignar_orden_taller(driver):
    # ---------------------------------------------------------------
    # PASO 1: crear la orden temporal pendiente en /ordenes-servicio
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

    fila_nueva = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//tbody[@id='tabla-ordenes']/tr[td[4][normalize-space(.)='{DATOS_ORDEN[0]}']][1]",
            )
        )
    )
    id_orden = fila_nueva.find_element(By.CSS_SELECTOR, "td.col-id").text.strip()

    # ---------------------------------------------------------------
    # PASO 2: tomar (asignar) la orden en el taller
    # ---------------------------------------------------------------
    driver.get(URL_TALLER)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # Simular el empleado logueado (requisito de taller.js para tomar ordenes)
    driver.execute_script(
        "window.localStorage.setItem('user', JSON.stringify({id_empleado: '1'}));"
    )

    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//tbody[@id='tabla-ordenes-servicio']//tr[@data-id='{id_orden}']",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-accion='tomar-orden']").click()

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificar la confirmacion: la orden queda "Asignada" y sale de
    # la lista de ordenes pendientes del taller ---
    espera.until(
        EC.invisibility_of_element_located(
            (
                By.XPATH,
                f"//tbody[@id='tabla-ordenes-servicio']//tr[@data-id='{id_orden}']",
            )
        )
    )

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Orden asignada (tomada) en el taller: {id_orden} -> estado 'Asignada'")
