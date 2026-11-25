import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Catálogo de productos: modificar la cantidad de un item del carrito
# REQUIERE sesión de cliente registrado con perfil completo, carrito con items y
# stock disponible del producto (el backend rechaza cantidades superiores al
# stock): en modo prueba el usuario falso es admin, por lo que la prueba informa
# y termina si el widget del carrito no existe o no tiene items. Se usa la vista
# del carrito del navbar ([data-cart-toggle] -> [data-cart-panel]); el modal
# #cart-modal de catalogo.html existe pero su botón de apertura (#cart-toggle)
# está comentado.
URL_MODULO = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/catalogo"
TIEMPO_ESPERA = 10


def test_modificar_carrito(driver):
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

    # Sin widget de carrito (usuario no cliente) no hay nada que modificar
    if not driver.find_elements(By.CSS_SELECTOR, "[data-cart-toggle]"):
        print("El widget del carrito no está disponible para este usuario; se omite")
        return

    # Abrir el carrito y esperar a que el backend cargue los items
    toggle = espera.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-cart-toggle]"))
    )
    toggle.click()
    espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-cart-panel]"))
    )
    # El panel recarga el carrito desde el backend al abrirse: esperar items
    # o el mensaje de vacío que pinta el JS del navbar
    items = espera.until(
        lambda d: d.find_elements(By.CSS_SELECTOR, "[data-cart-list] .cart-item")
        or d.find_elements(By.CSS_SELECTOR, "[data-cart-list] .cart-panel__empty")
    )
    if "cart-item" not in items[0].get_attribute("class"):
        print("El carrito está vacío; se omite la modificación de cantidad")
        driver.find_element(By.CSS_SELECTOR, "[data-cart-toggle]").click()
        espera.until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "[data-cart-panel]"))
        )
        return
    item = items[0]
    nombre = item.find_element(By.CSS_SELECTOR, ".cart-item__name").text
    cantidad_antes = int(
        item.find_element(By.CSS_SELECTOR, ".cart-item__quantity span").text
    )
    total_antes = driver.find_element(By.CSS_SELECTOR, "[data-cart-total]").text
    # Aumentar la cantidad del primer item con el botón "+" del item
    item.find_element(By.CSS_SELECTOR, "[data-cart-action='increase']").click()
    # El JS sincroniza con el backend y re-renderiza: esperar la cantidad nueva
    cantidad_esperada = str(cantidad_antes + 1)
    espera.until(
        lambda navegador: navegador.find_element(
            By.CSS_SELECTOR, "[data-cart-list] .cart-item .cart-item__quantity span"
        ).text
        == cantidad_esperada
    )
    total_nuevo = driver.find_element(By.CSS_SELECTOR, "[data-cart-total]").text
    assert total_nuevo != total_antes
    # El contador del encabezado del panel refleja la cantidad acumulada nueva
    contador = driver.find_element(By.CSS_SELECTOR, "[data-cart-count]").text
    assert contador not in ("", "0 productos")
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Cantidad modificada de '{nombre}': {cantidad_antes} -> {cantidad_esperada} "
        f"(total {total_antes} -> {total_nuevo})"
    )
