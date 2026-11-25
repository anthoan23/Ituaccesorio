import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_DASHBOARD = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/"
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

    # --- Verificaciones visuales de la pagina ---
    # Ojo: el block title usa "iTuAccesorio" (con esa capitalizacion), y el
    # dashboard no tiene breadcrumb ni hero: su encabezado son las tarjetas KPI.
    assert driver.title == "iTuAccesorio - Dashboard"
    # textContent (texto del DOM) por si el CSS renderiza en mayusculas
    etiquetas_kpi = [
        e.get_attribute("textContent").strip()
        for e in driver.find_elements(By.CSS_SELECTOR, ".kpi-card__label")
    ]
    assert etiquetas_kpi == ["Ventas Hoy", "Órdenes Activas", "Equipos Reparados", "Ingresos Mensuales"]
    assert driver.find_element(By.CSS_SELECTOR, ".chart-card__title").text == "Ingresos vs Gastos"
    assert driver.find_element(By.CSS_SELECTOR, ".chart-card__subtitle").text == "Últimos 7 días"
    assert driver.find_element(By.CSS_SELECTOR, ".activity-card__title").text == "Actividad Reciente"
    assert driver.find_element(By.CSS_SELECTOR, ".orders-card__title").text == "Órdenes Recientes"

    encabezados_ordenes = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, ".orders-table thead th")
    ]
    assert encabezados_ordenes == ["Orden", "Proveedor", "Estado", "Fecha", "Total"]

    acciones_rapidas = [
        b.get_attribute("textContent").strip()
        for b in driver.find_elements(By.CSS_SELECTOR, ".quick-action")
    ]
    assert acciones_rapidas == ["Nueva Orden", "Registrar Reparación", "Agregar Producto", "Nuevo Cliente"]

    etiquetas_widgets = [
        w.get_attribute("textContent").strip()
        for w in driver.find_elements(By.CSS_SELECTOR, ".widget__label")
    ]
    assert etiquetas_widgets == [
        "Reparaciones Pendientes",
        "Productos con Stock Bajo",
        "Ventas de la Semana",
        "Técnicos Activos",
    ]

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
    print(f"Dashboard renderizado: {visibles} elementos visibles")
