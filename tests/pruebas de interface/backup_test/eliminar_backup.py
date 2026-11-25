import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

URL_BACKUP = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/backup"
TIEMPO_ESPERA = 10

# Archivo SQL mínimo que se genera en runtime para subir el respaldo de prueba
RUTA_ARCHIVO = "/tmp/opencode/backup_prueba_eliminar.sql"


def ids_backups(driver):
    """IDs de los respaldos renderizados en la tabla (chips de la columna ID)."""
    cuerpo = driver.find_element(By.ID, "tabla-backups")
    return {chip.text.strip() for chip in cuerpo.find_elements(By.CSS_SELECTOR, "tr td .chip")}


def test_eliminar_backup(driver):
    # Para no depender de datos previos, la prueba sube su propio respaldo de
    # prueba y después elimina ese mismo respaldo
    os.makedirs(os.path.dirname(RUTA_ARCHIVO), exist_ok=True)
    with open(RUTA_ARCHIVO, "w", encoding="utf-8") as archivo:
        archivo.write("-- respaldo de prueba para eliminacion\n")

    driver.get(URL_BACKUP)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # El listado se llena por fetch: esperamos la primera fila (real o vacía)
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-backups tr")))
    ids_antes = ids_backups(driver)

    # --- Subida del respaldo de prueba ---
    driver.find_element(By.ID, "btn-subir-backup").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-subir-backup")))
    Select(
        driver.find_element(By.CSS_SELECTOR, "#form-subir-backup select[name='tipo_bd']")
    ).select_by_value("ituaccesorio")
    driver.find_element(
        By.CSS_SELECTOR, "#form-subir-backup input[type='file'][name='archivo']"
    ).send_keys(RUTA_ARCHIVO)
    driver.find_element(
        By.CSS_SELECTOR, "#form-subir-backup button[type='submit']"
    ).click()

    espera.until(EC.visibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-subir-backup")))
    ids_nuevos = espera.until(lambda d: (ids_backups(d) - ids_antes) or None)
    id_nuevo = sorted(ids_nuevos)[0]

    fila_xpath = (
        "//*[@id='tabla-backups']//tr"
        f"[td[1][span[normalize-space(.)='{id_nuevo}']]]"
    )
    nombre = driver.find_element(By.XPATH, f"{fila_xpath}/td[3]").text

    # --- Eliminación con confirmación ---
    driver.find_element(
        By.XPATH, f"{fila_xpath}//button[@data-action='eliminar']"
    ).click()

    espera.until(EC.visibility_of_element_located((By.ID, "modal-eliminar-backup")))
    # El texto de confirmación menciona el respaldo a eliminar
    texto = driver.find_element(By.ID, "texto-confirmar-eliminar-backup").text
    assert "backup_prueba_eliminar" in texto
    driver.find_element(By.ID, "btn-confirmar-eliminar-backup").click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-eliminar-backup")))

    # El respaldo eliminado desaparece del listado recargado
    espera.until(lambda d: id_nuevo not in ids_backups(d))

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Backup eliminado: {nombre}")
