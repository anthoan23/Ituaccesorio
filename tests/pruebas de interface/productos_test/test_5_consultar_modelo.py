import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_PRODUCTOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/productos"
TIEMPO_ESPERA = 10

# [nombre, descripcion] - el producto que la cadena creo y modifico
DATOS_MODELO = ["Producto Interfaz Editado", "Producto de prueba de interfaz"]

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
    # textContent (texto del DOM), porque el CSS puede renderizar en mayusculas
    nombre = fila.find_element(
        By.CSS_SELECTOR, "strong.product-name"
    ).get_attribute("textContent").strip()
    codigo = fila.find_element(
        By.CSS_SELECTOR, "span.product-sku"
    ).get_attribute("textContent").strip()
    marca = fila.find_element(
        By.CSS_SELECTOR, "span.badge-marca"
    ).get_attribute("textContent").strip()
    clase = fila.find_element(
        By.CSS_SELECTOR, "span.badge-clase"
    ).get_attribute("textContent").strip()

    assert nombre == DATOS_MODELO[0]
    assert codigo.startswith("Código: PRO")
    assert marca == "Iphone", "La marca deberia ser la primera disponible (indice 1)"
    assert clase == "Telefono", "La clase deberia ser la primera disponible (indice 1)"

    # La fila solo ofrece editar y eliminar (no existe boton de 'ver')
    assert fila.find_elements(By.CSS_SELECTOR, "button[data-action='editar']")
    assert fila.find_elements(By.CSS_SELECTOR, "button[data-action='eliminar']")
    assert not fila.find_elements(By.CSS_SELECTOR, "button[data-action='ver']")
    print(f"Producto consultado: {nombre} - {codigo} ({marca} / {clase})")
