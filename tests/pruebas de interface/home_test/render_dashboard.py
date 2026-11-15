import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_DASHBOARD = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/"
TIEMPO_ESPERA = 10

# Se asume ENTORNO_PRUEBA=true: el before_request inyecta un usuario admin
# falso, de lo contrario "/" redirige al catalogo y el dashboard no renderiza.

# IDs reales del dashboard (views/index.html + app/static/js/index.js)
SELECTORES_DASHBOARD = [
    "#kpi-ventas-hoy",        # tarjeta de ventas de hoy
    "#kpi-ordenes-activas",   # tarjeta de ordenes activas
    "#kpi-reparados",         # tarjeta de equipos reparados
    "#kpi-ingresos",          # tarjeta de ingresos mensuales
    "#chart-container",       # contenedor del grafico Ingresos vs Gastos
    "#main-chart",            # canvas del grafico (Chart.js)
    "#activity-list",         # lista de actividad reciente
    "#orders-table-body",     # tabla de ordenes recientes
]


def test_render_dashboard(driver):
    driver.get(URL_DASHBOARD)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    for selector in SELECTORES_DASHBOARD:
        espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

    # index.js carga los datos por fetch: espera a que reemplace el estado
    # de "Cargando..." (sin depender de valores numericos concretos)
    espera.until(
        lambda d: "Cargando..." not in d.find_element(By.ID, "orders-table-body").text
    )
    espera.until(
        lambda d: "Cargando actividad" not in d.find_element(By.ID, "activity-list").text
    )

    # Al menos 2 elementos clave del dashboard deben estar visibles
    visibles = 0
    for selector in SELECTORES_DASHBOARD:
        elemento = driver.find_element(By.CSS_SELECTOR, selector)
        if elemento.is_displayed():
            visibles += 1
    assert visibles >= 2

    canvas = driver.find_element(By.ID, "main-chart")
    tarjeta_ventas = driver.find_element(By.ID, "kpi-ventas-hoy")
    assert canvas.is_displayed()
    assert tarjeta_ventas.is_displayed()
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Dashboard renderizado: {visibles} elementos visibles")
