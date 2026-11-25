import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_PRODUCTOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/productos"
TIEMPO_ESPERA = 10

# [nombre_actual, nombre_nuevo, descripcion]
DATOS_MODELO = ["Modelo Prueba", "Modelo Editado", "Modelo de prueba de interface"]

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


def test_modificar_modelo(driver):
    driver.get(URL_PRODUCTOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(
        lambda navegador: buscar_fila_en_paginas(navegador, FILA_MODELO_ACTUAL)
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='editar']").click()

    # El JS llena el formulario con los datos del producto antes de abrir el modal
    espera.until(EC.visibility_of_element_located((By.ID, "modal-producto")))
    espera.until(
        lambda navegador: navegador.find_element(By.ID, "p-modelo").get_attribute(
            "value"
        )
        == DATOS_MODELO[0]
    )

    nombre = driver.find_element(By.ID, "p-modelo")
    nombre.clear()
    nombre.send_keys(DATOS_MODELO[1])
    driver.find_element(
        By.CSS_SELECTOR, "#form-producto button[type='submit']"
    ).click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-producto")))
    # El feedback de éxito aparece solo después de recargar la tabla
    espera.until(EC.visibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(
        lambda navegador: buscar_fila_en_paginas(navegador, FILA_MODELO_EDITADA)
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Modelo modificado: {DATOS_MODELO[0]} -> {DATOS_MODELO[1]}")
