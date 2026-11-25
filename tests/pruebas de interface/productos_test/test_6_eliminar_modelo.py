import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

URL_PRODUCTOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/productos"
TIEMPO_ESPERA = 10

# Nombre del producto que la cadena creo/modifico y aqui elimina. El JS arma el
# nombre mostrado como "<modelo> (<marca>)" al confirmar el borrado.
NOMBRE_MODELO = "Producto Interfaz Editado"
MARCA_MODELO = "Iphone"
NOMBRE_PRODUCTO = f"{NOMBRE_MODELO} ({MARCA_MODELO})"

# Fila del producto en la tabla (la columna 2 lleva el nombre del producto)
FILA_MODELO = f"//*[@id='tabla-productos']//tr[td[2]//strong[normalize-space(.)='{NOMBRE_MODELO}']]"


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


def fila_no_existe_en_paginas(navegador):
    """Recorre todas las páginas del paginador y devuelve True si la fila ya no existe."""
    anterior = navegador.find_element(By.ID, "pager-anterior")
    while not anterior.get_attribute("disabled"):
        anterior.click()  # volver a la primera página
    while True:
        filas = navegador.find_elements(By.XPATH, FILA_MODELO)
        if filas:
            return False  # el producto sigue existiendo
        boton = navegador.find_element(By.ID, "pager-siguiente")
        if boton.get_attribute("disabled"):
            return True  # última página y el producto no aparece
        boton.click()


def esperar_feedback_exito(espera, mensaje):
    """FeedbackModal global. OJO: el interceptor de feedback-modal.js muestra
    primero su modal generico (titulo 'Acción exitosa') al resolver el DELETE;
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


def test_eliminar_modelo(driver):
    driver.get(URL_PRODUCTOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(lambda navegador: buscar_fila_en_paginas(navegador, FILA_MODELO))
    fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']").click()

    # --- Modal de confirmacion creado por el JS (antes verifica el stock) ---
    espera.until(EC.visibility_of_element_located((By.ID, "confirmacion-modal")))
    quitar_hover(driver)
    assert driver.find_element(
        By.CSS_SELECTOR, "#confirmacion-modal .ui-modal__title"
    ).text == "Confirmar eliminación"
    mensaje = driver.find_element(By.ID, "confirmacion-modal-mensaje").text.strip()
    assert mensaje == f'¿Seguro que deseas eliminar el producto "{NOMBRE_PRODUCTO}"?', (
        f"El texto de confirmacion no menciona al producto: '{mensaje}'"
    )

    # --- Boton 'Eliminar': estilo peligro (texto y fondo rojo tenue) ---
    boton_confirmar = driver.find_element(By.ID, "btn-confirmar-accion")
    assert boton_confirmar.text.strip() == "Eliminar"
    assert "ui-btn--danger" in boton_confirmar.get_attribute("class")
    assert estilo_css(driver, boton_confirmar, "color") == "rgb(239, 68, 68)", (
        "El texto de 'Eliminar' deberia ser el rojo de peligro del tema"
    )
    assert estilo_css(driver, boton_confirmar, "backgroundColor") == (
        "rgba(220, 38, 38, 0.2)"
    ), "El fondo de 'Eliminar' deberia ser rojo tenue"

    boton_cancelar = driver.find_element(By.ID, "btn-cancelar-confirmacion")
    assert boton_cancelar.text.strip() == "Cancelar"
    assert "ui-btn--ghost" in boton_cancelar.get_attribute("class")
    assert estilo_css(driver, boton_cancelar, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Cancelar' deberia ser el ghost del tema oscuro"
    assert estilo_css(driver, boton_cancelar, "color") == "rgb(255, 255, 255)", (
        "El texto de 'Cancelar' deberia ser blanco"
    )

    boton_confirmar.click()

    espera.until(EC.invisibility_of_element_located((By.ID, "confirmacion-modal")))

    # --- Feedback global de exito: menciona el producto con su marca ---
    _, mensaje_feedback = esperar_feedback_exito(
        espera, f'Producto "{NOMBRE_PRODUCTO}" eliminado correctamente.'
    )

    # El producto ya no debe aparecer en ninguna página del paginador
    espera.until(lambda navegador: fila_no_existe_en_paginas(navegador))
    print(f"Producto eliminado: {NOMBRE_PRODUCTO} (feedback: {mensaje_feedback})")
