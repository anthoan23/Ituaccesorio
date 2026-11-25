import base64
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

# Módulo de ventas: procesar el pago del carrito (página /pagar)
# REQUIERE sesión de CLIENTE registrado con perfil completo y carrito con items:
# la vista /pagar y las API de pago redirigen/rechazan si el usuario no es un
# cliente existente; en modo prueba el usuario falso es admin, por lo que esta
# prueba puede fallar en runtime.
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
    driver.find_element(By.ID, "btn-pagar").click()
    # Confirmación del JS: toast "¡Pago registrado! Redirigiendo..."
    toast = espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".custom-toast"))
    )
    assert "Pago registrado" in toast.text
    # Tras registrar la venta, el JS redirige al catálogo
    espera.until(EC.url_contains("/catalogo"))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Pago procesado ({DATOS_PAGO[0]}, referencia {DATOS_PAGO[1]}): venta registrada")
