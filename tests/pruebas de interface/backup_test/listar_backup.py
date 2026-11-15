import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_BACKUP = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/backup"
TIEMPO_ESPERA = 10


def test_listar_backup(driver):
    driver.get(URL_BACKUP)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # El listado se llena por fetch (/api/backup/listar): esperamos que el JS
    # renderice la primera fila (respaldo real o mensaje de tabla vacía)
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-backups tr")))
    cuerpo = driver.find_element(By.ID, "tabla-backups")

    filas = [
        fila
        for fila in cuerpo.find_elements(By.CSS_SELECTOR, "tr")
        if not fila.find_elements(By.CSS_SELECTOR, "td.table__empty")
    ]
    if filas:
        # Estructura de cada fila: ID, Usuario, Nombre, Fecha, Estado y acciones
        primera = filas[0]
        assert len(primera.find_elements(By.TAG_NAME, "td")) == 6
        assert primera.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']")
        detalle = f"{len(filas)} respaldos en el historial"
    else:
        vacio = cuerpo.find_element(By.CSS_SELECTOR, "td.table__empty")
        assert "No hay respaldos registrados" in vacio.text
        detalle = "historial vacío"

    # El contador de respaldos del encabezado coincide con las filas renderizadas
    contador = driver.find_element(By.CSS_SELECTOR, ".stat-card__value[data-count]")
    assert int(contador.get_attribute("data-count")) == len(filas)

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Backups listados: {detalle}")
