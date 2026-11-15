import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

URL_ORDENES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/ordenes-servicio"
TIEMPO_ESPERA = 10

# ----------------------------------------------------------------------
# Prueba de interface: registrar la revision (test #1) de una orden de
# servicio desde /ordenes-servicio.
# NOTA DE FLUJO: en esta pagina la unica via de UI para registrar una
# revision es el modal "Revision inicial del equipo" (se abre solo al
# guardar el modal "Nueva orden" y se guarda como test #1 junto con la
# orden). El modal "modal-revision-orden" existe en el HTML pero ningun
# flujo de esta pagina lo abre, por eso la revision se marca aqui.
# AUTOCONTENIDA: crea su propia orden temporal registrando la revision
# con el LCD marcado como "No funciona" y observaciones. El registro
# queda persistido en la BD (no se elimina al terminar).
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

# Observaciones de la revision (sin las palabras "funciona" ni "falla"
# para no alterar los contadores de exito/fallo del resumen del test)
OBSERVACIONES = "Pantalla con desprendimiento detectado en la revision inicial de prueba"


def test_registrar_revision(driver):
    driver.get(URL_ORDENES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(lambda d: len(Select(d.find_element(By.ID, "orden-modelo")).options) > 1)

    # --- Modal de nueva orden ---
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

    # --- Guardar: abre el modal de revision inicial (test #1) ---
    driver.find_element(By.CSS_SELECTOR, "#form-orden-servicio button[type='submit']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-revision-inicial")))

    # --- Marcar componentes: todos OK y el LCD como "No funciona" (valor 0) ---
    driver.find_element(
        By.CSS_SELECTOR, "#modal-revision-inicial #btn-marcar-todos-test"
    ).click()
    driver.find_element(
        By.CSS_SELECTOR, "#modal-revision-inicial input[name='test_LCD'][value='0']"
    ).click()
    driver.find_element(By.ID, "revision-observaciones").send_keys(OBSERVACIONES)

    # --- Guardar la revision junto con la orden ---
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

    # --- Verificar la confirmacion: el detalle muestra el test #1 con 1 fallo ---
    fila.find_element(By.CSS_SELECTOR, "button[data-action='ver-detalle']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-detalle-orden")))
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#modal-order-tests .tests-table-wrap")
        )
    )
    tests = driver.find_element(By.ID, "modal-order-tests").text
    assert "Test #1" in tests
    assert "❌ 1" in tests

    # --- Cerrar el modal de detalle ---
    driver.find_element(
        By.CSS_SELECTOR, "#modal-detalle-orden .ui-form__actions button[data-close-modal]"
    ).click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-detalle-orden")))

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Revision (test #1) registrada en la orden {id_orden}: LCD marcado como falla")
