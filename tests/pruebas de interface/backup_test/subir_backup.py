import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

URL_BACKUP = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/backup"
TIEMPO_ESPERA = 10

# Archivo SQL mínimo que se genera en runtime para la subida
RUTA_ARCHIVO = "/tmp/opencode/backup_prueba.sql"


def ids_backups(driver):
    """IDs de los respaldos renderizados en la tabla (chips de la columna ID)."""
    cuerpo = driver.find_element(By.ID, "tabla-backups")
    return {chip.text.strip() for chip in cuerpo.find_elements(By.CSS_SELECTOR, "tr td .chip")}


def test_subir_backup(driver):
    # Se genera un archivo .sql mínimo en runtime para simular la subida
    os.makedirs(os.path.dirname(RUTA_ARCHIVO), exist_ok=True)
    with open(RUTA_ARCHIVO, "w", encoding="utf-8") as archivo:
        archivo.write("-- respaldo de prueba\n")

    driver.get(URL_BACKUP)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # El listado se llena por fetch: esperamos la primera fila (real o vacía)
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-backups tr")))
    ids_antes = ids_backups(driver)

    driver.find_element(By.ID, "btn-subir-backup").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-subir-backup")))

    # Tipo de BD y archivo dentro del formulario de subida
    Select(
        driver.find_element(By.CSS_SELECTOR, "#form-subir-backup select[name='tipo_bd']")
    ).select_by_value("ituaccesorio")
    driver.find_element(
        By.CSS_SELECTOR, "#form-subir-backup input[type='file'][name='archivo']"
    ).send_keys(RUTA_ARCHIVO)
    driver.find_element(
        By.CSS_SELECTOR, "#form-subir-backup button[type='submit']"
    ).click()

    # Confirmación: el interceptor global de fetch abre #feedback-modal al
    # responder el POST /api/backup/subir
    espera.until(EC.visibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-subir-backup")))

    # El respaldo subido debe aparecer en el listado recargado (ID nuevo)
    ids_nuevos = espera.until(lambda d: (ids_backups(d) - ids_antes) or None)
    id_nuevo = sorted(ids_nuevos)[0]

    fila_xpath = (
        "//*[@id='tabla-backups']//tr"
        f"[td[1][span[normalize-space(.)='{id_nuevo}']]]"
    )
    nombre = driver.find_element(By.XPATH, f"{fila_xpath}/td[3]").text
    estado = driver.find_element(By.XPATH, f"{fila_xpath}/td[5]").text
    assert "backup_prueba" in nombre
    assert estado.strip().lower() == "completado"

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Backup subido: {nombre}")
