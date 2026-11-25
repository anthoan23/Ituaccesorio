import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css

# Catálogo de productos: página pública del módulo de ventas
URL_MODULO = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/catalogo"
TIEMPO_ESPERA = 10


def test_listar_catalogo(driver):
    driver.get(URL_MODULO)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == "Ituaccesorio - Catálogo de Productos"
    # El héroe del catálogo no usa breadcrumb; su h1 va en mayusculas
    assert espera.until(
        lambda d: d.find_element(By.CSS_SELECTOR, ".catalog-hero__title").text
    ) == "NUESTROS PRODUCTOS"
    assert driver.find_element(By.CSS_SELECTOR, ".catalog-hero__subtitle").text == (
        "Encuentra teléfonos, accesorios y repuestos pensados para iPhone y su ecosistema."
    )

    # Categorías destacadas que pinta la vista (textContent, el CSS las
    # renderiza en mayusculas)
    categorias = [
        el.get_attribute("textContent").strip()
        for el in driver.find_elements(By.CSS_SELECTOR, ".category-card__title")
    ]
    assert categorias == ["Telefonos", "Accesorios", "Repuestos", "Protección iPhone"]

    # Título de la sección de listado y subtítulo
    assert driver.find_element(
        By.CSS_SELECTOR, "#catalogo-completo .card__title"
    ).get_attribute("textContent").strip() == "Catálogo completo"
    assert driver.find_element(By.CSS_SELECTOR, ".catalog-browser__subtitle").text == (
        "Todos los productos disponibles en tienda."
    )

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
    # Texto dinámico del JS: "N producto" / "N productos"
    assert contador.endswith("producto") or contador.endswith("productos"), contador
    tarjetas = driver.find_elements(
        By.CSS_SELECTOR,
        "#productos-grid .producto-card:not(.producto-card--skeleton)",
    )
    nombre = tarjeta.find_element(By.CSS_SELECTOR, ".producto-nombre").text
    marca = tarjeta.find_element(By.CSS_SELECTOR, ".producto-marca").text
    precio = tarjeta.find_element(By.CSS_SELECTOR, ".precio-usd").text
    assert len(tarjetas) >= 1
    assert nombre.strip() != ""
    assert precio.startswith("$"), precio

    # --- Boton 'Agregar al carrito': gradiente amarillo con texto oscuro ---
    boton_agregar = tarjeta.find_element(By.CSS_SELECTOR, ".btn-agregar")
    assert boton_agregar.text.strip() == "Agregar al carrito"
    assert estilo_css(driver, boton_agregar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Agregar al carrito' deberia ser oscuro"
    )
    fondo = estilo_css(driver, boton_agregar, "backgroundImage")
    assert "rgb(243, 197, 0)" in fondo and "rgb(241, 187, 0)" in fondo, (
        f"El fondo de 'Agregar al carrito' deberia ser el gradiente amarillo: {fondo}"
    )

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Catalogo listado: {contador} ({len(tarjetas)} tarjetas, "
        f"primera: {nombre} / {marca} / {precio})"
    )
