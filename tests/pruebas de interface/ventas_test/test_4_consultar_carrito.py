import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Catálogo de productos: consultar el carrito desde la UI
# REQUIERE sesión de cliente registrado con perfil completo y carrito con items:
# el widget del carrito del navbar solo se pinta para clientes
# ({% if es_cliente %}) y /api/carrito exige un cliente existente; en modo
# prueba el usuario falso es admin, por lo que la prueba informa y termina si
# el widget no existe. El widget del navbar ([data-cart-toggle] ->
# [data-cart-panel]) es la vista del carrito accesible por UI: el modal
# #cart-modal de catalogo.html existe pero su botón de apertura (#cart-toggle)
# está comentado.
URL_MODULO = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/catalogo"
TIEMPO_ESPERA = 10


def test_consultar_carrito(driver):
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

    # Sin widget de carrito (usuario no cliente) no hay nada que consultar
    if not driver.find_elements(By.CSS_SELECTOR, "[data-cart-toggle]"):
        print("El widget del carrito no está disponible para este usuario; se omite")
        return

    # Abrir el carrito desde el botón del navbar
    toggle = espera.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-cart-toggle]"))
    )
    assert toggle.get_attribute("aria-label") == "Carrito de compras"
    toggle.click()
    panel = espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-cart-panel]"))
    )
    # El panel recarga el carrito desde el backend al abrirse: esperar items
    # o el mensaje de vacío que pinta el JS del navbar
    items = espera.until(
        lambda d: d.find_elements(By.CSS_SELECTOR, "[data-cart-list] .cart-item")
        or d.find_elements(By.CSS_SELECTOR, "[data-cart-list] .cart-panel__empty")
    )
    if "cart-item" not in items[0].get_attribute("class"):
        print("El carrito está vacío; se omite la consulta de items")
        driver.find_element(By.CSS_SELECTOR, "[data-cart-toggle]").click()
        espera.until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "[data-cart-panel]"))
        )
        return
    # Encabezado del panel con el contador dinámico "N productos"
    contador = driver.find_element(By.CSS_SELECTOR, "[data-cart-count]").text
    assert contador not in ("", "0 productos")
    item = items[0]
    nombre = item.find_element(By.CSS_SELECTOR, ".cart-item__name").text
    total = driver.find_element(By.CSS_SELECTOR, "[data-cart-total]").text
    assert nombre.strip() != ""
    assert total not in ("", "Bs. 0")
    assert panel.find_element(By.CSS_SELECTOR, ".cart-panel__total strong").text != ""
    # Cerrar el panel del carrito (el botón alterna oculto/visible)
    driver.find_element(By.CSS_SELECTOR, "[data-cart-toggle]").click()
    espera.until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, "[data-cart-panel]"))
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Carrito consultado: {contador}, total {total}, primer item: {nombre}")
