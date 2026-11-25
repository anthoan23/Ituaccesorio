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

from helpers import estilo_css, quitar_hover

URL_REPORTES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/admin/reportes-ventas"
TIEMPO_ESPERA = 10


def test_listar_reportes(driver):
    driver.get(URL_REPORTES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == "Ituaccesorio - Reportes de Ventas"
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == (
        "Reportes de Ventas"
    )
    assert espera.until(
        lambda d: d.find_element(By.CSS_SELECTOR, ".hero__title").text
    ) == "Reportes de Ventas"

    # Boton 'Nueva Venta Local' del héroe: fondo amarillo con texto oscuro
    boton_venta_local = driver.find_element(By.ID, "btn-venta-local")
    assert boton_venta_local.text.strip() == "Nueva Venta Local"
    assert "ui-btn--primary" in boton_venta_local.get_attribute("class")
    assert estilo_css(driver, boton_venta_local, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Nueva Venta Local' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_venta_local, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Nueva Venta Local' deberia ser oscuro"
    )

    # Pestañas: la activa queda amarilla con texto oscuro
    tabs = driver.find_elements(By.CSS_SELECTOR, ".tab-btn")
    assert [t.get_attribute("textContent").strip() for t in tabs] == [
        "Reportes", "Ventas Locales"
    ]
    tab_activa = driver.find_element(By.CSS_SELECTOR, ".tab-btn.is-active")
    assert tab_activa.get_attribute("textContent").strip() == "Reportes"
    assert estilo_css(driver, tab_activa, "backgroundColor") == "rgb(243, 197, 0)", (
        "La pestaña activa deberia tener fondo amarillo"
    )

    # Encabezados de la tabla de resultados (textContent, el CSS los renderiza en mayusculas)
    encabezados = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, "#reportes-tab .table thead th")
    ]
    assert encabezados == [
        "Factura", "Cliente", "Fecha", "Método", "Referencia", "Monto", "Estado", "Acción"
    ]

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
    quitar_hover(driver)
    boton_generar = driver.find_element(By.ID, "btn-generar-reporte")
    assert boton_generar.text.strip() == "Generar reporte"
    assert estilo_css(driver, boton_generar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Generar reporte' deberia ser amarillo"
    )
    boton_generar.click()

    # Mecanismo de feedback del módulo (mostrarToast de reportes_ventas.js):
    # toast propio ".custom-toast" con el texto dinamico "Reporte generado: N transacciones"
    espera.until(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, ".custom-toast"), "Reporte generado: "
        )
    )
    toast = driver.find_element(By.CSS_SELECTOR, ".custom-toast")
    assert "transacciones" in toast.text
    espera.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".custom-toast")))

    espera.until(reporte_cargado)
    espera.until(EC.visibility_of_element_located((By.ID, "reporte-resumen")))

    # Resumen del reporte: etiquetas (textContent, el CSS las renderiza en mayusculas)
    etiquetas_resumen = [
        el.get_attribute("textContent").strip()
        for el in driver.find_elements(By.CSS_SELECTOR, "#reporte-resumen .stat-summary__label")
    ]
    assert etiquetas_resumen == [
        "Total transacciones", "Monto total", "Pendientes", "Aprobados", "Rechazados"
    ]

    filas = driver.find_elements(By.CSS_SELECTOR, "#reporte-tabla .btn-ver-detalle-reporte")
    if filas:
        # El botón 'Ver' de cada fila es amarillo (reportes_ventas.css pisa el ghost)
        boton_ver = filas[0]
        assert boton_ver.text.strip() == "Ver"
        assert estilo_css(driver, boton_ver, "backgroundColor") == "rgb(243, 197, 0)", (
            "El fondo del botón 'Ver' deberia ser amarillo"
        )
        print(f"Reporte generado con {len(filas)} ventas listadas")
    else:
        print("Reporte generado sin ventas (mensaje de vacío del JS)")
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print("Listado de reportes de ventas cargado correctamente")
