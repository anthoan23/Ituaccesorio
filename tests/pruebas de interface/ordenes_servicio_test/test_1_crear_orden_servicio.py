import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_ORDENES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/ordenes-servicio"
TIEMPO_ESPERA = 10

# ----------------------------------------------------------------------
# Prueba de interface: crear una orden de servicio desde /ordenes-servicio.
# AUTOCONTENIDA: registra una orden temporal (flujo minimo: modal "Nueva
# orden" + modal "Revision inicial" que el JS abre automaticamente).
# El registro queda persistido en la BD (no se elimina al terminar; la
# pagina no ofrece eliminacion de ordenes).
# Datos fijos: si el cliente o el equipo ya existen, el controlador/JS los
# reutiliza en lugar de duplicarlos.
# MECANISMO DE FEEDBACK: ordenes_servicio.js NO muestra feedback propio
# (Utils.showMessage solo escribe en la consola); el unico feedback visible
# es el del interceptor global de fetch para el POST de la orden: titulo
# 'Accion exitosa' y mensaje generico.
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


def crear_orden_servicio_ui(driver, espera):
    """Crea una orden de servicio por la UI (flujo minimo: revision inicial
    con todos los componentes OK) y devuelve la fila de la tabla."""
    driver.get(URL_ORDENES)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # El select de modelos se llena por API; se espera a que tenga opciones
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
    # Si el cliente no existia, el POST /api/clientes abre el feedback-modal
    # encima del modal de revision: esperar su autocierre antes de confirmar
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    driver.find_element(By.ID, "btn-confirmar-revision").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-revision-inicial")))
    # El JS no muestra feedback propio; el interceptor global muestra el suyo
    esperar_feedback(
        espera, tipo="success", titulo="Acción exitosa", mensaje="Registro realizado satisfactoriamente."
    )

    # La orden recien creada es la primera de la tabla (ORDER BY ID DESC)
    return espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//tbody[@id='tabla-ordenes']/tr[td[4][normalize-space(.)='{DATOS_ORDEN[0]}']][1]",
            )
        )
    )


def test_crear_orden_servicio(driver):
    # --- Verificaciones visuales de la pagina ---
    driver.get(URL_ORDENES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    assert driver.title == "Ituaccesorio - Órdenes de servicio"
    assert espera.until(
        lambda d: d.find_element(By.CSS_SELECTOR, ".hero__title").text
    ) == "Órdenes de servicio"
    # textContent: el CSS renderiza el eyebrow en mayusculas
    assert driver.find_element(By.CSS_SELECTOR, ".hero__eyebrow").get_attribute("textContent").strip() == (
        "Gestión del taller"
    )
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Órdenes de servicio"
    labels_stats = [
        elemento.get_attribute("textContent").strip()
        for elemento in driver.find_elements(By.CSS_SELECTOR, ".stat-card__label")
    ]
    assert labels_stats == ["Pendientes", "Asignadas", "Reparadas"]

    # --- Card principal: titulo, botonera y encabezados ---
    assert driver.find_element(
        By.CSS_SELECTOR, ".ordenes-table-card .card__title"
    ).get_attribute("textContent").strip() == "Órdenes registradas"
    quitar_hover(driver)
    boton_asignar_header = driver.find_element(By.ID, "btn-asignar-tecnico")
    assert boton_asignar_header.text.strip() == "Asignar"
    assert estilo_css(driver, boton_asignar_header, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Asignar' deberia ser el amarillo primario"
    )
    boton_nueva = driver.find_element(By.ID, "btn-nueva-orden")
    assert boton_nueva.text.strip() == "Nueva orden"
    assert estilo_css(driver, boton_nueva, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Nueva orden' deberia ser el amarillo primario"
    )
    assert estilo_css(driver, boton_nueva, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Nueva orden' deberia ser oscuro"
    )
    encabezados = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, ".ordenes-table-card .table thead th")
    ]
    assert encabezados == ["ID orden", "Estado", "Cliente", "Equipo", "Modelo", "Fecha ingreso", "Acciones"]

    # --- Modal 'Nueva orden de servicio': titulo, labels y botones ---
    boton_nueva.click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-nueva-orden")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-nueva-orden-title").text == "Nueva orden de servicio"
    label_imei = driver.find_element(
        By.XPATH, "//label[.//input[@id='orden-id-equipo']]/span"
    ).get_attribute("textContent").strip()
    assert label_imei == "IMEI *"
    label_descripcion = driver.find_element(
        By.XPATH, "//label[.//textarea[@id='orden-descripcion']]/span"
    ).get_attribute("textContent").strip()
    assert label_descripcion == "Descripción del problema *"
    boton_cancelar = driver.find_element(By.CSS_SELECTOR, "#modal-nueva-orden [data-close-modal]")
    assert boton_cancelar.text.strip() == "Cancelar"
    assert "ui-btn--ghost" in boton_cancelar.get_attribute("class")
    boton_guardar = driver.find_element(By.CSS_SELECTOR, "#form-orden-servicio button[type='submit']")
    assert boton_guardar.text.strip() == "Guardar orden"
    assert estilo_css(driver, boton_guardar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Guardar orden' deberia ser el amarillo primario"
    )

    # --- Datos del equipo y del cliente (el JS los reutiliza si ya existen) ---
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

    # --- Guardar: el JS cierra este modal y abre el de revision inicial ---
    boton_guardar.click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-revision-inicial")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Modal 'Revision inicial del equipo': titulo, subtitulo y botones ---
    assert driver.find_element(By.ID, "modal-revision-inicial-title").text == "Revisión inicial del equipo"
    assert driver.find_element(
        By.CSS_SELECTOR, "#modal-revision-inicial .revision-subtitle"
    ).get_attribute("textContent").strip() == "Registro del estado inicial del equipo"
    boton_ok = driver.find_element(By.ID, "btn-marcar-todos-test")
    assert boton_ok.text.strip() == "✅ Marcar todos como OK"
    assert "ui-btn--ghost" in boton_ok.get_attribute("class")
    boton_falla = driver.find_element(By.ID, "btn-marcar-todos-fallo")
    assert boton_falla.text.strip() == "❌ Marcar todos como No funciona"
    boton_confirmar = driver.find_element(By.ID, "btn-confirmar-revision")
    assert boton_confirmar.text.strip() == "Confirmar y guardar orden"
    assert estilo_css(driver, boton_confirmar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Confirmar y guardar orden' deberia ser el amarillo primario"
    )

    # --- Confirmar la revision inicial (todos los componentes OK por defecto) ---
    boton_confirmar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-revision-inicial")))

    # --- Feedback visible: solo el del interceptor global (el JS del modulo
    #     no muestra nada en pantalla; Utils.showMessage va a la consola) ---
    espera.until(
        lambda d: d.find_element(By.ID, "feedback-modal-title").text.strip() == "Acción exitosa"
    )
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo="Acción exitosa", mensaje="Registro realizado satisfactoriamente."
    )

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
    badge_estado = fila.find_element(By.CSS_SELECTOR, "td.col-estado .badge")
    # textContent: el CSS pinta el badge en mayusculas
    assert badge_estado.get_attribute("textContent").strip() == "Pendiente"
    assert "badge--pendiente" in badge_estado.get_attribute("class")
    cliente = fila.find_element(By.CSS_SELECTOR, "td.col-cliente").get_attribute("textContent").strip()
    modelo = fila.find_element(By.CSS_SELECTOR, "td.col-modelo").get_attribute("textContent").strip()
    assert cliente == f"{DATOS_CLIENTE[1]} {DATOS_CLIENTE[2]}"
    assert modelo == DATOS_ORDEN[1]

    # --- Iconos de la fila: ver detalle (azul) y asignar tecnico (amarillo) ---
    quitar_hover(driver)
    assert estilo_css(
        driver, fila.find_element(By.CSS_SELECTOR, "button[data-action='ver-detalle']"), "borderTopColor"
    ) == "rgb(0, 122, 255)", "El icono 'ver detalle' de la fila deberia ser azul"
    assert estilo_css(
        driver, fila.find_element(By.CSS_SELECTOR, "button[data-action='seleccionar-asignacion']"), "borderTopColor"
    ) == "rgb(243, 197, 0)", "El icono 'asignar tecnico' de la fila deberia ser amarillo"

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Orden de servicio creada: {id_orden} (IMEI {DATOS_ORDEN[0]}, cliente {cliente}; "
        f"feedback del interceptor: {mensaje})"
    )
