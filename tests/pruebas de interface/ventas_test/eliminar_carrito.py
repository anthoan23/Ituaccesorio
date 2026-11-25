import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Catálogo de productos: eliminar un item del carrito
# REQUIERE sesión de cliente registrado con perfil completo y carrito con al
# menos un item: en modo prueba el usuario falso es admin, por lo que esta
# prueba puede fallar en runtime. Se usa la vista del carrito del navbar
# ([data-cart-toggle] -> [data-cart-panel]); el botón "Vaciar" (#cart-vaciar)
# existe solo en el modal #cart-modal de catalogo.html, cuya apertura está
# comentada en la vista, por lo que no se ejercita en esta prueba.
URL_MODULO = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/catalogo"
TIEMPO_ESPERA = 10


def test_eliminar_carrito(driver):
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
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[data-cart-list] .cart-item")
        )
    )
    items_antes = len(
        driver.find_elements(By.CSS_SELECTOR, "[data-cart-list] .cart-item")
    )
    nombre = driver.find_element(
        By.CSS_SELECTOR, "[data-cart-list] .cart-item .cart-item__name"
    ).text
    # Eliminar el primer item con su botón de eliminar (icono X del item)
    driver.find_element(
        By.CSS_SELECTOR, "[data-cart-list] .cart-item [data-cart-action='remove']"
    ).click()
    # El JS elimina el item del backend y re-renderiza el panel
    espera.until(
        lambda navegador: len(
            navegador.find_elements(By.CSS_SELECTOR, "[data-cart-list] .cart-item")
        )
        == items_antes - 1
    )
    nombres_restantes = [
        el.text
        for el in driver.find_elements(
            By.CSS_SELECTOR, "[data-cart-list] .cart-item .cart-item__name"
        )
    ]
    assert nombre not in nombres_restantes
    contador = driver.find_element(By.CSS_SELECTOR, "[data-cart-count]").text
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Item eliminado del carrito: '{nombre}' (restan: {contador})")
