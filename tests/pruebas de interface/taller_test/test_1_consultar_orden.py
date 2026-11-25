import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from helpers import estilo_css, quitar_hover

URL_ORDENES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/ordenes-servicio"
URL_TALLER = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/taller"
TIEMPO_ESPERA = 10

# ----------------------------------------------------------------------
# Prueba de interface: consultar el detalle de una orden desde el
# modulo Taller (/taller, boton "Ver orden" de la fila -> modal
# "Detalle de la orden" con orden + fotos + historial de tests).
# AUTOCONTENIDA: crea primero su propia orden temporal en
# /ordenes-servicio (flujo minimo) y luego la consulta en el taller. El
# registro queda persistido en la BD (no se elimina al terminar).
# Requisitos: ENTORNO_PRUEBA=true (decoradores desactivados) y BD
# sembrada con modelos de telefono. Este flujo funciona en modo prueba
# porque la consulta (/api/taller/consultar-ordene) no depende de
# g.user.get("cedula").
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


def test_consultar_orden_taller(driver):
    # ---------------------------------------------------------------
    # PASO 1: crear la orden temporal que se va a consultar
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
    # PASO 2: consultar la orden en el taller (modal de detalle)
    # ---------------------------------------------------------------
    driver.get(URL_TALLER)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificaciones visuales de la pagina (vista-1 "Ordenes de servicio") ---
    assert driver.title == "Ituaccesorio - Taller"
    assert espera.until(
        lambda d: d.find_element(By.CSS_SELECTOR, ".taller-hero__title").text
    ) == "Taller"
    assert driver.find_element(By.CSS_SELECTOR, ".taller-hero__description").text.strip() == (
        "Gestiona órdenes de servicio, revisiones y reparaciones."
    )
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Taller"

    # Conmutador de vistas: dos botones y solo el de ordenes activo
    switcher = driver.find_elements(
        By.XPATH, "//section[contains(@class,'vista-1')]//button[@data-view-target]"
    )
    assert [b.text.strip() for b in switcher] == [
        "Órdenes de servicio",
        "Reparaciones asignadas",
    ]
    assert "is-active" in switcher[0].get_attribute("class")
    assert "is-active" not in switcher[1].get_attribute("class")

    # Tarjeta de ordenes: titulo y subtitulo (textContent, el CSS los renderiza
    # en mayusculas en algunos casos)
    tarjeta = driver.find_element(By.XPATH, "//section[contains(@class,'vista-1')]")
    assert tarjeta.find_element(By.CSS_SELECTOR, ".card__title").get_attribute("textContent").strip() == (
        "Órdenes de servicio"
    )
    assert tarjeta.find_element(By.CSS_SELECTOR, ".card__subtitle").get_attribute("textContent").strip() == (
        "Lista de órdenes pendientes en el taller."
    )

    # Encabezados de la tabla de ordenes (textContent por el text-transform)
    encabezados = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, ".vista-1 .table thead th")
    ]
    assert encabezados == [
        "ID orden",
        "Estado",
        "ID cliente",
        "Nombre cliente",
        "Modelo",
        "Fecha ingreso",
        "Acciones",
    ]

    # table-tools pagina a 10 filas y oculta el resto: se filtra por el
    # buscador de la tarjeta para que la fila quede visible y clickeable
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
    assert fila.find_element(By.CSS_SELECTOR, ".estado-badge").text.strip() == "Pendiente"

    # --- Iconos de accion de la fila: ver (azul) y tomar orden (verde) ---
    quitar_hover(driver)
    boton_ver = fila.find_element(By.CSS_SELECTOR, "button[data-accion='ver-orden']")
    boton_tomar = fila.find_element(By.CSS_SELECTOR, "button[data-accion='tomar-orden']")
    assert boton_ver.get_attribute("aria-label") == "Ver orden"
    assert boton_tomar.get_attribute("aria-label") == "Tomar orden"
    assert estilo_css(driver, boton_ver, "borderTopColor") == "rgb(0, 122, 255)", (
        "El borde de 'Ver orden' deberia ser azul"
    )
    assert estilo_css(driver, boton_ver.find_element(By.TAG_NAME, "svg"), "color") == "rgb(0, 122, 255)", (
        "El icono de 'Ver orden' deberia ser azul"
    )
    assert estilo_css(driver, boton_tomar, "borderTopColor") == "rgb(34, 197, 94)", (
        "El borde de 'Tomar orden' deberia ser verde"
    )
    assert estilo_css(driver, boton_tomar.find_element(By.TAG_NAME, "svg"), "color") == "rgb(34, 197, 94)", (
        "El icono de 'Tomar orden' deberia ser verde"
    )

    boton_ver.click()

    # --- Modal 'Detalle de la orden': titulo, etiquetas y datos ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-preview-orden")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-preview-orden-title").text == "Detalle de la orden"
    # El detalle se carga por API; se espera a que se dibuje la informacion
    espera.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#modal-order-info .detail-group"))
    )
    etiquetas = [
        e.get_attribute("textContent").strip()
        for e in driver.find_elements(By.CSS_SELECTOR, "#modal-order-info .detail-label")
    ]
    assert etiquetas == [
        "ID de la Orden:",
        "Estado:",
        "Cliente:",
        "Modelo:",
        "Descripción:",
        "Nota:",
    ]

    # --- Verificar los datos de la orden en el modal ---
    info = driver.find_element(By.ID, "modal-order-info").text
    assert f"#{id_orden}" in info
    assert f"{DATOS_CLIENTE[1]} {DATOS_CLIENTE[2]}" in info
    assert DATOS_ORDEN[1] in info
    assert DATOS_ORDEN[5] in info

    # --- Verificar el historial de tests (la creacion registra el test #1) ---
    espera.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#modal-order-tests .tests-table-wrap"))
    )
    tests = driver.find_element(By.ID, "modal-order-tests").text
    assert "Historial de revisiones" in tests
    assert "Test #1" in tests

    # --- Boton 'Tomar orden': fondo amarillo con texto oscuro ---
    boton_tomar_modal = driver.find_element(By.ID, "modal-tomar-orden-btn")
    assert boton_tomar_modal.text.strip() == "Tomar orden"
    assert estilo_css(driver, boton_tomar_modal, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Tomar orden' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_tomar_modal, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Tomar orden' deberia ser oscuro"
    )

    # --- Boton 'Cancelar': estilo fantasma (ghost, colores del tema oscuro) ---
    boton_cancelar = driver.find_element(
        By.CSS_SELECTOR, "#modal-preview-orden .service-form__actions button[data-close-modal]"
    )
    assert boton_cancelar.text.strip() == "Cancelar"
    assert "ui-btn--ghost" in boton_cancelar.get_attribute("class")
    assert estilo_css(driver, boton_cancelar, "backgroundColor") == "rgba(255, 255, 255, 0.06)", (
        "El fondo de 'Cancelar' deberia ser el ghost del tema oscuro"
    )
    assert estilo_css(driver, boton_cancelar, "color") == "rgb(255, 255, 255)", (
        "El texto de 'Cancelar' deberia ser blanco"
    )

    boton_cancelar.click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-preview-orden")))

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Orden consultada en el taller: {id_orden} (orden + test #1 visibles en el modal)")
