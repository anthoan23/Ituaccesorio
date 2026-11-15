# Prerequisito: /admin/reportes-ventas lista las ventas (facturas) generadas
# por el flujo de carrito/procesar-pago y las ventas locales. El JS genera el
# reporte automáticamente al iniciar la página; la prueba ejercita además el
# botón "Generar reporte" con los filtros vacíos y acepta tanto las filas como
# el mensaje de vacío del JS ("No hay ventas con esos filtros"); no falla por
# falta de datos. Se asume ENTORNO_PRUEBA=true.
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_REPORTES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/admin/reportes-ventas"
TIEMPO_ESPERA = 10


def test_listar_reportes(driver):
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

    # Ejercita el botón "Generar reporte" con los filtros vacíos; el JS avisa
    # por toast cuando el reporte termina de generarse
    espera.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".custom-toast")))
    driver.find_element(By.ID, "btn-generar-reporte").click()
    espera.until(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, ".custom-toast"), "Reporte generado"
        )
    )
    espera.until(reporte_cargado)
    espera.until(EC.visibility_of_element_located((By.ID, "reporte-resumen")))

    filas = driver.find_elements(By.CSS_SELECTOR, "#reporte-tabla .btn-ver-detalle-reporte")
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    if filas:
        print(f"Reporte generado con {len(filas)} ventas listadas")
    else:
        print("Reporte generado sin ventas (mensaje de vacío del JS)")
    print("Listado de reportes de ventas cargado correctamente")
