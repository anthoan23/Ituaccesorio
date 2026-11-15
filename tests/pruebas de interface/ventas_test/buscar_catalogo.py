import os

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Catálogo de productos: página pública del módulo de ventas
URL_MODULO = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/catalogo"
TIEMPO_ESPERA = 10

# Texto genérico de búsqueda (debe coincidir con nombres o marcas comunes)
TEXTO_BUSQUEDA = "a"


def test_buscar_catalogo(driver):
    driver.get(URL_MODULO)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # Esperar a que el fetch cargue los productos reales (sin esqueletos)
    espera.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "#productos-grid .producto-card:not(.producto-card--skeleton)",
            )
        )
    )
    # Abrir el buscador del catálogo (el box se expande con la clase is-open)
    driver.find_element(By.ID, "catalog-search-toggle").click()
    entrada = espera.until(EC.element_to_be_clickable((By.ID, "f-texto")))
    entrada.send_keys(TEXTO_BUSQUEDA)
    # El JS aplica el filtro al presionar Enter (aplicarFiltros -> cargarCatalogo)
    entrada.send_keys(Keys.ENTER)
    # Esperar a que el listado se refresque: el estado de carga #catalog-status
    # se limpia justo después de re-renderizar las tarjetas
    espera.until(
        lambda navegador: navegador.find_element(By.ID, "catalog-status").text == ""
    )
    tarjetas = driver.find_elements(
        By.CSS_SELECTOR,
        "#productos-grid .producto-card:not(.producto-card--skeleton)",
    )
    mensaje_vacio = driver.find_elements(
        By.CSS_SELECTOR, "#productos-grid .catalog-empty"
    )
    # Comportamiento visible: tarjetas con resultados o mensaje de sin resultados
    assert tarjetas or mensaje_vacio
    contador = driver.find_element(By.ID, "productos-count").text
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    if tarjetas:
        print(f"Busqueda '{TEXTO_BUSQUEDA}' aplicada: {contador} resultados")
    else:
        print("Busqueda aplicada: sin resultados (mensaje visible)")
