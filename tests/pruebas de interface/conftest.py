# conftest.py
import pytest
from selenium import webdriver
from helpers import guardar_captura


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Guarda el reporte de cada fase en el nodo para que la fixture
    pueda saber si la prueba fallo."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture
def driver(request):
    """Configura e inicia el navegador Firefox antes de la prueba,
    guarda una captura si falla, y lo cierra al terminar."""

    # Opciones opcionales para Firefox (ej. headless si lo necesitas)
    options = webdriver.FirefoxOptions()
    # options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)
    driver.maximize_window()

    yield driver

    # --- Teardown inteligente ---
    # Verificamos si la prueba actual falló
    reporte = getattr(request.node, "rep_call", None)
    if reporte is not None and reporte.failed:
        # Usamos el nombre de la prueba para nombrar la captura
        nombre_test = request.node.name
        guardar_captura(driver, nombre=f"fallo_{nombre_test}")

    driver.quit()
