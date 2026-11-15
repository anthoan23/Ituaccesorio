import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

URL_PRODUCTOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/productos"
TIEMPO_ESPERA = 10

# [nombre, descripcion]
DATOS_MODELO = ["Modelo Prueba", "Modelo de prueba de interface"]

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


def test_crear_modelo(driver):
    driver.get(URL_PRODUCTOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    driver.find_element(By.ID, "btn-registrar-producto").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-producto")))

    # El JS llena los selects de clase y marca por fetch
    espera.until(
        lambda navegador: len(
            Select(navegador.find_element(By.ID, "p-clase")).options
        )
        > 1
    )
    espera.until(
        lambda navegador: len(
            Select(navegador.find_element(By.ID, "p-marca")).options
        )
        > 1
    )

    # Primera clase y primera marca disponibles (la foto es opcional y no se toca)
    Select(driver.find_element(By.ID, "p-clase")).select_by_index(1)
    Select(driver.find_element(By.ID, "p-marca")).select_by_index(1)

    driver.find_element(By.ID, "p-modelo").send_keys(DATOS_MODELO[0])
    driver.find_element(By.ID, "p-descripcion").send_keys(DATOS_MODELO[1])
    driver.find_element(
        By.CSS_SELECTOR, "#form-producto button[type='submit']"
    ).click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-producto")))
    # El feedback de éxito aparece solo después de recargar la tabla
    espera.until(EC.visibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(buscar_fila_en_paginas)
    assert DATOS_MODELO[0] in fila.text
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Modelo creado: {DATOS_MODELO[0]}")
