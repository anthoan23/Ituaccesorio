import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_BACKUP = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/backup"
TIEMPO_ESPERA = 10

# Archivo SQL mínimo que se genera en runtime para subir el respaldo de prueba
RUTA_ARCHIVO = "/tmp/opencode/backup_prueba_eliminar.sql"

# Feedback: backup.js delega en el interceptor global de fetch (feedback-modal.js),
# que abre el FeedbackModal con titulo "Acción exitosa" y mensaje generico segun
# el metodo (POST -> registro / DELETE -> eliminacion).
FEEDBACK_TITULO = "Acción exitosa"
FEEDBACK_MENSAJE_SUBIDA = "Registro realizado satisfactoriamente."
FEEDBACK_MENSAJE_BORRADO = "Eliminación realizada satisfactoriamente."


def ids_backups(driver):
    """IDs de los respaldos renderizados en la tabla (chips de la columna ID)."""
    cuerpo = driver.find_element(By.ID, "tabla-backups")
    return {chip.text.strip() for chip in cuerpo.find_elements(By.CSS_SELECTOR, "tr td .chip")}


def subir_respaldo_de_prueba(driver, espera):
    """Sube el respaldo de prueba por la UI y devuelve su nombre de archivo."""
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

    # Feedback global del interceptor de fetch (POST) y cierre del modal
    esperar_feedback(
        espera, tipo="success", titulo=FEEDBACK_TITULO, mensaje=FEEDBACK_MENSAJE_SUBIDA
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-subir-backup")))

    fila_xpath = (
        "//*[@id='tabla-backups']//tr"
        f"[td[3][contains(normalize-space(.), 'backup_prueba_eliminar')]]"
    )
    fila = espera.until(EC.visibility_of_element_located((By.XPATH, fila_xpath)))
    return fila.find_element(By.XPATH, "td[3]").text.strip()


def eliminar_respaldo(driver, espera, nombre):
    """Elimina por la UI (modal de confirmacion) el respaldo cuyo nombre de
    archivo coincide exactamente con el indicado."""
    fila_xpath = (
        "//*[@id='tabla-backups']//tr"
        f"[td[3][normalize-space(.)='{nombre}']]"
    )
    fila = espera.until(EC.visibility_of_element_located((By.XPATH, fila_xpath)))
    fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']").click()

    # --- Modal de confirmacion: texto dinamico con el nombre y estilos ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-eliminar-backup")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-eliminar-backup-title").text == "Eliminar Backup"
    texto = driver.find_element(By.ID, "texto-confirmar-eliminar-backup").text
    assert texto == f'¿Estás seguro de que quieres eliminar el respaldo "{nombre}"?', (
        f"El texto de confirmacion no menciona el respaldo: '{texto}'"
    )

    boton_confirmar = driver.find_element(By.ID, "btn-confirmar-eliminar-backup")
    assert boton_confirmar.text.strip() == "Sí, eliminar"
    assert estilo_css(driver, boton_confirmar, "backgroundColor") == "rgba(220, 38, 38, 0.2)", (
        "El fondo de 'Sí, eliminar' deberia ser el rojo translucido de peligro"
    )
    assert estilo_css(driver, boton_confirmar, "color") == "rgb(239, 68, 68)", (
        "El texto de 'Sí, eliminar' deberia ser rojo peligro"
    )
    boton_cancelar = driver.find_element(
        By.CSS_SELECTOR, "#modal-eliminar-backup .ui-form__actions [data-close-modal]"
    )
    assert boton_cancelar.text.strip() == "Cancelar"
    assert estilo_css(driver, boton_cancelar, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Cancelar' deberia ser el ghost del tema oscuro"

    boton_confirmar.click()

    # Feedback global del interceptor de fetch (DELETE) con mensaje generico
    _, mensaje = esperar_feedback(
        espera, tipo="success", titulo=FEEDBACK_TITULO, mensaje=FEEDBACK_MENSAJE_BORRADO
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-eliminar-backup")))

    # El respaldo eliminado desaparece del listado recargado
    espera.until(EC.invisibility_of_element_located((By.XPATH, fila_xpath)))
    return mensaje


def test_eliminar_backup(driver):
    # Para no depender de datos previos, la prueba sube su propio respaldo de
    # prueba y después elimina ese mismo respaldo
    os.makedirs(os.path.dirname(RUTA_ARCHIVO), exist_ok=True)
    with open(RUTA_ARCHIVO, "w", encoding="utf-8") as archivo:
        archivo.write("-- respaldo de prueba para eliminacion\n")

    # Carpeta de respaldos de la app (app/bd): se toma un snapshot inicial para
    # comprobar al final que la cadena no deja archivos nuevos
    carpeta_bd = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "app", "bd")
    )
    contenido_inicial = set(os.listdir(carpeta_bd)) if os.path.isdir(carpeta_bd) else set()

    driver.get(URL_BACKUP)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # El listado se llena por fetch: esperamos la primera fila (real o vacía)
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-backups tr")))

    # --- Subida del respaldo de prueba y eliminacion de ese mismo respaldo ---
    nombre_subido = subir_respaldo_de_prueba(driver, espera)
    mensaje_borrado = eliminar_respaldo(driver, espera, nombre_subido)
    print(f"Backup eliminado: {nombre_subido} (feedback: {mensaje_borrado})")

    # --- Limpieza de la cadena: el respaldo CREADO por test_2 tambien se elimina ---
    # Asi la BD de respaldos y la carpeta app/bd quedan como estaban (solo el
    # respaldo seed). El modelo borra tambien el archivo fisico.
    filas_creadas = driver.find_elements(
        By.XPATH, "//*[@id='tabla-backups']//tr[td[3][contains(normalize-space(.), 'ituaccesorio_backup_')]]"
    )
    if filas_creadas:
        nombre_creado = filas_creadas[0].find_element(By.XPATH, "td[3]").text.strip()
        mensaje_creado = eliminar_respaldo(driver, espera, nombre_creado)
        print(f"Backup de la cadena eliminado: {nombre_creado} (feedback: {mensaje_creado})")

    # La carpeta de respaldos no debe acumular archivos nuevos por la cadena
    contenido_final = set(os.listdir(carpeta_bd)) if os.path.isdir(carpeta_bd) else set()
    residuos = contenido_final - contenido_inicial
    assert not residuos, f"La carpeta app/bd quedo con respaldos de prueba: {sorted(residuos)}"
    print("Carpeta de respaldos limpia tras la cadena de backups")
