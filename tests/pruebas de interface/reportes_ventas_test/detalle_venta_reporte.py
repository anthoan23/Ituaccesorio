# Prerequisito: /admin/reportes-ventas lista las ventas (facturas) generadas
# por el flujo de carrito/procesar-pago y las ventas locales. Si el reporte
# tiene filas, la prueba abre el detalle de la primera (botón "Ver", que
# consulta /api/reportes-ventas/detalle/<factura> y abre el modal
# #modal-detalle-venta con los datos de pago y los items), verifica el
# contenido y lo cierra con la × del modal. Si el reporte está vacío no falla:
# verifica la carga (el mensaje de vacío del JS es aceptable) y termina.
# Se asume ENTORNO_PRUEBA=true.
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_REPORTES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/admin/reportes-ventas"
TIEMPO_ESPERA = 10


def test_detalle_venta_reporte(driver):
    driver.get(URL_REPORTES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # El JS genera el reporte al iniciar: espera filas o su mensaje de vacío
    # (no el placeholder "Selecciona filtros y genera un reporte" de la plantilla)
    espera.until(EC.visibility_of_element_located((By.ID, "reporte-preview")))

    def reporte_cargado(navegador):
        tabla = navegador.find_element(By.ID, "reporte-tabla")
        if tabla.find_elements(By.CSS_SELECTOR, ".btn-ver-detalle-reporte"):
            return True
        return "No hay ventas con esos filtros" in tabla.text

    espera.until(reporte_cargado)
    botones = driver.find_elements(
        By.CSS_SELECTOR, "#reporte-tabla .btn-ver-detalle-reporte"
    )
    if not botones:
        print("No hay ventas en el reporte (mensaje de vacío); se omite el detalle")
        return

    # El detalle se consulta por fetch y se muestra en el modal de detalle
    botones[0].click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-detalle-venta")))
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#detalle-venta-info .detail-info-item")
        )
    )
    factura = driver.find_element(
        By.CSS_SELECTOR, "#detalle-venta-info .detail-info-item span"
    ).text
    total = driver.find_element(By.ID, "detalle-venta-total-amount").text
    assert total.strip(), "El detalle de la venta no muestra el total"
    productos = driver.find_elements(By.CSS_SELECTOR, "#detalle-venta-productos tr")

    # Cierra el modal con la × (botón data-close-modal del propio modal)
    driver.find_element(By.CSS_SELECTOR, "#modal-detalle-venta .ui-modal__close").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-detalle-venta")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Detalle de la venta {factura} consultado "
        f"({len(productos)} productos, total {total}) y cerrado"
    )
