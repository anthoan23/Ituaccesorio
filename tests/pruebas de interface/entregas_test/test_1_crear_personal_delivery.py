import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

# Módulo de entregas: registrar personal de delivery (pestaña "Personal Delivery")
# Nota: la cédula del delivery debe existir como empleado registrado en la BD
# (los campos del modal son libres: cédula, nombre y apellido).
# MECANISMO DE FEEDBACK: toast propio del módulo (#toast, Utils.mostrarToast,
# visible ~3 s y se oculta solo); a la vez, el interceptor global de fetch
# abre su FeedbackModal generico sobre el POST.
URL_ENTREGAS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/entregas"
TIEMPO_ESPERA = 10

# [cedula, nombre, apellido] - la cadena crea/consulta/modifica/elimina este registro
DATOS_PERSONAL = ["30124556", "Personal", "Delivery"]

TITULO_PAGINA = "Ituaccesorio - Entregas"


def esperar_toast(espera, mensaje):
    """Espera el toast propio del modulo (#toast con .is-visible), valida su
    texto y espera su desaparicion (se oculta solo a los ~3 segundos)."""
    def toast_visible(d):
        toast = d.find_element(By.ID, "toast")
        if "is-visible" in (toast.get_attribute("class") or ""):
            return toast.text.strip() or False
        return False

    texto = espera.until(toast_visible)
    assert texto == mensaje, f"Toast inesperado: '{texto}' (se esperaba '{mensaje}')"
    espera.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "#toast.is-visible")))
    # El interceptor global tambien abre su FeedbackModal: esperar su autocierre
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    return texto


def test_crear_personal_delivery(driver):
    driver.get(URL_ENTREGAS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == TITULO_PAGINA
    assert espera.until(
        lambda d: d.find_element(By.CSS_SELECTOR, ".hero__title").text
    ) == "Administración de entregas"
    # textContent: el CSS renderiza el eyebrow y las etiquetas en mayusculas
    assert driver.find_element(By.CSS_SELECTOR, ".hero__eyebrow").get_attribute("textContent").strip() == (
        "Gestión de entregas"
    )
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Entregas"
    labels_stats = [
        elemento.get_attribute("textContent").strip()
        for elemento in driver.find_elements(By.CSS_SELECTOR, ".stat-card__label")
    ]
    assert labels_stats == ["Entregas registradas", "Personal Delivery", "Facturas pendientes"]

    # --- Pestañas: Entregas activa por defecto, Personal Delivery oculta ---
    tab_entregas = driver.find_element(By.ID, "tab-entregas")
    tab_personal = driver.find_element(By.ID, "tab-personal")
    assert tab_entregas.text.strip() == "Entregas"
    assert tab_personal.text.strip() == "Personal Delivery"
    assert tab_entregas.get_attribute("aria-selected") == "true"
    assert tab_personal.get_attribute("aria-selected") == "false"

    # --- Card de entregas: titulo, boton y encabezados de la tabla ---
    assert driver.find_element(
        By.CSS_SELECTOR, "#tab-panel-entregas .card__title"
    ).get_attribute("textContent").strip() == "Entregas registradas"
    boton_entrega = driver.find_element(By.ID, "btn-nueva-entrega")
    assert boton_entrega.text.strip() == "Registrar entrega"
    assert estilo_css(driver, boton_entrega, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Registrar entrega' deberia ser el amarillo primario"
    )
    encabezados_entregas = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, "#tab-panel-entregas .table thead th")
    ]
    assert encabezados_entregas == ["ID Entrega", "Factura", "Delivery", "Estado", "Dirección", "Fecha", "Acciones"]

    # --- Cambiar a la pestaña Personal Delivery ---
    tab_personal.click()
    espera.until(lambda d: d.find_element(By.ID, "tab-personal").get_attribute("aria-selected") == "true")
    assert driver.find_element(
        By.CSS_SELECTOR, "#tab-panel-personal .card__title"
    ).get_attribute("textContent").strip() == "Personal de delivery"
    boton_personal = driver.find_element(By.ID, "btn-nuevo-personal")
    assert boton_personal.text.strip() == "Registrar delivery"
    assert estilo_css(driver, boton_personal, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Registrar delivery' deberia ser el amarillo primario"
    )
    encabezados_personal = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, "#tab-panel-personal .table thead th")
    ]
    assert encabezados_personal == ["Cédula", "Nombre completo", "Acciones"]

    # --- Modal 'Registrar delivery': titulo, labels y botones ---
    boton_personal.click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-personal")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-personal-title").text == "Registrar delivery"
    labels = [
        label.get_attribute("textContent").strip()
        for label in driver.find_elements(By.CSS_SELECTOR, "#form-personal label.field > span")
    ]
    assert labels == ["Cédula *", "Nombre *", "Apellido *"]
    boton_cancelar = driver.find_element(By.CSS_SELECTOR, "#form-personal [data-close-modal]")
    assert boton_cancelar.text.strip() == "Cancelar"
    assert "ui-btn--ghost" in boton_cancelar.get_attribute("class")
    assert estilo_css(driver, boton_cancelar, "backgroundColor") == "rgba(255, 255, 255, 0.06)", (
        "El fondo de 'Cancelar' deberia ser el ghost del tema oscuro"
    )
    boton_limpiar = driver.find_element(By.CSS_SELECTOR, "#form-personal [data-reset-form]")
    assert boton_limpiar.text.strip() == "Limpiar"
    boton_guardar = driver.find_element(By.CSS_SELECTOR, "#form-personal button[type='submit']")
    assert boton_guardar.text.strip() == "Guardar delivery"
    assert estilo_css(driver, boton_guardar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Guardar delivery' deberia ser el amarillo primario"
    )
    assert estilo_css(driver, boton_guardar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Guardar delivery' deberia ser oscuro"
    )

    # --- Registrar el delivery de la cadena ---
    driver.find_element(By.ID, "personal-cedula").send_keys(DATOS_PERSONAL[0])
    driver.find_element(By.ID, "personal-nombre").send_keys(DATOS_PERSONAL[1])
    driver.find_element(By.ID, "personal-apellido").send_keys(DATOS_PERSONAL[2])
    boton_guardar.click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-personal")))

    # --- Toast propio del modulo con el mensaje del JS ---
    mensaje = esperar_toast(espera, "Delivery registrado exitosamente")

    # --- Fila creada: filtrar con el buscador de la tabla y verificarla ---
    buscador = driver.find_element(By.CSS_SELECTOR, "#tab-panel-personal .table-controls__input")
    buscador.send_keys(DATOS_PERSONAL[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-personal']//tr[td[1][contains(., '{DATOS_PERSONAL[0]}')]]",
            )
        )
    )
    nombre_fila = fila.find_element(By.CSS_SELECTOR, "td:nth-child(2)").get_attribute("textContent").strip()
    assert nombre_fila == f"{DATOS_PERSONAL[1]} {DATOS_PERSONAL[2]}"

    # --- Iconos de la fila: editar (amarillo) y eliminar (rojo) ---
    quitar_hover(driver)
    assert estilo_css(
        driver, fila.find_element(By.CSS_SELECTOR, "button[data-action='editar-personal']"), "borderTopColor"
    ) == "rgb(243, 197, 0)", "El icono 'editar' de la fila deberia ser amarillo"
    assert estilo_css(
        driver, fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar-personal']"), "borderTopColor"
    ) == "rgb(220, 38, 38)", "El icono 'eliminar' de la fila deberia ser rojo"

    print(
        f"Personal delivery creado: {nombre_fila} ({DATOS_PERSONAL[0]}) (toast: {mensaje})"
    )
