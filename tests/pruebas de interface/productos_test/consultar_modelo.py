import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_PRODUCTOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/productos"
TIEMPO_ESPERA = 10

# [nombre, descripcion]
DATOS_MODELO = ["Modelo Prueba", "Modelo de prueba de interface"]

# Fila del producto en la tabla (la columna 2 lleva el nombre del producto)
FILA_MODELO = f"//*[@id='tabla-productos']//tr[td[2]//strong[normalize-space(.)='{DATOS_MODELO[0]}']]"


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


def test_consultar_modelo(driver):
    driver.get(URL_PRODUCTOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(lambda navegador: buscar_fila_en_paginas(navegador, FILA_MODELO))

    # Datos visibles en la fila (esta vista no tiene botón de detalle/ver)
    nombre = fila.find_element(By.CSS_SELECTOR, "strong.product-name").text
    codigo = fila.find_element(By.CSS_SELECTOR, "span.product-sku").text
    marca = fila.find_element(By.CSS_SELECTOR, "span.badge-marca").text
    clase = fila.find_element(By.CSS_SELECTOR, "span.badge-clase").text

    assert nombre == DATOS_MODELO[0]
    assert codigo.startswith("Código: PRO")
    assert marca != ""
    assert clase != ""
    print(f"Modelo consultado: {nombre} - {codigo} ({marca} / {clase})")
