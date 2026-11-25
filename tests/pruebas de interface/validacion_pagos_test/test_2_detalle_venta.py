# Prerequisito: /admin/validar-pagos opera sobre facturas con pago pendiente
# creadas previamente por el flujo de carrito/procesar-pago. La prueba abre el
# detalle inline de la PRIMERA tarjeta pendiente (botón "Ver productos", que
# consulta /api/validacion-pagos/venta/<factura>/detalle) y acepta tanto los
# productos como el mensaje de detalle vacío que pinta el JS ("No hay productos
# registrados en esta venta"); no falla por falta de datos. Si la consulta del
# detalle falla, la prueba sí falla (error real de la UI). Nota: el modal
# #modal-detalle-venta de esta página se abre desde el "Ver" del reporte de
# pagos y se cubre en reportes_ventas_test/.
# Se asume ENTORNO_PRUEBA=true.
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css

URL_VALIDACION = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/admin/validar-pagos"
TIEMPO_ESPERA = 10


def test_detalle_venta(driver):
    driver.get(URL_VALIDACION)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == "Ituaccesorio - Validación de Pagos"
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == (
        "Validación de Pagos"
    )

    # La lista de pendientes carga por fetch (tarjetas o mensaje de vacío)
    espera.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "#pendientes-list .pago-card[data-factura], #pendientes-list .empty-state",
            )
        )
    )
    tarjetas = driver.find_elements(
        By.CSS_SELECTOR, "#pendientes-list .pago-card[data-factura]"
    )
    if not tarjetas:
        print("No hay pagos pendientes; se omite el detalle (lista vacía)")
        return

    tarjeta = tarjetas[0]
    factura = tarjeta.get_attribute("data-factura")

    # --- Boton 'Ver productos': texto dinamico y color amarillo del tema ---
    boton_ver = tarjeta.find_element(By.CSS_SELECTOR, ".btn-ver-detalle")
    assert boton_ver.text.strip() == "Ver productos"
    assert estilo_css(driver, boton_ver, "color") == "rgb(243, 197, 0)", (
        "El texto de 'Ver productos' deberia ser amarillo"
    )

    # El detalle inline se consulta por fetch: espera los productos o su vacío
    boton_ver.click()
    espera.until(
        lambda navegador: navegador.find_elements(
            By.CSS_SELECTOR, f"#detalle-{factura} .producto-item"
        )
        or navegador.find_elements(
            By.CSS_SELECTOR, f"#detalle-{factura} .empty-detalle"
        )
    )
    # El JS cambia el texto del mismo boton cuando el detalle queda abierto
    assert tarjeta.find_element(By.CSS_SELECTOR, ".btn-ver-detalle").text.strip() == (
        "Ocultar productos"
    )

    items = driver.find_elements(
        By.CSS_SELECTOR, f"#detalle-{factura} .producto-item"
    )
    if items:
        print(f"Detalle de la venta {factura} con {len(items)} productos")
    else:
        print(
            f"Detalle de la venta {factura} sin productos registrados (mensaje de vacío)"
        )

    # Cierra el detalle con el mismo botón ("Ocultar productos")
    tarjeta.find_element(By.CSS_SELECTOR, ".btn-ver-detalle").click()
    espera.until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, f"#detalle-{factura}"))
    )
    # El texto del botón vuelve al estado inicial
    assert tarjeta.find_element(By.CSS_SELECTOR, ".btn-ver-detalle").text.strip() == (
        "Ver productos"
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Detalle de la venta {factura} abierto y cerrado")
