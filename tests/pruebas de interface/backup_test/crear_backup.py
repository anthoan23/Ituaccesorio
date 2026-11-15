import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_BACKUP = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/backup"
TIEMPO_ESPERA = 10
# La creación vuelca la BD completa con pymysql y puede tardar varios minutos:
# la confirmación y la aparición del nuevo respaldo se esperan con margen amplio
TIEMPO_RESPALDO = 180


def ids_backups(driver):
    """IDs de los respaldos renderizados en la tabla (chips de la columna ID)."""
    cuerpo = driver.find_element(By.ID, "tabla-backups")
    return {chip.text.strip() for chip in cuerpo.find_elements(By.CSS_SELECTOR, "tr td .chip")}


def test_crear_backup(driver):
    driver.get(URL_BACKUP)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # El listado se llena por fetch: esperamos la primera fila (real o vacía)
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-backups tr")))
    ids_antes = ids_backups(driver)

    driver.find_element(By.ID, "btn-crear-backup").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-seleccionar-bd")))
    driver.find_element(
        By.CSS_SELECTOR, "#modal-seleccionar-bd .backup-option[data-tipo='ituaccesorio']"
    ).click()

    # Confirmación: el interceptor global de fetch abre #feedback-modal al
    # responder el POST /api/backup/crear
    espera_respaldo = WebDriverWait(driver, TIEMPO_RESPALDO)
    espera_respaldo.until(EC.visibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-seleccionar-bd")))

    # El nuevo respaldo debe aparecer en el listado recargado (ID nuevo)
    ids_nuevos = espera_respaldo.until(lambda d: (ids_backups(d) - ids_antes) or None)
    id_nuevo = sorted(ids_nuevos)[0]

    fila_xpath = (
        "//*[@id='tabla-backups']//tr"
        f"[td[1][span[normalize-space(.)='{id_nuevo}']]]"
    )
    nombre = driver.find_element(By.XPATH, f"{fila_xpath}/td[3]").text
    estado = driver.find_element(By.XPATH, f"{fila_xpath}/td[5]").text
    assert "ituaccesorio_backup" in nombre
    assert estado.strip().lower() == "completado"

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Backup creado: {nombre}")
