import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

URL_INVENTARIO = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/inventario"
TIEMPO_ESPERA = 10


def test_reporte_inventario(driver):
    driver.get(URL_INVENTARIO)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#inventario-tbody tr td .status")
        )
    )

    # --- Boton 'Reportes' de la card: estilo fantasma del tema oscuro ---
    boton_reportes = driver.find_element(By.ID, "btn-reportes")
    assert boton_reportes.text.strip() == "Reportes"
    assert "ui-btn--ghost" in boton_reportes.get_attribute("class")
    assert estilo_css(driver, boton_reportes, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Reportes' deberia ser el ghost del tema oscuro"
    assert estilo_css(driver, boton_reportes, "color") == "rgb(255, 255, 255)", (
        "El texto de 'Reportes' deberia ser blanco"
    )

    # Abrir el modal de reportes (el JS carga clases y marcas para los filtros)
    boton_reportes.click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-reportes")))
    quitar_hover(driver)

    # --- Modal 'Reporte de inventario': titulo, labels y botones ---
    assert driver.find_element(By.ID, "modal-reportes-title").text == "Reporte de inventario"
    labels = [
        el.get_attribute("textContent").strip()
        for el in driver.find_elements(By.CSS_SELECTOR, "#modal-reportes .field > span")
    ]
    assert labels == ["Búsqueda", "Clase", "Marca", "Stock mínimo", "Stock máximo"]

    boton_generar = driver.find_element(By.ID, "btn-generar-reporte")
    assert boton_generar.text.strip() == "Generar reporte"
    assert "ui-btn--primary" in boton_generar.get_attribute("class")
    assert estilo_css(driver, boton_generar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Generar reporte' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_generar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Generar reporte' deberia ser oscuro"
    )

    boton_limpiar = driver.find_element(By.ID, "btn-limpiar-filtros")
    assert boton_limpiar.text.strip() == "Limpiar filtros"
    assert "ui-btn--ghost" in boton_limpiar.get_attribute("class")
    assert estilo_css(driver, boton_limpiar, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Limpiar filtros' deberia ser el ghost del tema oscuro"

    # Generar el reporte (POST /api/inventario/reportes)
    boton_generar.click()

    # El JS muestra el preview con el total y las filas del reporte
    espera.until(EC.visibility_of_element_located((By.ID, "reporte-preview")))
    espera.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#reporte-tabla tr"))
    )
    total_texto = driver.find_element(By.ID, "reporte-total").text
    # Texto dinamico del JS: "Total de productos: N"
    assert total_texto.startswith("Total de productos: "), total_texto

    # Encabezados de la tabla del reporte (textContent, el CSS los renderiza en mayusculas)
    encabezados = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, "#modal-reportes .table--min thead th")
    ]
    assert encabezados == ["Imagen", "Producto", "Marca", "Clase", "Stock", "Costo", "Estado"]

    filas = driver.find_elements(By.CSS_SELECTOR, "#reporte-tabla tr")
    assert filas, "La tabla del reporte quedó vacía"
    sin_datos = any("No hay productos" in fila.text for fila in filas)
    if not sin_datos:
        total = int(total_texto.split(":")[-1].strip())
        assert len(filas) == total
        # Con datos, los botones de exportación quedan habilitados
        assert driver.find_element(By.ID, "btn-exportar-excel").get_attribute(
            "disabled"
        ) is None

    # --- Estilos de los botones de exportacion del preview ---
    boton_excel = driver.find_element(By.ID, "btn-exportar-excel")
    assert boton_excel.text.strip() == "Excel"
    assert "ui-btn--success" in boton_excel.get_attribute("class")
    assert estilo_css(driver, boton_excel, "color") == "rgb(34, 197, 94)", (
        "El texto de 'Excel' deberia ser verde"
    )
    boton_pdf = driver.find_element(By.ID, "btn-exportar-pdf")
    assert boton_pdf.text.strip() == "PDF"
    assert "ui-btn--danger" in boton_pdf.get_attribute("class")
    assert estilo_css(driver, boton_pdf, "color") == "rgb(239, 68, 68)", (
        "El texto de 'PDF' deberia ser rojo"
    )
    boton_imprimir = driver.find_element(By.ID, "btn-imprimir")
    assert boton_imprimir.text.strip() == "Imprimir"
    assert "ui-btn--ghost" in boton_imprimir.get_attribute("class")

    # Cerrar el modal con la × para no pisar la siguiente prueba
    driver.find_element(By.CSS_SELECTOR, "#modal-reportes .ui-modal__close").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-reportes")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # Mecanismo de feedback del JS de reportes de inventario (notifyReportes):
    # FeedbackModal con titulos 'Acción exitosa' / 'No se pudo completar'; solo
    # aparece en errores, por eso solo se espera su desaparición aquí.
    print(f"Reporte de inventario generado: {total_texto}")
