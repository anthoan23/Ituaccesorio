# Prerequisito: /admin/reportes-ventas lista las ventas (facturas) generadas
# por el flujo de carrito/procesar-pago y las ventas locales. La prueba aplica
# un filtro visible del formulario (select de método de pago) y genera el
# reporte; acepta filas con ese método o el mensaje de vacío del JS ("No hay
# ventas con esos filtros"); no falla por falta de datos. Nota: se usa el
# select de método porque los inputs type="date" dependen del locale del
# navegador y send_keys es ambiguo con ellos. Se asume ENTORNO_PRUEBA=true.
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

URL_REPORTES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/admin/reportes-ventas"
TIEMPO_ESPERA = 10

# [metodo de pago]
DATOS_FILTRO = ["efectivo_usd"]


def test_filtrar_reportes(driver):
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

    # Aplica el filtro de método de pago (select con opciones)
    Select(driver.find_element(By.ID, "reporte-metodo")).select_by_value(
        DATOS_FILTRO[0]
    )
    espera.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".custom-toast")))
    driver.find_element(By.ID, "btn-generar-reporte").click()
    espera.until(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, ".custom-toast"), "Reporte generado"
        )
    )
    espera.until(reporte_cargado)
    espera.until(EC.visibility_of_element_located((By.ID, "reporte-resumen")))

    # La tabla se actualizó con el filtro: filas con ese método o vacío
    filas = driver.find_elements(By.CSS_SELECTOR, "#reporte-tabla tr")
    if driver.find_elements(By.CSS_SELECTOR, "#reporte-tabla .btn-ver-detalle-reporte"):
        for fila in filas:
            metodo = fila.find_element(By.CSS_SELECTOR, "td:nth-child(4)").text
            assert (
                DATOS_FILTRO[0] in metodo
            ), f"Fila con método inesperado tras el filtro: {metodo}"
        print(f"Filtro aplicado: {len(filas)} filas con método '{DATOS_FILTRO[0]}'")
    else:
        print("Filtro aplicado sin resultados (mensaje de vacío del JS)")
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Reporte filtrado por método de pago '{DATOS_FILTRO[0]}'")
