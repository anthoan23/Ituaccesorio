import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_PRODUCTOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/productos"
TIEMPO_ESPERA = 10

# Nombre del producto que se va a eliminar
NOMBRE_MODELO = "Modelo Editado"

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


def test_eliminar_modelo(driver):
    driver.get(URL_PRODUCTOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(lambda navegador: buscar_fila_en_paginas(navegador, FILA_MODELO))
    fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']").click()

    # El JS verifica el stock del producto y abre su propio modal de confirmación
    espera.until(EC.visibility_of_element_located((By.ID, "confirmacion-modal")))
    driver.find_element(By.ID, "btn-confirmar-accion").click()

    espera.until(EC.invisibility_of_element_located((By.ID, "confirmacion-modal")))
    # El producto ya no debe aparecer en ninguna página del paginador
    espera.until(lambda navegador: fila_no_existe_en_paginas(navegador))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Modelo eliminado: {NOMBRE_MODELO}")
