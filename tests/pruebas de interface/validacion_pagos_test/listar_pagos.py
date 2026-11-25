# Prerequisito: /admin/validar-pagos opera sobre facturas con pago pendiente
# creadas previamente por el flujo de carrito/procesar-pago. La prueba recorre
# las tres pestañas (Pendientes/Aprobados/Rechazados) y acepta tanto las
# tarjetas de pago como el mensaje de vacío que pinta el JS ("No hay pagos en
# esta lista"); no falla por falta de datos. Se asume ENTORNO_PRUEBA=true.
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_VALIDACION = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/admin/validar-pagos"
TIEMPO_ESPERA = 10


def test_listar_pagos(driver):
    driver.get(URL_VALIDACION)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # La pestaña Pendientes carga por fetch al iniciar la página (tarjetas o vacío)
    espera.until(EC.visibility_of_element_located((By.ID, "pendientes-tab")))
    espera.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "#pendientes-list .pago-card[data-factura], #pendientes-list .empty-state",
            )
        )
    )
    pendientes = driver.find_elements(
        By.CSS_SELECTOR, "#pendientes-list .pago-card[data-factura]"
    )
    print(f"Pagos pendientes listados: {len(pendientes)}")

    # Pestaña Aprobados (el JS recarga la lista por fetch al cambiar de pestaña)
    driver.find_element(By.CSS_SELECTOR, ".tab-btn[data-tab='aprobados']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "aprobados-tab")))
    espera.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "#aprobados-list .pago-card[data-factura], #aprobados-list .empty-state",
            )
        )
    )
    aprobados = driver.find_elements(
        By.CSS_SELECTOR, "#aprobados-list .pago-card[data-factura]"
    )
    print(f"Pagos aprobados listados: {len(aprobados)}")

    # Pestaña Rechazados
    driver.find_element(By.CSS_SELECTOR, ".tab-btn[data-tab='rechazados']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "rechazados-tab")))
    espera.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "#rechazados-list .pago-card[data-factura], #rechazados-list .empty-state",
            )
        )
    )
    rechazados = driver.find_elements(
        By.CSS_SELECTOR, "#rechazados-list .pago-card[data-factura]"
    )
    print(f"Pagos rechazados listados: {len(rechazados)}")

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print("Listados de validación de pagos cargados correctamente")
