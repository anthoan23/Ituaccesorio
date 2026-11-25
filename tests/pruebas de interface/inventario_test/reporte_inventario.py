import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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

    # Abrir el modal de reportes (el JS carga clases y marcas para los filtros)
    driver.find_element(By.ID, "btn-reportes").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-reportes")))

    # Generar el reporte (POST /api/inventario/reportes)
    driver.find_element(By.ID, "btn-generar-reporte").click()

    # El JS muestra el preview con el total y las filas del reporte
    espera.until(EC.visibility_of_element_located((By.ID, "reporte-preview")))
    espera.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#reporte-tabla tr"))
    )
    total_texto = driver.find_element(By.ID, "reporte-total").text
    assert "Total de productos:" in total_texto

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

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Reporte de inventario generado: {total_texto}")
