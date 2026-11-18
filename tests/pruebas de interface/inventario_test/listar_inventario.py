import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_INVENTARIO = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/inventario"
TIEMPO_ESPERA = 10


def test_listar_inventario(driver):
    driver.get(URL_INVENTARIO)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

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

    # Los indicadores dejan de mostrar el marcador vacío
    stat_modelos = driver.find_element(By.ID, "inv-stat-modelos").text
    assert stat_modelos not in ("", "—")

    print(f"Inventario listado: {len(filas_con_datos)} filas con datos")
