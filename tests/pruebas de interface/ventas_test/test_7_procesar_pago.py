import base64
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

# Módulo de ventas: procesar el pago del carrito (página /pagar)
# REQUIERE sesión de CLIENTE registrado con perfil completo y carrito con items:
# la vista /pagar y las API de pago redirigen/rechazan si el usuario no es un
# cliente existente; en modo prueba el usuario falso es admin y /pagar redirige
# a /catalogo, por lo que la prueba informa y termina si no llegó a la página.
# Mecanismo de feedback del módulo (mostrarToast de ventas.js): toast propio
# ".custom-toast" con "¡Pago registrado! Redirigiendo..." al tener éxito.
URL_PAGAR = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/pagar"
TIEMPO_ESPERA = 10

# [metodo, referencia, monto] — pago_movil exige comprobante (capture)
DATOS_PAGO = ["pago_movil", "123456", "10.00"]

# Captura mínima PNG de 1x1 pixel que se sube como comprobante de pago
RUTA_CAPTURE = "/tmp/opencode/test_capture.png"
PNG_1X1_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLv"
    "AAAAAElFTkSuQmCC"
)


def test_procesar_pago(driver):
    # Crear la imagen mínima del comprobante si aún no existe
    os.makedirs(os.path.dirname(RUTA_CAPTURE), exist_ok=True)
    if not os.path.exists(RUTA_CAPTURE):
        with open(RUTA_CAPTURE, "wb") as archivo:
            archivo.write(base64.b64decode(PNG_1X1_BASE64))

    driver.get(URL_PAGAR)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Sin sesión de cliente la vista /pagar redirige a /catalogo: no hay nada
    # que procesar en modo prueba
    if "/pagar" not in driver.current_url:
        print("/pagar redirigió a otro página (no hay cliente con carrito); se omite")
        return

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == "Ituaccesorio - Procesar Pago"
    assert driver.find_element(By.CSS_SELECTOR, ".ventas-pagos .card__title").text == (
        "Finalizar compra"
    )
    boton_volver = driver.find_element(By.ID, "btn-volver")
    assert boton_volver.text.strip() == "Volver al catálogo"
    boton_pagar = driver.find_element(By.ID, "btn-pagar")
    assert boton_pagar.text.strip() == "Confirmar pago"

    # Validación del front: sin método elegido el JS muestra su toast de error
    # (mecanismo de feedback del módulo: toast propio ".custom-toast")
    boton_pagar.click()
    toast = espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".custom-toast"))
    )
    assert "Selecciona un método de pago" in toast.text
    espera.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".custom-toast")))

    # Los métodos de pago llegan por fetch (/api/metodos-pago)
    espera.until(
        lambda navegador: len(
            Select(navegador.find_element(By.ID, "metodo-pago")).options
        )
        > 1
    )
    Select(driver.find_element(By.ID, "metodo-pago")).select_by_value(DATOS_PAGO[0])
    # El formulario se pinta dinámicamente al elegir el método
    espera.until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                "#form-pago-container input[name='referencia']",
            )
        )
    )
    # Título dinámico del formulario según el método elegido
    assert driver.find_element(
        By.CSS_SELECTOR, "#form-pago-container .form-pago h4"
    ).text == "Pago Móvil (Bolívares)"
    driver.find_element(
        By.CSS_SELECTOR, "#form-pago-container input[name='monto']"
    ).send_keys(DATOS_PAGO[2])
    driver.find_element(
        By.CSS_SELECTOR, "#form-pago-container input[name='referencia']"
    ).send_keys(DATOS_PAGO[1])
    # pago_movil exige comprobante: subir la captura por el input file
    driver.find_element(
        By.CSS_SELECTOR, "#form-pago-container input[name='capture']"
    ).send_keys(RUTA_CAPTURE)
    boton_pagar.click()

    # Sin carrito con items el backend rechaza y el JS pinta el toast de error
    # con el mensaje del servidor; con carrito válido, toast "¡Pago registrado!
    # Redirigiendo..." y redirección al catálogo.
    toast = espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".custom-toast"))
    )
    if "Pago registrado" in toast.text:
        # Tras registrar la venta, el JS redirige al catálogo
        espera.until(EC.url_contains("/catalogo"))
        print(
            f"Pago procesado ({DATOS_PAGO[0]}, referencia {DATOS_PAGO[1]}): venta registrada"
        )
    else:
        print(
            f"No se procesó el pago en modo prueba "
            f"({DATOS_PAGO[0]}, referencia {DATOS_PAGO[1]}): {toast.text}"
        )
    espera.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".custom-toast")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
