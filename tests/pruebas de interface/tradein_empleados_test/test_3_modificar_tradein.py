import os
import time

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_TRADEIN_EMPLEADOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/empleados/tradein"
TIEMPO_ESPERA = 10

# Datos del trade-in creado por test_1_crear_tradein.py
IMEI_EQUIPO = "351111111111888"
VALOR_ACTUAL = "150.00"
VALOR_NUEVO = "175.00"

# PRERREQUISITOS:
# - Ejecutar antes test_1_crear_tradein.py (este test edita ese registro).
# - La cédula del usuario logueado se usa como ID de empleado al actualizar;
#   en modo prueba (ENTORNO_PRUEBA=true) se requiere una sesión con cédula.
#
# MECANISMO DE FEEDBACK DE ESTE MODULO: tradein_empleados.js NO usa el
# FeedbackModal global para sus propias acciones; muestra un toast propio
# (mostrarToast -> .custom-toast--success | --error, se autodestruye a los
# ~3.3 s) con el mensaje del servidor ("Trade-in actualizado correctamente").
# Ademas el interceptor global de feedback-modal.js envuelve window.fetch y
# muestra el modal de exito generico para todo PUT /api/... no excluido
# (titulo 'Acción exitosa', mensaje 'Actualización realizada
# satisfactoriamente.'), que tambien se verifica.


def _aceptar_confirmacion_nativa(driver, segundos=5):
    """Acepta el diálogo nativo confirm() si aparece (el IMEI ya existe en la BD)."""
    try:
        WebDriverWait(driver, segundos).until(EC.alert_is_present()).accept()
    except TimeoutException:
        pass  # No hay confirmación: el equipo es nuevo


def _esperar_tabla_cargada(espera):
    """Espera a que la tabla termine el fetch inicial (desaparece 'Cargando...')."""
    espera.until(
        EC.invisibility_of_element_located(
            (By.XPATH, "//tbody[@id='tradein-list']//td[contains(., 'Cargando...')]")
        )
    )


def _ver_todas_las_filas(driver, espera):
    """table-tools pagina la tabla a 10 filas; sube el tamaño de página a 100."""
    tamano = espera.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "select.table-controls__select"))
    )
    Select(tamano).select_by_value("100")


def _abrir_detalle_y_coincidir_imei(driver, espera, imei):
    """Abre el detalle de cada fila hasta hallar el trade-in con el IMEI dado.
    Devuelve (fila, id_tradein) o (None, None); deja el modal abierto si coincide."""
    for fila in driver.find_elements(By.CSS_SELECTOR, "#tradein-list tr[data-id]"):
        try:
            fila.find_element(By.CSS_SELECTOR, "button[data-action='ver']").click()
            espera.until(EC.visibility_of_element_located((By.ID, "modal-detalle")))
            id_tradein = fila.get_attribute("data-id")
            # Asegura que el detalle ya muestre los datos de ESTA fila (#<id>)
            espera.until(
                EC.text_to_be_present_in_element(
                    (By.ID, "detalle-contenido"), f"#{id_tradein}"
                )
            )
            contenido = driver.find_element(By.ID, "detalle-contenido").text
        except StaleElementReferenceException:
            return None, None  # La tabla se recargó; reintentar con filas nuevas
        if imei in contenido:
            return fila, id_tradein
        driver.find_element(By.CSS_SELECTOR, "#modal-detalle .ui-modal__close").click()
        espera.until(EC.invisibility_of_element_located((By.ID, "modal-detalle")))
    return None, None


def _encontrar_tradein_por_imei(driver, espera, imei, intentos=4):
    """Busca el trade-in por IMEI con reintentos mientras la tabla se recarga."""
    for _ in range(intentos):
        fila, id_tradein = _abrir_detalle_y_coincidir_imei(driver, espera, imei)
        if fila is not None:
            return fila, id_tradein
        time.sleep(1)  # Espera breve entre reintentos mientras la tabla se refresca
    return None, None


def test_modificar_tradein(driver):
    driver.get(URL_TRADEIN_EMPLEADOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    _esperar_tabla_cargada(espera)
    _ver_todas_las_filas(driver, espera)

    fila, id_tradein = _encontrar_tradein_por_imei(driver, espera, IMEI_EQUIPO)
    assert fila is not None, (
        f"No se encontró el trade-in con IMEI {IMEI_EQUIPO} "
        "(ejecute primero test_1_crear_tradein.py)."
    )

    # Cerrar el detalle y abrir el modal de edición desde la fila
    driver.find_element(By.CSS_SELECTOR, "#modal-detalle .ui-modal__close").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-detalle")))

    fila.find_element(By.CSS_SELECTOR, "button[data-action='editar']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-registrar")))

    # --- Al editar, el JS cambia el titulo del modal y el texto del boton ---
    quitar_hover(driver)
    assert driver.find_element(
        By.CSS_SELECTOR, "#modal-registrar .ui-modal__title"
    ).get_attribute("textContent").strip() == "Editar Trade-In"
    boton_guardar = driver.find_element(
        By.CSS_SELECTOR, "#form-registrar-tradein button[type='submit']"
    )
    assert boton_guardar.text.strip() == "Actualizar Trade-In"
    assert estilo_css(driver, boton_guardar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Actualizar Trade-In' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_guardar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Actualizar Trade-In' deberia ser oscuro"
    )

    # El modal de edición precarga los datos (fetch del detalle)
    espera.until(EC.text_to_be_present_in_element_value((By.ID, "id_equipo"), IMEI_EQUIPO))

    # Cambiar el valor pagado
    valor = driver.find_element(By.ID, "valor-pagado")
    valor.clear()
    valor.send_keys(VALOR_NUEVO)

    # Guardar los cambios
    boton_guardar.click()

    # Confirmación nativa: el equipo/IMEI ya existe y la UI pide reutilizarlo
    _aceptar_confirmacion_nativa(driver)

    # --- Toast propio del modulo: success verde con el mensaje del servidor ---
    toast = espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".custom-toast"))
    )
    assert "custom-toast--success" in toast.get_attribute("class"), (
        "El toast deberia ser de tipo success"
    )
    assert toast.text.strip() == "Trade-in actualizado correctamente"
    assert estilo_css(driver, toast, "backgroundColor") == "rgb(34, 197, 94)", (
        "El fondo del toast de exito deberia ser verde"
    )

    # --- Feedback global: el interceptor de feedback-modal.js muestra el
    # exito generico del PUT /api/tradein/<id> (ademas del toast) ---
    _, mensaje = esperar_feedback(
        espera,
        tipo="success",
        titulo="Acción exitosa",
        mensaje="Actualización realizada satisfactoriamente.",
    )

    # El toast se autodestruye a los ~3.3 s
    espera.until(lambda d: not d.find_elements(By.CSS_SELECTOR, ".custom-toast"))

    try:
        espera.until(EC.invisibility_of_element_located((By.ID, "modal-registrar")))
    except TimeoutException:
        raise AssertionError(
            "El trade-in no se actualizó (el modal sigue abierto). Verifique los "
            "prerrequisitos: sesión con cédula de empleado y datos precargados."
        )

    # La tabla se recarga; verificar el nuevo valor en la fila del trade-in
    fila_actualizada = espera.until(
        EC.presence_of_element_located(
            (By.XPATH, f"//tr[@data-id='{id_tradein}'][contains(., '${VALOR_NUEVO}')]")
        )
    )
    assert VALOR_NUEVO in fila_actualizada.text

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Trade-in modificado: {id_tradein} | Valor pagado {VALOR_ACTUAL} -> {VALOR_NUEVO} "
        f"(toast + feedback: {mensaje})"
    )
