import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Catálogo de productos: página pública del módulo de ventas
# REQUIERE sesión de cliente registrado con perfil completo: agregar al carrito
# valida que el usuario autenticado sea un cliente existente (en modo prueba el
# usuario falso es admin, por lo que esta prueba puede fallar en runtime).
# Nota: el badge de ventas.js (#cart-count) está comentado en catalogo.html; la
# confirmación real del JS es el toast ".custom-toast" y el contador del widget
# del carrito del navbar ([data-cart-count], solo se pinta para clientes).
URL_MODULO = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/catalogo"
TIEMPO_ESPERA = 10


def test_agregar_carrito(driver):
    driver.get(URL_MODULO)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # Esperar a que el fetch cargue las tarjetas con productos reales
    espera.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "#productos-grid .producto-card:not(.producto-card--skeleton)",
            )
        )
    )
    # Botón "Agregar al carrito" de la primera tarjeta con stock disponible
    boton_agregar = espera.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "#productos-grid .producto-card:not(.producto-card--skeleton) "
                ".btn-agregar:not([disabled])",
            )
        )
    )
    boton_agregar.click()
    # Confirmación del JS de ventas.js: toast "Producto agregado al carrito"
    toast = espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".custom-toast"))
    )
    assert "Producto agregado al carrito" in toast.text
    # Verificar el contador del carrito actualizado en el widget del navbar
    toggle = espera.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-cart-toggle]"))
    )
    toggle.click()
    espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-cart-panel]"))
    )
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[data-cart-list] .cart-item")
        )
    )
    contador = driver.find_element(By.CSS_SELECTOR, "[data-cart-count]").text
    assert contador not in ("", "0 productos")
    # Cerrar el panel del carrito
    driver.find_element(By.CSS_SELECTOR, "[data-cart-toggle]").click()
    espera.until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, "[data-cart-panel]"))
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Producto agregado al carrito: contador del carrito = {contador}")
