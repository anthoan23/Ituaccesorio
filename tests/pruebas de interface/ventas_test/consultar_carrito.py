import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Catálogo de productos: consultar el carrito desde la UI
# REQUIERE sesión de cliente registrado con perfil completo y carrito con items:
# el widget del carrito del navbar solo se pinta para clientes
# ({% if es_cliente %}) y /api/carrito exige un cliente existente; en modo
# prueba el usuario falso es admin, por lo que esta prueba puede fallar en
# runtime. El widget del navbar ([data-cart-toggle] -> [data-cart-panel]) es la
# vista del carrito accesible por UI: el modal #cart-modal de catalogo.html
# existe pero su botón de apertura (#cart-toggle) está comentado.
URL_MODULO = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/catalogo"
TIEMPO_ESPERA = 10


def test_consultar_carrito(driver):
    driver.get(URL_MODULO)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # Abrir el carrito desde el botón del navbar
    toggle = espera.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-cart-toggle]"))
    )
    toggle.click()
    espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-cart-panel]"))
    )
    # El panel recarga el carrito desde el backend al abrirse: esperar items
    item = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[data-cart-list] .cart-item")
        )
    )
    nombre = item.find_element(By.CSS_SELECTOR, ".cart-item__name").text
    contador = driver.find_element(By.CSS_SELECTOR, "[data-cart-count]").text
    total = driver.find_element(By.CSS_SELECTOR, "[data-cart-total]").text
    assert contador not in ("", "0 productos")
    assert total not in ("", "Bs. 0")
    # Cerrar el panel del carrito (el botón alterna oculto/visible)
    driver.find_element(By.CSS_SELECTOR, "[data-cart-toggle]").click()
    espera.until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, "[data-cart-panel]"))
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Carrito consultado: {contador}, total {total}, primer item: {nombre}")
