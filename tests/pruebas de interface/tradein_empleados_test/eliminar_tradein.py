import os
import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

URL_TRADEIN_EMPLEADOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/empleados/tradein"
TIEMPO_ESPERA = 10

# Datos del trade-in modificado por modificar_tradein.py
IMEI_EQUIPO = "351111111111888"

# PRERREQUISITOS:
# - Ejecutar antes crear_tradein.py y modificar_tradein.py (este test elimina ese registro).
# - La eliminación requiere el permiso 'Trade-in' -> 'eliminar' (el rol admin lo tiene).


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


def test_eliminar_tradein(driver):
    driver.get(URL_TRADEIN_EMPLEADOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    _esperar_tabla_cargada(espera)
    _ver_todas_las_filas(driver, espera)

    fila, id_tradein = _encontrar_tradein_por_imei(driver, espera, IMEI_EQUIPO)
    assert fila is not None, (
        f"No se encontró el trade-in con IMEI {IMEI_EQUIPO} "
        "(ejecute primero crear_tradein.py)."
    )

    # Cerrar el detalle y pulsar eliminar en la fila correspondiente
    driver.find_element(By.CSS_SELECTOR, "#modal-detalle .ui-modal__close").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-detalle")))

    fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']").click()

    # Confirmación nativa del navegador (confirm() del JS)
    WebDriverWait(driver, TIEMPO_ESPERA).until(EC.alert_is_present()).accept()

    # La fila debe desaparecer de la tabla tras el DELETE
    espera.until(
        EC.invisibility_of_element_located((By.XPATH, f"//tr[@data-id='{id_tradein}']"))
    )

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Trade-in eliminado: {id_tradein} (IMEI {IMEI_EQUIPO})")
