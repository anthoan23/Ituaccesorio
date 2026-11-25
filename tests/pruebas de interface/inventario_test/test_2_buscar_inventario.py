import os
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_INVENTARIO = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/inventario"
TIEMPO_ESPERA = 10


def test_buscar_inventario(driver):
    driver.get(URL_INVENTARIO)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # La vista solo tiene filtros rápidos por chip (no hay input de búsqueda)
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#inventario-tbody tr td .status")
        )
    )

    # --- Filtro por tipo 'Telefono': chip activo y nota del JS ---
    chip = driver.find_element(
        By.CSS_SELECTOR,
        ".hero__chips .chip[data-filter='tipo'][data-value='Telefono']",
    )
    assert chip.get_attribute("textContent").strip() == "Teléfonos"
    chip.click()

    # El JS re-renderiza la tabla y actualiza la nota con el filtro activo
    espera.until(
        lambda navegador: "Telefono"
        in navegador.find_element(By.ID, "inventario-note").text
    )

    chip_activo = driver.find_element(
        By.CSS_SELECTOR,
        ".hero__chips .chip[data-filter='tipo'][data-value='Telefono']",
    )
    assert "chip--active" in chip_activo.get_attribute("class")
    assert chip_activo.get_attribute("aria-pressed") == "true"

    # La cantidad mostrada en la nota coincide con las filas visibles
    nota = driver.find_element(By.ID, "inventario-note").text
    coincidencia = re.search(r"Mostrando (\d+) de (\d+) registros · Telefono\.", nota)
    assert coincidencia, f"La nota no refleja el filtro: {nota}"
    total_filtrado = int(coincidencia.group(1))

    filas = driver.find_elements(By.CSS_SELECTOR, "#inventario-tbody tr")
    filas_con_datos = [
        fila for fila in filas if fila.find_elements(By.CSS_SELECTOR, "td .status")
    ]
    assert len(filas_con_datos) == total_filtrado
    # Toda fila visible es de la clase filtrada (columna Clase)
    for fila in filas_con_datos:
        clase = fila.find_element(By.CSS_SELECTOR, "td:nth-child(2)")
        assert clase.get_attribute("textContent").strip() == "Telefono"

    # --- Filtro 'Bajo stock': la nota usa la etiqueta del chip ---
    chip_bajo = driver.find_element(
        By.CSS_SELECTOR, ".hero__chips .chip[data-filter='low']"
    )
    chip_bajo.click()
    espera.until(
        lambda navegador: "Bajo stock"
        in navegador.find_element(By.ID, "inventario-note").text
    )
    nota_bajo = driver.find_element(By.ID, "inventario-note").text
    assert "· Bajo stock." in nota_bajo

    # --- Volver a 'Todos': la nota queda sin filtro ---
    chip_todos = driver.find_element(By.CSS_SELECTOR, ".hero__chips .chip[data-filter='all']")
    chip_todos.click()
    espera.until(
        lambda navegador: "· Todos."
        in navegador.find_element(By.ID, "inventario-note").text
    )
    print(f"Inventario filtrado: {nota} -> {nota_bajo} -> {driver.find_element(By.ID, 'inventario-note').text}")
