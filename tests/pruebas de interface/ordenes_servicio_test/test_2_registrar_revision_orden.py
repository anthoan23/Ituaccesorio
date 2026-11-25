import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from helpers import esperar_feedback, quitar_hover

from test_1_crear_orden_servicio import DATOS_CLIENTE, DATOS_ORDEN

URL_ORDENES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/ordenes-servicio"
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
# queda persistido en la BD (no se elimina al terminar; la pagina no
# ofrece eliminacion de ordenes).
# MECANISMO DE FEEDBACK: ordenes_servicio.js no muestra feedback propio
# (consola); el visible es el del interceptor global de fetch.
# ----------------------------------------------------------------------

# Observaciones de la revision (sin las palabras "funciona" ni "falla"
# para no alterar los contadores de exito/fallo del resumen del test)
OBSERVACIONES = "Pantalla con desprendimiento detectado en la revision inicial de prueba"


def test_registrar_revision(driver):
    driver.get(URL_ORDENES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(lambda d: len(Select(d.find_element(By.ID, "orden-modelo")).options) > 1)

    # --- Modal de nueva orden (datos reutilizados si ya existen) ---
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
    # Si el cliente se dio de alta ahora, el feedback-modal queda encima: esperar
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

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
    # Feedback visible: el del interceptor global (el JS del modulo va a consola)
    esperar_feedback(
        espera, tipo="success", titulo="Acción exitosa", mensaje="Registro realizado satisfactoriamente."
    )

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
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-detalle-orden-title").text == "Detalle de orden"
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#modal-order-tests .tests-table-wrap")
        )
    )
    tests = driver.find_element(By.ID, "modal-order-tests").text
    assert "Test #1" in tests
    assert "❌ 1" in tests

    # --- Cerrar el modal de detalle con el boton "Cerrar" (ghost) ---
    boton_cerrar = driver.find_element(
        By.CSS_SELECTOR, "#modal-detalle-orden .ui-form__actions button[data-close-modal]"
    )
    assert boton_cerrar.text.strip() == "Cerrar"
    assert "ui-btn--ghost" in boton_cerrar.get_attribute("class")
    boton_cerrar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-detalle-orden")))

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Revision (test #1) registrada en la orden {id_orden}: LCD marcado como fallo")
