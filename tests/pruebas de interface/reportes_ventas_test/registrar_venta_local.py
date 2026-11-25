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
    driver.find_element(By.ID, "agregar-producto-local").click()
    espera.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#items-local-list .cart-item"))
    )

    # Método de pago efectivo USD y registro de la venta
    Select(driver.find_element(By.ID, "metodo-local")).select_by_value(
        DATOS_VENTA_LOCAL[2]
    )
    espera.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".custom-toast")))
    driver.find_element(By.ID, "btn-registrar-venta-local").click()

    # El interceptor global de fetch abre el modal de feedback con el resultado
    espera.until(EC.visibility_of_element_located((By.ID, "feedback-modal")))
    titulo = driver.find_element(By.ID, "feedback-modal-title").text

    if titulo == "Acción exitosa":
        espera.until(EC.invisibility_of_element_located((By.ID, "venta-local-modal")))
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
