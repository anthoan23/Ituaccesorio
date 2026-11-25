import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from helpers import estilo_css, quitar_hover

# Módulo de entregas: registrar una entrega (modal "Registrar entrega")
# PRERREQUISITO: al menos una factura pendiente (sin entrega asignada) en la BD
# y al menos un delivery registrado (el select ofrece los existentes; se elige
# la primera opción disponible de cada uno).
# La dirección incluye una marca unica por ejecución para que la fila nueva
# sea localizable aunque existan entregas previas de la misma factura; al
# final la entrega se elimina por la UI y la factura vuelve a pendientes
# (la BD queda como estaba).
# MECANISMO DE FEEDBACK: toast propio del módulo (#toast, Utils.mostrarToast);
# el interceptor global de fetch abre además su FeedbackModal sobre el POST/DELETE.
URL_ENTREGAS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/entregas"
TIEMPO_ESPERA = 10

# Dirección base de la entrega de prueba (sin '.' ni ',': el validador los filtra)
DIRECCION_BASE = "Av Principal Barquisimeto Prueba Interfaz"

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


def test_registrar_entrega(driver):
    driver.get(URL_ENTREGAS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificaciones visuales de la pestaña Entregas (activa por defecto) ---
    assert driver.title == TITULO_PAGINA
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Entregas"
    assert driver.find_element(By.ID, "tab-entregas").get_attribute("aria-selected") == "true"

    # --- Modal 'Registrar entrega': titulo, labels y botones ---
    # El botón pertenece a la pestaña Entregas; su JS carga las facturas
    # pendientes y el select de delivery antes de abrir el modal
    driver.find_element(By.ID, "btn-nueva-entrega").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-entrega")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-entrega-title").text == "Registrar entrega"
    labels = [
        label.get_attribute("textContent").strip()
        for label in driver.find_elements(By.CSS_SELECTOR, "#form-entrega label.field > span")
    ]
    assert labels == ["Factura *", "Delivery *", "Dirección de entrega *", "Estado"]
    boton_cancelar = driver.find_element(By.CSS_SELECTOR, "#form-entrega [data-close-modal]")
    assert boton_cancelar.text.strip() == "Cancelar"
    assert "ui-btn--ghost" in boton_cancelar.get_attribute("class")
    boton_limpiar = driver.find_element(By.CSS_SELECTOR, "#form-entrega [data-reset-form]")
    assert boton_limpiar.text.strip() == "Limpiar"
    boton_guardar = driver.find_element(By.CSS_SELECTOR, "#form-entrega button[type='submit']")
    assert boton_guardar.text.strip() == "Guardar entrega"
    assert estilo_css(driver, boton_guardar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Guardar entrega' deberia ser el amarillo primario"
    )
    assert estilo_css(driver, boton_guardar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Guardar entrega' deberia ser oscuro"
    )

    # --- Primera factura pendiente y primer delivery disponibles ---
    espera.until(
        lambda navegador: len(Select(navegador.find_element(By.ID, "factura-id")).options) > 1
    )
    espera.until(
        lambda navegador: len(Select(navegador.find_element(By.ID, "delivery-cedula")).options) > 1
    )
    select_factura = Select(driver.find_element(By.ID, "factura-id"))
    select_factura.select_by_index(1)
    factura_id = select_factura.first_selected_option.get_attribute("value")
    Select(driver.find_element(By.ID, "delivery-cedula")).select_by_index(1)

    # Dirección con marca unica por ejecución (sin '.' ni ',')
    direccion = f"{DIRECCION_BASE} {int(time.time())}"
    campo_direccion = driver.find_element(
        By.CSS_SELECTOR, "#form-entrega textarea[name='direccion']"
    )
    campo_direccion.clear()
    campo_direccion.send_keys(direccion)
    boton_guardar.click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-entrega")))

    # --- Toast propio del modulo con el mensaje del JS ---
    mensaje_registro = esperar_toast(espera, "Entrega registrada exitosamente")

    # --- La fila nueva: filtrar por la direccion unica y verificar su contenido ---
    buscador = driver.find_element(By.CSS_SELECTOR, "#tab-panel-entregas .table-controls__input")
    buscador.send_keys(direccion)
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-entregas']//tr[td[5][contains(., '{direccion}')]]",
            )
        )
    )
    assert fila.find_element(By.CSS_SELECTOR, "td:nth-child(2)").get_attribute("textContent").strip() == factura_id
    badge_estado = fila.find_element(By.CSS_SELECTOR, "td:nth-child(4) .estado-badge")
    # textContent: el CSS pinta el badge en mayusculas
    assert badge_estado.get_attribute("textContent").strip() == "Pendiente"
    direccion_mostrada = fila.find_element(By.CSS_SELECTOR, "td:nth-child(5)").get_attribute("textContent").strip()
    assert direccion_mostrada == direccion

    # --- Iconos de la fila: editar (amarillo) y eliminar (rojo) ---
    quitar_hover(driver)
    assert estilo_css(
        driver, fila.find_element(By.CSS_SELECTOR, "button[data-action='editar-entrega']"), "borderTopColor"
    ) == "rgb(243, 197, 0)", "El icono 'editar' de la fila deberia ser amarillo"
    assert estilo_css(
        driver, fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar-entrega']"), "borderTopColor"
    ) == "rgb(220, 38, 38)", "El icono 'eliminar' de la fila deberia ser rojo"

    # --- Limpieza: eliminar la entrega para que la factura vuelva a pendientes ---
    fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar-entrega']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-eliminar")))
    texto_confirmacion = driver.find_element(By.ID, "confirmar-mensaje").get_attribute("textContent")
    assert texto_confirmacion == "¿Estás seguro de que quieres eliminar esta entrega?"
    driver.find_element(By.ID, "btn-confirmar-eliminar").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-eliminar")))

    mensaje_eliminacion = esperar_toast(espera, "Entrega eliminada exitosamente")
    espera.until(
        EC.invisibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-entregas']//tr[td[5][contains(., '{direccion}')]]",
            )
        )
    )
    print(
        f"Entrega registrada y eliminada (limpieza): factura {factura_id}, dirección '{direccion}' "
        f"(toasts: '{mensaje_registro}' / '{mensaje_eliminacion}')"
    )
