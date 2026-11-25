import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_BACKUP = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/backup"
TIEMPO_ESPERA = 10

# Archivo SQL mínimo que se genera en runtime para la subida
RUTA_ARCHIVO = "/tmp/opencode/backup_prueba.sql"

# Feedback: backup.js delega en el interceptor global de fetch (feedback-modal.js),
# que abre el FeedbackModal con titulo "Acción exitosa" y mensaje generico de POST.
# El mensaje del servidor ("Backup subido exitosamente: <archivo>") solo va a
# consola: Utils.showMessage no pinta nada (window.notify no existe).
FEEDBACK_TITULO = "Acción exitosa"
FEEDBACK_MENSAJE = "Registro realizado satisfactoriamente."


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

    # --- Modal 'Subir Backup': titulo, labels y botones ---
    driver.find_element(By.ID, "btn-subir-backup").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-subir-backup")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-subir-backup-title").text == "Subir Backup"
    labels = [
        span.get_attribute("textContent").strip()
        for span in driver.find_elements(By.CSS_SELECTOR, "#form-subir-backup .backup-form__field > span")
    ]
    assert labels == ["Tipo de Base de Datos", "Archivo SQL"]

    boton_subir = driver.find_element(By.CSS_SELECTOR, "#form-subir-backup button[type='submit']")
    assert boton_subir.text.strip() == "Subir Backup"
    assert estilo_css(driver, boton_subir, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Subir Backup' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_subir, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Subir Backup' deberia ser oscuro"
    )
    boton_cancelar = driver.find_element(
        By.CSS_SELECTOR, "#form-subir-backup [data-close-modal]"
    )
    assert boton_cancelar.text.strip() == "Cancelar"
    assert estilo_css(driver, boton_cancelar, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Cancelar' deberia ser el ghost del tema oscuro"

    # Tipo de BD y archivo dentro del formulario de subida
    Select(
        driver.find_element(By.CSS_SELECTOR, "#form-subir-backup select[name='tipo_bd']")
    ).select_by_value("ituaccesorio")
    driver.find_element(
        By.CSS_SELECTOR, "#form-subir-backup input[type='file'][name='archivo']"
    ).send_keys(RUTA_ARCHIVO)
    boton_subir.click()

    # Feedback global del interceptor de fetch con el mensaje generico de POST
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo=FEEDBACK_TITULO, mensaje=FEEDBACK_MENSAJE
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-subir-backup")))

    # El respaldo subido debe aparecer en el listado recargado (ID nuevo)
    ids_nuevos = espera.until(lambda d: (ids_backups(d) - ids_antes) or None)
    id_nuevo = sorted(ids_nuevos, key=int)[0]

    fila_xpath = (
        "//*[@id='tabla-backups']//tr"
        f"[td[1][span[normalize-space(.)='{id_nuevo}']]]"
    )
    nombre = driver.find_element(By.XPATH, f"{fila_xpath}/td[3]").text
    badge = driver.find_element(By.XPATH, f"{fila_xpath}/td[5]/span")
    assert "backup_prueba" in nombre, f"El respaldo subido deberia conservar el nombre: '{nombre}'"
    assert badge.get_attribute("textContent").strip().lower() == "completado", (
        f"El estado del respaldo subido deberia ser 'Completado': '{badge.text}'"
    )
    assert "badge--success" in badge.get_attribute("class"), (
        "El badge de 'Completado' deberia ser verde"
    )

    print(f"Backup subido: {nombre} (feedback: {mensaje})")
