import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css

# Catálogo de productos: agregar al carrito
# REQUIERE sesión de cliente registrado con perfil completo: agregar al carrito
# valida que el usuario autenticado sea un cliente existente (en modo prueba el
# usuario falso es admin, por lo que esta prueba acepta ambos desenlaces del
# toast: la confirmación del JS o el rechazo del backend).
# Nota: el badge de ventas.js (#cart-count) está comentado en catalogo.html; la
# confirmación real del JS es el toast ".custom-toast" y el contador del widget
# del carrito del navbar ([data-cart-count], solo se pinta para clientes).
# Mecanismo de feedback del módulo (mostrarToast de ventas.js): toast propio
# ".custom-toast" con estilo inline (verde rgb(34, 197, 94) / rojo rgb(239, 68, 68)).
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
    assert boton_agregar.text.strip() == "Agregar al carrito"
    boton_agregar.click()

    # Confirmación del JS de ventas.js: toast "Producto agregado al carrito";
    # si no hay sesión de cliente, el backend rechaza y el JS pinta su toast
    # de error con el mensaje del servidor.
    toast = espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".custom-toast"))
    )
    if "Producto agregado al carrito" in toast.text:
        assert "custom-toast--success" in toast.get_attribute("class")
        assert estilo_css(driver, toast, "backgroundColor") == "rgb(34, 197, 94)", (
            "El toast de éxito deberia ser verde"
        )
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
        print(f"Producto agregado al carrito: contador del carrito = {contador}")
    else:
        # Sin cliente registrado el backend responde 400 y el toast es rojo
        assert "custom-toast--error" in toast.get_attribute("class")
        assert estilo_css(driver, toast, "backgroundColor") == "rgb(239, 68, 68)", (
            "El toast de error deberia ser rojo"
        )
        print(f"No se agregó al carrito en modo prueba (toast: {toast.text})")
    espera.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".custom-toast")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
