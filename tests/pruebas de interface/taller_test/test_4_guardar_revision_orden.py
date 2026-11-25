import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from helpers import estilo_css, esperar_feedback

URL_ORDENES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/ordenes-servicio"
URL_TALLER = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/taller"
TIEMPO_ESPERA = 10

# ----------------------------------------------------------------------
# Prueba de interface: guardar una revision tecnica desde el modulo
# Taller (vista-5 "Reparaciones asignadas" -> detalle -> vista-3
# "Revision" -> formulario #form-revision-tecnica, componentes
# evaluados como radios Funciona / No funciona).
# AUTOCONTENIDA: crea primero su propia orden temporal en
# /ordenes-servicio (la creacion registra el test #1), la toma en el
# taller y le guarda la revision tecnica (test #2). El registro queda
# persistido en la BD (no se elimina al terminar).
# NOTAS:
# - taller.js obtiene el id del empleado logueado del localStorage/JWT;
#   en modo prueba no hay login, por lo que se simula con execute_script.
# - Los endpoints /api/taller/asignar-orden, guardar-revision y
#   reparaciones-asignadas usan g.user.get("cedula"), incompatible con
#   el usuario SimpleNamespace de ENTORNO_PRUEBA (fallan con 500); la
#   prueba sigue el flujo real de la UI y requiere sesion real (JWT).
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

OBSERVACIONES = "Revisión técnica de prueba del taller"

# TALLER_CONFIG.COMPONENTES_TEST en taller.js: 22 componentes evaluables
CANTIDAD_COMPONENTES = 22


def test_guardar_revision_taller(driver):
    # ---------------------------------------------------------------
    # PASO 1: crear la orden temporal (la creacion registra el test #1)
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
    # PASO 2: tomar la orden en el taller y abrir su detalle
    # ---------------------------------------------------------------
    driver.get(URL_TALLER)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    driver.execute_script(
        "window.localStorage.setItem('user', JSON.stringify({id_empleado: '1'}));"
    )

    buscador = driver.find_element(
        By.XPATH,
        "//section[contains(@class,'vista-1')]//input[contains(@class,'table-controls__input')]",
    )
    buscador.send_keys(id_orden)
    fila = espera.until(
        EC.visibility_of_element_located(
            (By.XPATH, f"//tbody[@id='tabla-ordenes-servicio']//tr[@data-id='{id_orden}']")
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-accion='tomar-orden']").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    driver.find_element(
        By.XPATH, "//section[contains(@class,'vista-1')]//button[@data-view-target='vista-5']"
    ).click()
    fila_asignada = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//tbody[@id='tabla-reparaciones-asignadas']//tr[@data-id='{id_orden}']",
            )
        )
    )
    fila_asignada.find_element(By.CSS_SELECTOR, "button[data-accion='ver-detalle']").click()

    # verDetalle activa la vista-2 "Informacion de la orden"
    espera.until(
        lambda d: d.find_element(By.XPATH, "//section[contains(@class,'vista-2')]").is_displayed()
    )
    espera.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#order-info .detail-group"))
    )

    # ---------------------------------------------------------------
    # PASO 3: abrir el formulario de revision (vista-3) y guardarlo
    # ---------------------------------------------------------------
    driver.find_element(By.ID, "btn-realizar-revision").click()
    espera.until(
        lambda d: d.find_element(By.XPATH, "//section[contains(@class,'vista-3')]").is_displayed()
    )

    # --- Verificaciones visuales del formulario de revision ---
    # La tarjeta muestra la orden en revision (el JS rellena el span)
    tarjeta = driver.find_element(By.XPATH, "//section[contains(@class,'vista-3')]")
    assert "Revisión de la orden" in tarjeta.find_element(
        By.CSS_SELECTOR, ".card__subtitle"
    ).get_attribute("textContent")
    assert driver.find_element(By.ID, "orden-id").get_attribute("textContent").strip() == id_orden

    # Los componentes se dibujan por JS; se espera a que existan los radios
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#form-revision-tecnica input[name='test_LCD']")
        )
    )
    items = driver.find_elements(By.CSS_SELECTOR, "#test-componentes-grid .test-row-item")
    assert len(items) == CANTIDAD_COMPONENTES, (
        f"Deberian dibujarse {CANTIDAD_COMPONENTES} componentes y hay {len(items)}"
    )
    primer_componente = driver.find_element(
        By.CSS_SELECTOR, "#test-componentes-grid .test-row-item .test-label"
    ).get_attribute("textContent").strip()
    assert primer_componente == "Botón power"

    # Botones de atajo: fantasma (ghost, colores del tema oscuro)
    quitar_hover(driver)
    boton_ok = driver.find_element(By.ID, "btn-marcar-todos-test")
    assert boton_ok.text.strip() == "✅ Marcar todos como OK"
    assert "ui-btn--ghost" in boton_ok.get_attribute("class")
    assert estilo_css(driver, boton_ok, "backgroundColor") == "rgba(255, 255, 255, 0.06)", (
        "El fondo de 'Marcar todos como OK' deberia ser el ghost del tema oscuro"
    )
    boton_fallo = driver.find_element(By.ID, "btn-marcar-todos-fallo")
    assert boton_fallo.text.strip() == "❌ Marcar todos como No funciona"
    assert "ui-btn--ghost" in boton_fallo.get_attribute("class")

    # Boton 'Guardar revisión': fondo amarillo con texto oscuro
    boton_guardar = driver.find_element(
        By.CSS_SELECTOR, "#form-revision-tecnica button[type='submit']"
    )
    assert boton_guardar.text.strip() == "Guardar revisión"
    assert estilo_css(driver, boton_guardar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Guardar revisión' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_guardar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Guardar revisión' deberia ser oscuro"
    )

    # Evaluar componentes: todos OK y el LCD como "No funciona"
    driver.find_element(By.ID, "btn-marcar-todos-test").click()
    driver.find_element(
        By.CSS_SELECTOR, "#form-revision-tecnica input[name='test_LCD'][value='No funciona']"
    ).click()
    driver.find_element(
        By.CSS_SELECTOR, "#form-revision-tecnica textarea[name='observaciones']"
    ).send_keys(OBSERVACIONES)

    driver.find_element(By.CSS_SELECTOR, "#form-revision-tecnica button[type='submit']").click()

    # --- Feedback global de exito: taller.js no muestra mensaje propio al
    # guardar la revision; el interceptor de feedback-modal.js muestra el
    # modal generico de exito para el POST a /api/taller/guardar-revision ---
    _, mensaje = esperar_feedback(
        espera,
        tipo="success",
        titulo="Acción exitosa",
        mensaje="Registro realizado satisfactoriamente.",
    )

    # --- Verificar la confirmacion: al guardar, el JS vuelve a la vista-2
    # y recarga el detalle; debe aparecer el nuevo test (#2) ---
    espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//div[@id='order-tests']//span[contains(normalize-space(.), 'Test #2')]",
            )
        )
    )

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Revisión técnica guardada en el taller: test #2 registrado en la orden "
        f"{id_orden} (feedback: {mensaje})"
    )
