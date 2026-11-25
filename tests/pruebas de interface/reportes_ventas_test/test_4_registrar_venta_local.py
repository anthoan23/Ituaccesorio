# Prerequisito: usa el flujo de venta local del propio módulo de reportes
# (modal "Nueva Venta Local": buscador de clientes por fetch, productos del
# catálogo por fetch y método de pago). Registra una venta con el PRIMER
# cliente disponible, el PRIMER producto del select con cantidad 1 y método
# efectivo USD. Si no hay clientes o productos disponibles, informa y termina
# sin fallar por falta de datos; si el backend rechaza el registro, informa el
# error pintado por la UI (modal de feedback). Se asume ENTORNO_PRUEBA=true.
import os

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from helpers import estilo_css, quitar_hover

URL_REPORTES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/admin/reportes-ventas"
TIEMPO_ESPERA = 10

# [consulta del cliente, cantidad, metodo de pago]
DATOS_VENTA_LOCAL = ["a", "1", "efectivo_usd"]


def test_registrar_venta_local(driver):
    driver.get(URL_REPORTES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Abre el modal de nueva venta local
    driver.find_element(By.ID, "btn-venta-local").click()
    espera.until(EC.visibility_of_element_located((By.ID, "venta-local-modal")))
    quitar_hover(driver)

    # --- Modal 'Nueva Venta Local': titulo y botones de acción ---
    assert driver.find_element(By.ID, "venta-local-title").text == "Nueva Venta Local"
    boton_agregar = driver.find_element(By.ID, "agregar-producto-local")
    assert boton_agregar.text.strip() == "Agregar"
    assert "ui-btn--primary" in boton_agregar.get_attribute("class")
    assert estilo_css(driver, boton_agregar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Agregar' deberia ser amarillo"
    )
    boton_registrar = driver.find_element(By.ID, "btn-registrar-venta-local")
    assert boton_registrar.text.strip() == "Registrar Venta"
    assert estilo_css(driver, boton_registrar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Registrar Venta' deberia ser amarillo"
    )
    assert driver.find_element(
        By.CSS_SELECTOR, "#venta-local-modal .ui-form__actions [data-close-modal]"
    ).text.strip() == "Cancelar"

    # Lista vacía inicial de productos agregados (texto dinámico del JS)
    assert driver.find_element(
        By.CSS_SELECTOR, "#items-local-list .sin-resultados"
    ).text == "No hay productos agregados"

    # --- Validación del front (toast propio del módulo): sin producto no agrega ---
    boton_agregar.click()
    toast = espera.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".custom-toast.custom-toast--error")
        )
    )
    assert "Selecciona un producto" in toast.text
    espera.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".custom-toast")))

    # Busca el primer cliente disponible (el cache de clientes carga por fetch)
    busqueda = driver.find_element(By.ID, "cliente-busqueda-input")
    busqueda.send_keys(DATOS_VENTA_LOCAL[0])
    espera.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "#cliente-resultados .resultado-item, #cliente-resultados .sin-resultados",
            )
        )
    )
    resultados = driver.find_elements(
        By.CSS_SELECTOR, "#cliente-resultados .resultado-item"
    )
    if not resultados:
        # El cache puede seguir cargando: reintenta con el botón de búsqueda
        driver.find_element(By.ID, "cliente-buscar-btn").click()
        espera.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "#cliente-resultados .resultado-item, #cliente-resultados .sin-resultados",
                )
            )
        )
        resultados = driver.find_elements(
            By.CSS_SELECTOR, "#cliente-resultados .resultado-item"
        )
    if not resultados:
        driver.find_element(By.CSS_SELECTOR, "#venta-local-modal .ui-modal__close").click()
        espera.until(EC.invisibility_of_element_located((By.ID, "venta-local-modal")))
        print("No hay clientes disponibles; no se registra la venta local")
        return
    resultados[0].click()
    espera.until(EC.visibility_of_element_located((By.ID, "cliente-seleccionado")))
    assert driver.find_element(
        By.ID, "cliente-id"
    ).get_attribute("value"), "No se seleccionó ningún cliente"

    # Primer producto disponible en el select del catálogo
    try:
        espera.until(
            lambda navegador: len(
                Select(navegador.find_element(By.ID, "producto-select")).options
            )
            > 1
        )
    except TimeoutException:
        driver.find_element(By.CSS_SELECTOR, "#venta-local-modal .ui-modal__close").click()
        espera.until(EC.invisibility_of_element_located((By.ID, "venta-local-modal")))
        print("No hay productos disponibles en el catálogo; no se registra la venta local")
        return
    Select(driver.find_element(By.ID, "producto-select")).select_by_index(1)
    cantidad = driver.find_element(By.ID, "cantidad-local")
    cantidad.clear()
    cantidad.send_keys(DATOS_VENTA_LOCAL[1])
    boton_agregar.click()
    # El JS pinta el item con su subtotal y el total acumulado
    espera.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#items-local-list .cart-item"))
    )
    assert "x1" in driver.find_element(
        By.CSS_SELECTOR, "#items-local-list .cart-item span"
    ).text

    # Método de pago efectivo USD y registro de la venta
    Select(driver.find_element(By.ID, "metodo-local")).select_by_value(
        DATOS_VENTA_LOCAL[2]
    )
    espera.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".custom-toast")))
    boton_registrar.click()

    # El interceptor global de fetch abre el modal de feedback con el resultado
    # ('Acción exitosa') y el JS muestra además su toast "Venta registrada: F..."
    espera.until(EC.visibility_of_element_located((By.ID, "feedback-modal")))
    titulo = driver.find_element(By.ID, "feedback-modal-title").text

    if titulo == "Acción exitosa":
        # El JS muestra además su toast propio: "Venta registrada: <factura>"
        toast = espera.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".custom-toast.custom-toast--success")
            )
        )
        assert "Venta registrada: " in toast.text
        espera.until(EC.invisibility_of_element_located((By.ID, "venta-local-modal")))
        espera.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".custom-toast")))
        # La lista de ventas locales se recarga con la nueva factura
        driver.find_element(By.CSS_SELECTOR, ".tab-btn[data-tab='ventas-local']").click()
        espera.until(EC.visibility_of_element_located((By.ID, "ventas-local-tab")))
        espera.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "#ventas-locales-tabla .btn-ver-detalle-reporte, "
                    "#ventas-locales-tabla td.table__empty",
                )
            )
        )
        facturas = driver.find_elements(
            By.CSS_SELECTOR, "#ventas-locales-tabla .btn-ver-detalle-reporte"
        )
        print(
            f"Venta local registrada y lista de Ventas Locales actualizada "
            f"({len(facturas)} facturas)"
        )
    else:
        mensaje = driver.find_element(By.ID, "feedback-modal-message").text
        driver.find_element(By.CSS_SELECTOR, "#venta-local-modal .ui-modal__close").click()
        espera.until(EC.invisibility_of_element_located((By.ID, "venta-local-modal")))
        print(
            f"El backend no registró la venta local (feedback: {titulo} - {mensaje})"
        )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print("Registro de venta local finalizado")
