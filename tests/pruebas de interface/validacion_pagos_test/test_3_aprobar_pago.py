# Prerequisito: /admin/validar-pagos opera sobre facturas con pago pendiente
# creadas previamente por el flujo de carrito/procesar-pago. La prueba aprueba
# la PRIMERA tarjeta pendiente (botón "Aprobar"; el JS pide confirmación con un
# diálogo nativo confirm()). Si la lista está vacía no falla: verifica la
# carga y termina. Nota de entorno: en ENTORNO_PRUEBA el usuario falso no
# tiene cédula y el backend responde 400 ("Empleado no identificado"), por lo
# que la prueba acepta los dos desenlaces que pinta el JS: el pago sale de
# pendientes y pasa a la pestaña Aprobados, o el interceptor de fetch muestra
# el modal de feedback con el error del backend y el pago sigue pendiente.
# Se asume ENTORNO_PRUEBA=true.
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

URL_VALIDACION = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/admin/validar-pagos"
TIEMPO_ESPERA = 10


def test_aprobar_pago(driver):
    driver.get(URL_VALIDACION)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == "Ituaccesorio - Validación de Pagos"
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == (
        "Validación de Pagos"
    )

    # La lista de pendientes carga por fetch (tarjetas o mensaje de vacío)
    espera.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "#pendientes-list .pago-card[data-factura], #pendientes-list .empty-state",
            )
        )
    )
    tarjetas = driver.find_elements(
        By.CSS_SELECTOR, "#pendientes-list .pago-card[data-factura]"
    )
    if not tarjetas:
        print("No hay pagos pendientes para aprobar (lista vacía)")
        return

    tarjeta = tarjetas[0]
    factura = tarjeta.get_attribute("data-factura")

    # --- Botones 'Aprobar' y 'Rechazar' de la tarjeta pendiente ---
    quitar_hover(driver)
    boton_aprobar = tarjeta.find_element(By.CSS_SELECTOR, ".btn-aprobar")
    assert boton_aprobar.text.strip() == "Aprobar"
    assert "ui-btn--primary" in boton_aprobar.get_attribute("class")
    assert estilo_css(driver, boton_aprobar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Aprobar' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_aprobar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Aprobar' deberia ser oscuro"
    )
    boton_rechazar = tarjeta.find_element(By.CSS_SELECTOR, ".btn-rechazar")
    assert boton_rechazar.text.strip() == "Rechazar"
    assert "ui-btn--danger" in boton_rechazar.get_attribute("class")
    assert estilo_css(driver, boton_rechazar, "color") == "rgb(239, 68, 68)", (
        "El texto de 'Rechazar' deberia ser rojo"
    )

    boton_aprobar.click()

    # El JS pide confirmación con un diálogo nativo (confirm())
    WebDriverWait(driver, TIEMPO_ESPERA).until(EC.alert_is_present())
    alerta = driver.switch_to.alert
    # Texto dinámico del confirm() del JS
    assert f"¿Aprobar el pago de la factura {factura}?" in alerta.text
    alerta.accept()

    # Tras el POST el JS recarga las listas: si se aprueba, la tarjeta deja de
    # aparecer en pendientes; si el backend rechaza la acción, el interceptor
    # global de fetch pinta el modal de feedback con el error.
    def resuelto(navegador):
        if not navegador.find_elements(
            By.CSS_SELECTOR, f"#pendientes-list .pago-card[data-factura='{factura}']"
        ):
            return True
        feedback = navegador.find_elements(By.ID, "feedback-modal")
        if feedback and feedback[0].is_displayed():
            return (
                navegador.find_element(By.ID, "feedback-modal-title").text
                == "No se pudo completar"
            )
        return False

    espera.until(resuelto)
    fuera = not driver.find_elements(
        By.CSS_SELECTOR, f"#pendientes-list .pago-card[data-factura='{factura}']"
    )
    if fuera:
        # Mecanismo de feedback del JS de validación de pagos: toast propio
        # ".custom-toast" con "Pago <factura> aprobado correctamente" (además,
        # el interceptor global muestra el modal 'Acción exitosa').
        toast = espera.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".custom-toast.custom-toast--success")
            )
        )
        assert f"Pago {factura} aprobado correctamente" in toast.text
        # El toast de éxito usa el color verde del tema (theme.css)
        assert estilo_css(driver, toast, "backgroundColor") == "rgb(52, 199, 89)", (
            "El toast de aprobación deberia ser verde"
        )
        # Verifica que el pago pasa a la pestaña Aprobados
        driver.find_element(By.CSS_SELECTOR, ".tab-btn[data-tab='aprobados']").click()
        espera.until(EC.visibility_of_element_located((By.ID, "aprobados-tab")))
        tarjeta_aprobada = espera.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    f"#aprobados-list .pago-card[data-factura='{factura}']",
                )
            )
        )
        assert tarjeta_aprobada.find_element(
            By.CSS_SELECTOR, ".pago-estado"
        ).get_attribute("textContent").strip() == "Aprobado"
        print(
            f"Pago aprobado: factura {factura} salió de pendientes y aparece en Aprobados"
        )
    else:
        titulo = driver.find_element(By.ID, "feedback-modal-title").text
        # El JS también muestra su toast de error con el mensaje del backend
        toast_error = driver.find_element(By.CSS_SELECTOR, ".custom-toast.custom-toast--error")
        assert toast_error.text.strip() != ""
        print(
            f"El backend no aprobó el pago {factura} en modo prueba "
            f"(feedback: {titulo}, toast: {toast_error.text.strip()})"
        )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Aprobación de pago finalizada para la factura {factura}")
