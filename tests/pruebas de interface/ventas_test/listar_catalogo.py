import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Catálogo de productos: página pública del módulo de ventas
URL_MODULO = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/catalogo"
TIEMPO_ESPERA = 10


def test_listar_catalogo(driver):
    driver.get(URL_MODULO)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # El listado llega por fetch (/api/catalogo/productos): esperar a que las
    # tarjetas reales reemplacen a los esqueletos de carga en #productos-grid
    tarjeta = espera.until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                "#productos-grid .producto-card:not(.producto-card--skeleton)",
            )
        )
    )
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#productos-grid .producto-card .btn-agregar")
        )
    )
    contador = driver.find_element(By.ID, "productos-count").text
    tarjetas = driver.find_elements(
        By.CSS_SELECTOR,
        "#productos-grid .producto-card:not(.producto-card--skeleton)",
    )
    nombre = tarjeta.find_element(By.CSS_SELECTOR, ".producto-nombre").text
    precio = tarjeta.find_element(By.CSS_SELECTOR, ".precio-usd").text
    assert len(tarjetas) >= 1
    assert nombre.strip() != ""
    assert precio.strip() != ""
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Catalogo listado: {contador} ({len(tarjetas)} tarjetas, primera: {nombre})")
