import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_BACKUP = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/backup"
TIEMPO_ESPERA = 10
# La creación vuelca la BD completa con pymysql y puede tardar varios minutos:
# la confirmación y la aparición del nuevo respaldo se esperan con margen amplio
TIEMPO_RESPALDO = 180

# Feedback: backup.js delega en el interceptor global de fetch (feedback-modal.js),
# que abre el FeedbackModal con titulo "Acción exitosa" y mensaje generico de POST.
# El mensaje del servidor ("Backup creado exitosamente: <archivo>") solo va a
# consola: Utils.showMessage no pinta nada (window.notify no existe).
FEEDBACK_TITULO = "Acción exitosa"
FEEDBACK_MENSAJE = "Registro realizado satisfactoriamente."


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

    # --- Modal 'Seleccionar Base de Datos': texto y opciones ---
    driver.find_element(By.ID, "btn-crear-backup").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-seleccionar-bd")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-seleccionar-bd-title").text == "Seleccionar Base de Datos"
    assert driver.find_element(By.CSS_SELECTOR, "#modal-seleccionar-bd .confirm-text").text == (
        "¿De qué base de datos deseas crear un respaldo?"
    )
    nombres_opciones = [
        o.get_attribute("textContent").strip()
        for o in driver.find_elements(By.CSS_SELECTOR, "#modal-seleccionar-bd .backup-option__name")
    ]
    assert nombres_opciones == ["Seguridad", "Ituaccesorio"]
    boton_cancelar = driver.find_element(
        By.CSS_SELECTOR, "#modal-seleccionar-bd .ui-form__actions [data-close-modal]"
    )
    assert boton_cancelar.text.strip() == "Cancelar"
    assert estilo_css(driver, boton_cancelar, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Cancelar' deberia ser el ghost del tema oscuro"

    # Crear el respaldo de la BD principal (el JS dispara el POST al click)
    driver.find_element(
        By.CSS_SELECTOR, "#modal-seleccionar-bd .backup-option[data-tipo='ituaccesorio']"
    ).click()

    # Feedback global del interceptor de fetch con el mensaje generico de POST
    espera_respaldo = WebDriverWait(driver, TIEMPO_RESPALDO)
    esperar_feedback(
        espera_respaldo,
        tipo="success",
        titulo=FEEDBACK_TITULO,
        mensaje=FEEDBACK_MENSAJE,
    )
    espera_respaldo.until(EC.invisibility_of_element_located((By.ID, "modal-seleccionar-bd")))

    # El nuevo respaldo debe aparecer en el listado recargado (ID nuevo)
    ids_nuevos = espera_respaldo.until(lambda d: (ids_backups(d) - ids_antes) or None)
    id_nuevo = sorted(ids_nuevos, key=int)[0]

    fila_xpath = (
        "//*[@id='tabla-backups']//tr"
        f"[td[1][span[normalize-space(.)='{id_nuevo}']]]"
    )
    nombre = driver.find_element(By.XPATH, f"{fila_xpath}/td[3]").text
    badge = driver.find_element(By.XPATH, f"{fila_xpath}/td[5]/span")
    assert "ituaccesorio_backup" in nombre, f"El respaldo creado deberia nombrar la BD: '{nombre}'"
    assert badge.get_attribute("textContent").strip().lower() == "completado", (
        f"El estado del respaldo creado deberia ser 'Completado': '{badge.text}'"
    )
    assert "badge--success" in badge.get_attribute("class"), (
        "El badge de 'Completado' deberia ser verde"
    )

    print(f"Backup creado: {nombre} (feedback: {FEEDBACK_MENSAJE})")
