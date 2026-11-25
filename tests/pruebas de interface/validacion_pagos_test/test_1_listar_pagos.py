# Prerequisito: /admin/validar-pagos opera sobre facturas con pago pendiente
# creadas previamente por el flujo de carrito/procesar-pago. La prueba recorre
# las tres pestañas (Pendientes/Aprobados/Rechazados) y acepta tanto las
# tarjetas de pago como el mensaje de vacío que pinta el JS ("No hay pagos en
# esta lista"); no falla por falta de datos. Se asume ENTORNO_PRUEBA=true.
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

URL_VALIDACION = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/admin/validar-pagos"
TIEMPO_ESPERA = 10


def test_listar_pagos(driver):
    driver.get(URL_VALIDACION)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == "Ituaccesorio - Validación de Pagos"
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == (
        "Validación de Pagos"
    )
    assert espera.until(
        lambda d: d.find_element(By.CSS_SELECTOR, ".hero__title").text
    ) == "Validación de Pagos"

    # Boton 'Reportes' del héroe: estilo fantasma del tema oscuro
    boton_reportes = driver.find_element(By.ID, "btn-reportes-pagos")
    assert boton_reportes.text.strip() == "Reportes"
    assert "ui-btn--ghost" in boton_reportes.get_attribute("class")
    assert estilo_css(driver, boton_reportes, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Reportes' deberia ser el ghost del tema oscuro"

    # Pestañas visibles: la activa queda amarilla con texto oscuro
    tabs = driver.find_elements(By.CSS_SELECTOR, ".tab-btn")
    assert [t.get_attribute("textContent").strip() for t in tabs] == [
        "Pendientes", "Aprobados", "Rechazados"
    ]
    tab_activa = driver.find_element(By.CSS_SELECTOR, ".tab-btn.is-active")
    assert tab_activa.get_attribute("textContent").strip() == "Pendientes"
    assert estilo_css(driver, tab_activa, "backgroundColor") == "rgb(243, 197, 0)", (
        "La pestaña activa deberia tener fondo amarillo"
    )
    assert estilo_css(driver, tab_activa, "color") == "rgb(18, 18, 18)", (
        "El texto de la pestaña activa deberia ser oscuro"
    )

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
    if not pendientes:
        vacio = driver.find_element(By.CSS_SELECTOR, "#pendientes-list .empty-state")
        assert vacio.text == "No hay pagos en esta lista"
        print("Pagos pendientes: lista vacía (mensaje del JS)")
    for tarjeta in pendientes[:2]:
        # Badge de estado (textContent, el CSS lo renderiza en mayusculas)
        badge = tarjeta.find_element(By.CSS_SELECTOR, ".pago-estado")
        assert badge.get_attribute("textContent").strip() == "Pendiente"
        # Encabezado dinamico del JS: "Factura: X"
        assert tarjeta.find_element(By.CSS_SELECTOR, ".pago-factura").text.startswith(
            "Factura: "
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
    quitar_hover(driver)
    if aprobados:
        # Badge verde de estado aprobado
        badge = aprobados[0].find_element(By.CSS_SELECTOR, ".pago-estado.aprobado")
        assert badge.get_attribute("textContent").strip() == "Aprobado"
        assert estilo_css(driver, badge, "color") == "rgb(34, 197, 94)", (
            "El badge 'Aprobado' deberia ser verde"
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
    if rechazados:
        # Badge rojo de estado rechazado
        badge = rechazados[0].find_element(By.CSS_SELECTOR, ".pago-estado.rechazado")
        assert badge.get_attribute("textContent").strip() == "Rechazado"
        assert estilo_css(driver, badge, "color") == "rgb(239, 68, 68)", (
            "El badge 'Rechazado' deberia ser rojo"
        )
    print(f"Pagos rechazados listados: {len(rechazados)}")

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print("Listados de validación de pagos cargados correctamente")
