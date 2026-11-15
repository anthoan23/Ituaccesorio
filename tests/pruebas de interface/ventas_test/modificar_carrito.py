import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Catálogo de productos: modificar la cantidad de un item del carrito
# REQUIERE sesión de cliente registrado con perfil completo, carrito con items y
# stock disponible del producto (el backend rechaza cantidades superiores al
# stock): en modo prueba el usuario falso es admin, por lo que esta prueba puede
# fallar en runtime. Se usa la vista del carrito del navbar
# ([data-cart-toggle] -> [data-cart-panel]); el modal #cart-modal de
# catalogo.html existe pero su botón de apertura (#cart-toggle) está comentado.
URL_MODULO = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/catalogo"
TIEMPO_ESPERA = 10


def test_modificar_carrito(driver):
    driver.get(URL_MODULO)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # Abrir el carrito y esperar a que el backend cargue los items
    toggle = espera.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-cart-toggle]"))
    )
    toggle.click()
    espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-cart-panel]"))
    )
    item = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[data-cart-list] .cart-item")
        )
    )
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
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Cantidad modificada: {cantidad_antes} -> {cantidad_esperada} "
        f"(total {total_antes} -> {total_nuevo})"
    )
