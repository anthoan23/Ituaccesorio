import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

URL_BACKUP = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/backup"
TIEMPO_ESPERA = 10


def test_listar_backup(driver):
    driver.get(URL_BACKUP)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == "Ituaccesorio - Respaldo de Base de Datos"
    assert driver.find_element(By.CSS_SELECTOR, ".hero__title").text == "Respaldo de Base de Datos"
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Respaldo de BD"
    # textContent (texto del DOM): el CSS renderiza el eyebrow en mayusculas
    assert driver.find_element(By.CSS_SELECTOR, ".hero__eyebrow").get_attribute("textContent").strip() == (
        "Gestión de respaldos"
    )
    assert driver.find_element(By.CSS_SELECTOR, ".card__title").text == "Historial de Respaldos"
    etiqueta_stat = driver.find_element(By.CSS_SELECTOR, ".stat-card__label")
    assert etiqueta_stat.get_attribute("textContent").strip() == "Respaldos"

    # Encabezados de la tabla (textContent por el uppercase del CSS)
    encabezados = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, ".table thead th")
    ]
    assert encabezados == ["ID", "Usuario", "Nombre", "Fecha", "Estado", "Acciones"]

    # --- Botones de accion: 'Crear Backup' verde y 'Subir Backup' azul ---
    quitar_hover(driver)
    boton_crear = driver.find_element(By.ID, "btn-crear-backup")
    assert boton_crear.text.strip() == "Crear Backup"
    assert "btn-icon-action--success" in boton_crear.get_attribute("class")
    assert estilo_css(driver, boton_crear, "borderTopColor") == "rgb(34, 197, 94)", (
        "El borde de 'Crear Backup' deberia ser verde"
    )
    assert estilo_css(driver, boton_crear, "color") == "rgb(34, 197, 94)", (
        "El texto de 'Crear Backup' deberia ser verde"
    )
    boton_subir = driver.find_element(By.ID, "btn-subir-backup")
    assert boton_subir.text.strip() == "Subir Backup"
    assert "btn-icon-action--info" in boton_subir.get_attribute("class")
    assert estilo_css(driver, boton_subir, "borderTopColor") == "rgb(59, 130, 246)", (
        "El borde de 'Subir Backup' deberia ser azul"
    )
    assert estilo_css(driver, boton_subir, "color") == "rgb(59, 130, 246)", (
        "El texto de 'Subir Backup' deberia ser azul"
    )

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
        # El badge de estado refleja el estado textual de la fila
        badge = primera.find_element(By.CSS_SELECTOR, "span.badge")
        estado_texto = badge.get_attribute("textContent").strip().lower()
        clases_badge = badge.get_attribute("class")
        if estado_texto == "completado":
            assert "badge--success" in clases_badge
        elif estado_texto in ("fallido", "error"):
            assert "badge--error" in clases_badge
        else:
            assert "badge--warning" in clases_badge
        detalle = f"{len(filas)} respaldos en el historial"
    else:
        vacio = cuerpo.find_element(By.CSS_SELECTOR, "td.table__empty")
        assert "No hay respaldos registrados" in vacio.text
        detalle = "historial vacío"

    # El contador de respaldos del encabezado coincide con las filas renderizadas
    contador = driver.find_element(By.CSS_SELECTOR, ".stat-card__value[data-count]")
    assert int(contador.get_attribute("data-count")) == len(filas)

    print(f"Backups listados: {detalle}")
