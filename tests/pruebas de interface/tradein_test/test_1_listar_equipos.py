import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css

URL_TRADEIN = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/trade-in"
TIEMPO_ESPERA = 10

# PRERREQUISITO: la BD debe tener equipos Apple (marca Apple, clase Telefono y
# existencias > 0) porque el select de /trade-in se llena al renderizar la vista.


def test_listar_equipos(driver):
    driver.get(URL_TRADEIN)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == "Ituaccesorio - Trade-in"
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Trade-in"
    # textContent (texto del DOM), porque el CSS renderiza el eyebrow en mayusculas
    assert driver.find_element(By.CSS_SELECTOR, ".hero__eyebrow").get_attribute("textContent").strip() == (
        "Trade-in"
    )
    assert driver.find_element(By.CSS_SELECTOR, ".hero__title").text.strip() == (
        "Cotización de equipo usado"
    )
    # Chips de estado de la cotizacion en el encabezado
    chips = [
        c.get_attribute("textContent").strip()
        for c in driver.find_elements(By.CSS_SELECTOR, ".tradein-chip__label")
    ]
    assert chips == ["Flujo", "Registro"]

    # Tarjetas del formulario y del resultado
    titulos = [
        c.get_attribute("textContent").strip()
        for c in driver.find_elements(By.CSS_SELECTOR, ".tradein-grid .card__title")
    ]
    assert titulos == ["Datos del equipo", "Resultado estimado"]

    # El select de equipos es server-side; presence_of_all_elements_located
    # sigue esperando mientras la lista de opciones quede vacía.
    opciones = espera.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "#tradein-equipo option:not([value=''])")
        )
    )
    assert len(opciones) >= 1, "No hay equipos cargados en el select de /trade-in."

    # Etiquetas del formulario (textContent por el text-transform en mayusculas)
    etiqueta_equipo = driver.find_element(
        By.XPATH, "//label[.//select[@id='tradein-equipo']]/span[@class='field__label']"
    ).get_attribute("textContent").strip()
    assert etiqueta_equipo == "Equipo *"
    leyenda_liberacion = driver.find_element(
        By.XPATH, "//fieldset[.//input[@name='liberado']]/legend"
    ).get_attribute("textContent").strip()
    assert leyenda_liberacion == "Liberación del equipo *"
    opciones_liberado = [
        s.get_attribute("textContent").strip()
        for s in driver.find_elements(By.CSS_SELECTOR, ".tradein-choice span")
    ]
    assert opciones_liberado == ["Sí, está liberado", "No, está bloqueado"]

    # Leyenda de fallas y desplegable con el significado de cada una
    leyenda_fallas = driver.find_element(
        By.XPATH, "//fieldset[.//input[@name='fallas']]/legend"
    ).get_attribute("textContent").strip()
    assert leyenda_fallas == (
        "Por favor marca en las casillas las cosas que no funcionan en tu teléfono"
    )
    assert driver.find_element(By.CSS_SELECTOR, ".tradein-legend__summary").get_attribute("textContent").strip() == (
        "¿Qué significa cada falla? (Haz clic para ver)"
    )

    # Casillas de fallas: 20 etiquetas (FALLAS_COTIZACION) y 4 con badge
    # de costo alto (lcd, tactil, camara_trasera, camara_delantera)
    radios_liberado = driver.find_elements(By.CSS_SELECTOR, "input[name='liberado']")
    casillas_fallas = driver.find_elements(By.CSS_SELECTOR, "input[name='fallas']")
    assert len(radios_liberado) == 2, "Faltan las opciones de liberación del equipo."
    assert len(casillas_fallas) == 20, "La lista de fallas no coincide con FALLAS_COTIZACION."
    etiquetas_fallas = [
        s.get_attribute("textContent").strip()
        for s in driver.find_elements(
            By.CSS_SELECTOR, ".tradein-check > span:not(.tradein-check__badge)"
        )
    ]
    assert "LCD" in etiquetas_fallas and "Mica" in etiquetas_fallas
    assert len(driver.find_elements(By.CSS_SELECTOR, ".tradein-check__badge")) == 4

    # --- Boton 'Cotizar': fondo amarillo con texto oscuro ---
    boton_cotizar = driver.find_element(By.ID, "tradein-submit")
    assert boton_cotizar.is_displayed()
    assert boton_cotizar.text.strip() == "Cotizar"
    assert estilo_css(driver, boton_cotizar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Cotizar' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_cotizar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Cotizar' deberia ser oscuro"
    )

    # --- Panel de resultado vacio antes de cotizar ---
    espera.until(EC.presence_of_element_located((By.ID, "tradein-resultado")))
    assert driver.find_element(By.CSS_SELECTOR, ".tradein-result__label").get_attribute("textContent").strip() == (
        "Monto estimado (USD)"
    )
    assert driver.find_element(By.ID, "tradein-monto").text == "$0.00"
    assert driver.find_element(By.ID, "tradein-base").text == "$0.00"
    assert driver.find_element(By.ID, "tradein-deduccion").text == "$0.00"
    assert driver.find_element(By.ID, "tradein-total-fallas").text == "0"
    assert driver.find_element(By.ID, "tradein-detalles").text.strip() == (
        "No hay fallas seleccionadas."
    )
    assert driver.find_element(By.ID, "tradein-mensajes").text.strip() == (
        'Presiona "Cotizar" para ver la estimación.'
    )

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Equipos listados en /trade-in: {len(opciones)} opción(es). "
        f"Primera: {opciones[0].text}"
    )
