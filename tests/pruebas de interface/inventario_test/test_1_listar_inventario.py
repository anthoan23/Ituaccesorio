import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_INVENTARIO = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/inventario"
TIEMPO_ESPERA = 10


def test_listar_inventario(driver):
    driver.get(URL_INVENTARIO)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == "Ituaccesorio - Inventario"
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Inventario"
    assert espera.until(
        lambda d: d.find_element(By.CSS_SELECTOR, ".hero__title").text
    ) == "Inventario"
    # El eyebrow se renderiza en mayusculas por CSS: usar textContent del DOM
    assert (
        driver.find_element(By.CSS_SELECTOR, ".hero__eyebrow").get_attribute("textContent").strip()
        == "Gestión de inventario"
    )

    # Chips de filtro rapido que pinta la vista
    chips = [
        chip.get_attribute("textContent").strip()
        for chip in driver.find_elements(By.CSS_SELECTOR, ".hero__chips .chip")
    ]
    assert chips == ["Todos", "Teléfonos", "Pantallas", "Repuestos", "Bajo stock"]

    # Indicadores del hero: etiquetas (textContent, el CSS las renderiza en mayusculas)
    etiquetas = [
        el.get_attribute("textContent").strip()
        for el in driver.find_elements(By.CSS_SELECTOR, ".stat-card__label")
    ]
    assert etiquetas == ["Clases", "Marcas", "Productos", "Piezas en stock"]

    # Encabezados de la tabla principal (textContent, el CSS los renderiza en mayusculas)
    encabezados = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, ".inventory-table thead th")
    ]
    assert encabezados == [
        "Imagen", "Clase", "Marca", "Producto", "Existencia", "Costo venta", "Estado"
    ]

    # El JS pinta la tabla desde GET /api/inventario; cada fila de datos
    # lleva su badge de estado (la fila de carga inicial no lo tiene)
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#inventario-tbody tr td .status")
        )
    )

    filas = driver.find_elements(By.CSS_SELECTOR, "#inventario-tbody tr")
    filas_con_datos = [
        fila for fila in filas if fila.find_elements(By.CSS_SELECTOR, "td .status")
    ]
    assert filas_con_datos, "La tabla de inventario no tiene filas de datos"
    for fila in filas_con_datos:
        assert fila.text.strip() != ""

    # Cada fila de datos muestra un badge de existencia y un estado con texto
    for fila in filas_con_datos[:3]:
        badge = fila.find_element(By.CSS_SELECTOR, "td:nth-child(5) .badge")
        assert badge.get_attribute("textContent").strip() != ""
        estado = fila.find_element(By.CSS_SELECTOR, "td:nth-child(7) .status")
        assert estado.get_attribute("textContent").strip() in (
            "Disponible", "Alto stock", "Bajo stock", "Sin stock", "Revisar"
        )

    # Los indicadores dejan de mostrar el marcador vacío
    stat_modelos = driver.find_element(By.ID, "inv-stat-modelos").text
    assert stat_modelos not in ("", "—")

    # Nota dinamica del JS: "Mostrando N de M registros · Todos."
    nota = espera.until(
        lambda d: "Mostrando " in d.find_element(By.ID, "inventario-note").text
        and d.find_element(By.ID, "inventario-note").text
    )
    assert nota.startswith("Mostrando "), f"La nota no refleja la carga: {nota}"
    assert "· Todos." in nota

    print(f"Inventario listado: {len(filas_con_datos)} filas con datos (nota: {nota})")
