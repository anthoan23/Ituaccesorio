import base64
import os
import time

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

URL_TRADEIN_EMPLEADOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/empleados/tradein"
TIEMPO_ESPERA = 10

# Datos de prueba (en español)
IMEI_EQUIPO = "351111111111888"  # 15 dígitos
VALOR_PAGADO = "150.00"
COLOR = "Negro"
CAPACIDAD = "128GB"
CLAVE_EQUIPO = "1234"
PATRON_EQUIPO = "2589"
BUSQUEDA_CLIENTE = "Prueba"  # búsqueda principal del cliente en el modal
BUSQUEDA_RESPALDO = "an"     # búsqueda amplia (mínimo 2 caracteres) si no hay coincidencias
TEST_NOMBRE = "Mica"         # prueba del catálogo de /api/tradein/catalogo-tests
TEST_RESULTADO = "Funciona"
RUTA_FOTO = "/tmp/opencode/test_foto_tradein.png"
PNG_FOTO_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

# PRERREQUISITOS:
# - Orden de ejecución: crear -> consultar -> modificar -> eliminar.
# - La BD debe tener productos iPhone (clase Telefono) y clientes registrados
#   (el buscador de clientes necesita resultados reales para elegir uno).
# - El registro usa la cédula del usuario logueado como ID de empleado
#   (Trade_in.ID_empleado, FK a Empleado). En modo prueba (ENTORNO_PRUEBA=true)
#   el usuario inyectado no trae cédula, por lo que se requiere una sesión real.


def _crear_foto_prueba():
    """Crea una imagen PNG mínima (base64) para el input de fotos."""
    carpeta = os.path.dirname(RUTA_FOTO)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    with open(RUTA_FOTO, "wb") as archivo:
        archivo.write(base64.b64decode(PNG_FOTO_BASE64))
    return RUTA_FOTO


def _seleccionar_primer_cliente(driver, espera):
    """Busca el cliente en el modal y elige el primer resultado real.
    Devuelve el nombre completo del cliente elegido."""
    campo = driver.find_element(By.ID, "cliente-search-input")
    for consulta in (BUSQUEDA_CLIENTE, BUSQUEDA_RESPALDO):
        campo.clear()
        campo.send_keys(consulta)
        try:
            # Los resultados reales traen data-id (el mensaje "No se encontraron
            # clientes" usa la misma clase pero sin data-id)
            resultado = espera.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#cliente-results .search-result-item[data-id]")
                )
            )
            nombre = resultado.get_attribute("data-nombre")
            resultado.click()
            return nombre
        except TimeoutException:
            continue  # Sin coincidencias para esta consulta; probar el respaldo
    raise AssertionError(
        "No hay clientes en la BD: no se pudo elegir un cliente para el trade-in."
    )


def _aceptar_confirmacion_nativa(driver, segundos=5):
    """Acepta el diálogo nativo confirm() si aparece (ej. reutilizar un IMEI ya registrado)."""
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


def test_crear_tradein(driver):
    driver.get(URL_TRADEIN_EMPLEADOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    _esperar_tabla_cargada(espera)
    _ver_todas_las_filas(driver, espera)

    # Abrir el modal de registro
    driver.find_element(By.ID, "btn-nuevo-tradein").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-registrar")))

    # Esperar los catálogos cargados por fetch: productos y pruebas del equipo
    try:
        espera.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#producto-id option:not([value=''])")
            )
        )
    except TimeoutException:
        raise AssertionError(
            "No hay productos iPhone disponibles para trade-in (el select quedó vacío)."
        )
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#tests-container-registro .test-item")
        )
    )

    # Cliente: primera opción del buscador
    nombre_cliente = _seleccionar_primer_cliente(driver, espera)

    # Producto: primera opción del select
    producto = Select(driver.find_element(By.ID, "producto-id"))
    producto.select_by_index(1)

    # Datos del equipo
    driver.find_element(By.ID, "id_equipo").send_keys(IMEI_EQUIPO)
    driver.find_element(By.ID, "color").send_keys(COLOR)
    driver.find_element(By.ID, "capacidad").send_keys(CAPACIDAD)
    driver.find_element(By.ID, "clave").send_keys(CLAVE_EQUIPO)
    driver.find_element(By.ID, "patron").send_keys(PATRON_EQUIPO)
    driver.find_element(By.ID, "valor-pagado").send_keys(VALOR_PAGADO)

    # Pruebas del equipo: marcar el resultado de una prueba del catálogo
    marcada = False
    for item in driver.find_elements(
        By.CSS_SELECTOR, "#tests-container-registro .test-item"
    ):
        if item.find_element(By.CSS_SELECTOR, ".test-nombre").text.strip() == TEST_NOMBRE:
            item.find_element(
                By.CSS_SELECTOR, f"input[type='radio'][value='{TEST_RESULTADO}']"
            ).click()
            marcada = True
            break
    assert marcada, f"No se encontró la prueba '{TEST_NOMBRE}' en el formulario."

    # Foto del equipo (PNG mínimo generado en runtime)
    driver.find_element(By.ID, "fotos").send_keys(_crear_foto_prueba())

    # Guardar el trade-in
    driver.find_element(
        By.CSS_SELECTOR, "#form-registrar-tradein button[type='submit']"
    ).click()

    # Si el IMEI ya existe en la BD, la UI muestra un confirm() nativo para reutilizarlo
    _aceptar_confirmacion_nativa(driver)

    try:
        espera.until(EC.invisibility_of_element_located((By.ID, "modal-registrar")))
    except TimeoutException:
        raise AssertionError(
            "El trade-in no se registró (el modal sigue abierto). Verifique los "
            "prerrequisitos: sesión con cédula de empleado, cliente y producto en la BD."
        )

    # La tabla se recarga tras guardar; verificar que el trade-in aparece
    fila, id_tradein = _encontrar_tradein_por_imei(driver, espera, IMEI_EQUIPO)
    assert fila is not None, f"El trade-in con IMEI {IMEI_EQUIPO} no aparece en la tabla."
    assert nombre_cliente in fila.text
    assert f"${VALOR_PAGADO}" in fila.text

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Trade-in registrado: {id_tradein} | Cliente: {nombre_cliente} "
        f"| Valor pagado: ${VALOR_PAGADO}"
    )
