import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from helpers import estilo_css, quitar_hover

URL_PRODUCTOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/productos"
TIEMPO_ESPERA = 10

# [nombre, descripcion] - la cadena CRUD crea/modifica/elimina este registro
# El select toma la primera clase y la primera marca disponibles (indice 1).
DATOS_MODELO = ["Producto Interfaz", "Producto de prueba de interfaz"]

# Fila del producto en la tabla (la columna 2 lleva el nombre del producto)
FILA_MODELO = f"//*[@id='tabla-productos']//tr[td[2]//strong[normalize-space(.)='{DATOS_MODELO[0]}']]"


def buscar_fila_en_paginas(navegador):
    """Busca la fila del producto recorriendo las páginas del paginador."""
    filas = navegador.find_elements(By.XPATH, FILA_MODELO)
    if filas:
        return filas[0]
    boton = navegador.find_element(By.ID, "pager-siguiente")
    if boton.get_attribute("disabled"):
        return False
    boton.click()
    filas = navegador.find_elements(By.XPATH, FILA_MODELO)
    return filas[0] if filas else False


def esperar_feedback_exito(espera, mensaje):
    """FeedbackModal global. OJO: el interceptor de feedback-modal.js muestra
    primero su modal generico (titulo 'Acción exitosa') al resolver el POST;
    productos.js lo sobreescribe con titulo 'Éxito' y su mensaje definitivo
    despues de recargar la tabla. Esta espera solo acepta el mensaje
    definitivo y luego espera el autocierre del modal."""
    def mensaje_definitivo(navegador):
        modal = navegador.find_element(By.ID, "feedback-modal")
        if modal.get_attribute("hidden"):
            return False
        titulo = navegador.find_element(By.ID, "feedback-modal-title").text.strip()
        texto = navegador.find_element(By.ID, "feedback-modal-message").text.strip()
        return (titulo, texto) if titulo == "Éxito" and mensaje in texto else False

    titulo, texto = espera.until(mensaje_definitivo)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    return titulo, texto


def test_crear_modelo(driver):
    driver.get(URL_PRODUCTOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-productos tr[data-id]")))

    # --- Boton 'Registrar producto': texto y estilo amarillo ---
    boton_registrar = driver.find_element(By.ID, "btn-registrar-producto")
    assert boton_registrar.text.strip() == "Registrar producto"
    assert estilo_css(driver, boton_registrar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Registrar producto' deberia ser amarillo"
    )
    boton_registrar.click()

    # --- Modal 'Registrar producto': titulo y acciones ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-producto")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-producto-title").text == "Registrar producto"
    boton_guardar = driver.find_element(
        By.CSS_SELECTOR, "#form-producto button[type='submit']"
    )
    assert boton_guardar.text.strip() == "Guardar producto"
    assert estilo_css(driver, boton_guardar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Guardar producto' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_guardar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Guardar producto' deberia ser oscuro"
    )
    boton_cancelar = driver.find_element(
        By.CSS_SELECTOR, "#form-producto [data-close-modal]"
    )
    assert boton_cancelar.text.strip() == "Cancelar"
    assert "ui-btn--ghost" in boton_cancelar.get_attribute("class")

    # El JS llena los selects de clase y marca por fetch
    espera.until(lambda navegador: len(Select(navegador.find_element(By.ID, "p-clase")).options) > 1)
    espera.until(lambda navegador: len(Select(navegador.find_element(By.ID, "p-marca")).options) > 1)

    # Primera clase y primera marca disponibles (la foto es opcional y no se toca)
    Select(driver.find_element(By.ID, "p-clase")).select_by_index(1)
    Select(driver.find_element(By.ID, "p-marca")).select_by_index(1)

    driver.find_element(By.ID, "p-modelo").send_keys(DATOS_MODELO[0])
    driver.find_element(By.ID, "p-descripcion").send_keys(DATOS_MODELO[1])
    boton_guardar.click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-producto")))

    # --- Feedback global de exito con el mensaje definitivo del JS ---
    # (aparece solo despues de que el JS recarga la tabla)
    _, mensaje = esperar_feedback_exito(espera, "Producto guardado correctamente.")

    # --- Fila creada: localizarla recorriendo las paginas del paginador ---
    fila = espera.until(buscar_fila_en_paginas)
    # textContent (texto del DOM), porque el CSS puede renderizar en mayusculas
    assert fila.find_element(
        By.CSS_SELECTOR, "strong.product-name"
    ).get_attribute("textContent").strip() == DATOS_MODELO[0]
    # La marca/clase elegidas con indice 1 son las primeras de la lista
    assert fila.find_element(
        By.CSS_SELECTOR, "span.badge-marca"
    ).get_attribute("textContent").strip() == "Iphone"
    assert fila.find_element(
        By.CSS_SELECTOR, "span.badge-clase"
    ).get_attribute("textContent").strip() == "Telefono"
    print(f"Producto creado: {DATOS_MODELO[0]} (feedback: {mensaje})")
