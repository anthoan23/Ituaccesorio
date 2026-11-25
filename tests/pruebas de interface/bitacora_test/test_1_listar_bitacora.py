import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

URL_BITACORA = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/bitacora"
TIEMPO_ESPERA = 10

# Estructura esperada de la tabla de eventos (se pinta server-side con 'registros')
ENCABEZADOS_BITACORA = ["ID", "Usuario", "Acción", "Módulo", "Descripción", "Fecha/Hora"]

# Etiquetas del modal de detalle (bitacora.html)
ETIQUETAS_DETALLE = ["ID del evento", "Usuario", "Acción", "Módulo", "Fecha y hora", "Descripción"]


def test_listar_bitacora(driver):
    driver.get(URL_BITACORA)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == "Ituaccesorio - Bitácora del Sistema"
    assert driver.find_element(By.CSS_SELECTOR, ".hero__title").text == "Bitácora del Sistema"
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Bitácora del Sistema"
    # textContent (texto del DOM): el CSS renderiza el eyebrow en mayusculas
    assert driver.find_element(By.CSS_SELECTOR, ".hero__eyebrow").get_attribute("textContent").strip() == (
        "Registro de actividades"
    )
    assert driver.find_element(By.CSS_SELECTOR, ".card__title").text == "Eventos Registrados"
    assert driver.find_element(By.CSS_SELECTOR, ".card__subtitle").text == "Historial de actividades del sistema"

    # --- Boton 'Refrescar': estilo fantasma (ghost) del tema oscuro ---
    boton_refrescar = driver.find_element(By.ID, "btn-refrescar")
    assert boton_refrescar.text.strip() == "Refrescar"
    quitar_hover(driver)
    assert estilo_css(driver, boton_refrescar, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Refrescar' deberia ser el ghost del tema oscuro"
    assert estilo_css(driver, boton_refrescar, "color") == "rgb(255, 255, 255)", (
        "El texto de 'Refrescar' deberia ser blanco"
    )

    # Los registros viajan en el HTML (no hay fetch): el <tbody> ya trae las filas.
    # Encabezados con textContent porque el CSS renderiza los th en mayusculas.
    cuerpo = espera.until(EC.presence_of_element_located((By.ID, "tabla-bitacora")))
    encabezados = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, ".bitacora-table thead th")
    ]
    assert encabezados == ENCABEZADOS_BITACORA

    # table-tools.js pagina a 10 filas y oculta el resto: solo contamos las visibles
    filas = [
        fila
        for fila in cuerpo.find_elements(By.CSS_SELECTOR, "tr.evento-row")
        if fila.is_displayed()
    ]
    if filas:
        # Cada fila de evento expone sus datos en atributos data-*
        primera = filas[0]
        assert primera.get_attribute("data-id")
        assert primera.get_attribute("data-accion")
        assert len(primera.find_elements(By.TAG_NAME, "td")) == 6
        detalle = f"{len(filas)} eventos visibles en la primera pagina"

        # --- Modal de detalle: se abre al hacer click en la fila ---
        primera.click()
        espera.until(EC.visibility_of_element_located((By.ID, "modal-detalle")))
        quitar_hover(driver)
        assert driver.find_element(By.ID, "detalle-title").text == "Detalle del evento"
        etiquetas = [
            e.get_attribute("textContent").strip()
            for e in driver.find_elements(By.CSS_SELECTOR, "#modal-detalle .detail-label")
        ]
        assert etiquetas == ETIQUETAS_DETALLE

        # Los valores del detalle salen de los data-* de la fila clickeada
        # (la fecha se re-formatea con JS, se comprueba que no quede vacia)
        assert driver.find_element(By.ID, "d-id").text == primera.get_attribute("data-id")
        assert driver.find_element(By.ID, "d-usuario").text == primera.get_attribute("data-usuario")
        assert driver.find_element(By.ID, "d-accion").text == primera.get_attribute("data-accion")
        assert driver.find_element(By.ID, "d-modulo").text == primera.get_attribute("data-modulo")
        assert driver.find_element(By.ID, "d-descripcion").text == primera.get_attribute("data-descripcion")
        assert driver.find_element(By.ID, "d-fecha").text

        # Cierre por el boton 'Cerrar' (ghost)
        boton_cerrar = driver.find_element(
            By.CSS_SELECTOR, "#modal-detalle .ui-form__actions [data-close-modal]"
        )
        assert boton_cerrar.text.strip() == "Cerrar"
        assert estilo_css(driver, boton_cerrar, "backgroundColor") == (
            "rgba(255, 255, 255, 0.06)"
        ), "El fondo de 'Cerrar' deberia ser el ghost del tema oscuro"
        boton_cerrar.click()
        espera.until(EC.invisibility_of_element_located((By.ID, "modal-detalle")))
    else:
        # Estado inicial sin registros: la tabla muestra el mensaje vacío
        vacio = cuerpo.find_element(By.CSS_SELECTOR, "td.table__empty")
        assert "No hay eventos registrados" in vacio.text
        detalle = "sin eventos registrados"

    # Modulo de solo lectura: no hay POST/PUT/DELETE, el FeedbackModal global no
    # interviene y no hay toast que verificar.
    print(f"Bitácora listada: {detalle}")
