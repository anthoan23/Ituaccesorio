import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_BITACORA = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/bitacora"
TIEMPO_ESPERA = 10

# Estructura esperada de la tabla de eventos (se pinta server-side con 'registros')
ENCABEZADOS_BITACORA = ["ID", "Usuario", "Acción", "Módulo", "Descripción", "Fecha/Hora"]


def test_listar_bitacora(driver):
    driver.get(URL_BITACORA)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Los registros viajan en el HTML (no hay fetch): el <tbody> ya trae las filas
    cuerpo = espera.until(EC.presence_of_element_located((By.ID, "tabla-bitacora")))

    # Estructura de la tabla según bitacora.html
    encabezados = [
        th.text.strip()
        for th in driver.find_elements(By.CSS_SELECTOR, ".bitacora-table thead th")
    ]
    assert encabezados == ENCABEZADOS_BITACORA

    filas = cuerpo.find_elements(By.CSS_SELECTOR, "tr.evento-row")
    if filas:
        # Cada fila de evento expone sus datos en atributos data-*
        primera = filas[0]
        assert primera.get_attribute("data-id")
        assert primera.get_attribute("data-accion")
        assert len(primera.find_elements(By.TAG_NAME, "td")) == 6
        detalle = f"{len(filas)} eventos registrados"
    else:
        # Estado inicial sin registros: la tabla muestra el mensaje vacío
        vacio = cuerpo.find_element(By.CSS_SELECTOR, "td.table__empty")
        assert "No hay eventos registrados" in vacio.text
        detalle = "sin eventos registrados"

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Bitácora listada: {detalle}")
