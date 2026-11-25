import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

URL_PRODUCTOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/productos"
TIEMPO_ESPERA = 10

# [nombre_actual, nombre_nuevo, descripcion] - el producto que creo test_3_crear_modelo
DATOS_MODELO = ["Producto Interfaz", "Producto Interfaz Editado", "Producto de prueba de interfaz"]

# Filas antes y después de editar (la columna 2 lleva el nombre del producto)
FILA_MODELO_ACTUAL = f"//*[@id='tabla-productos']//tr[td[2]//strong[normalize-space(.)='{DATOS_MODELO[0]}']]"
FILA_MODELO_EDITADA = f"//*[@id='tabla-productos']//tr[td[2]//strong[normalize-space(.)='{DATOS_MODELO[1]}']]"


def buscar_fila_en_paginas(navegador, xpath_fila):
    """Busca la fila indicada recorriendo las páginas del paginador."""
    filas = navegador.find_elements(By.XPATH, xpath_fila)
    if filas:
        return filas[0]
    boton = navegador.find_element(By.ID, "pager-siguiente")
    if boton.get_attribute("disabled"):
        return False
    boton.click()
    filas = navegador.find_elements(By.XPATH, xpath_fila)
    return filas[0] if filas else False


def esperar_feedback_exito(espera, mensaje):
    """FeedbackModal global. OJO: el interceptor de feedback-modal.js muestra
    primero su modal generico (titulo 'Acción exitosa') al resolver el PUT;
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


def test_modificar_modelo(driver):
    driver.get(URL_PRODUCTOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(
        lambda navegador: buscar_fila_en_paginas(navegador, FILA_MODELO_ACTUAL)
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='editar']").click()

    # --- El JS cambia el titulo del modal y precarga los datos del producto ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-producto")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-producto-title").text == "Editar producto"
    espera.until(
        lambda navegador: navegador.find_element(By.ID, "p-modelo").get_attribute(
            "value"
        )
        == DATOS_MODELO[0]
    )
    assert driver.find_element(By.ID, "p-descripcion").get_attribute("value") == (
        DATOS_MODELO[2]
    )

    # --- El texto del submit NO cambia al editar (siempre 'Guardar producto') ---
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

    nombre = driver.find_element(By.ID, "p-modelo")
    nombre.clear()
    nombre.send_keys(DATOS_MODELO[1])
    boton_guardar.click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-producto")))

    # --- Feedback global de exito: el mismo mensaje sirve para crear y editar ---
    _, mensaje = esperar_feedback_exito(espera, "Producto guardado correctamente.")

    espera.until(
        lambda navegador: buscar_fila_en_paginas(navegador, FILA_MODELO_EDITADA)
    )
    print(
        f"Producto modificado: {DATOS_MODELO[0]} -> {DATOS_MODELO[1]} "
        f"(feedback: {mensaje})"
    )
