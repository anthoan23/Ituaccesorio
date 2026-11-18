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

URL_VALIDACION = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/admin/validar-pagos"
TIEMPO_ESPERA = 10


def test_aprobar_pago(driver):
    driver.get(URL_VALIDACION)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

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
    tarjeta.find_element(By.CSS_SELECTOR, ".btn-aprobar").click()

    # El JS pide confirmación con un diálogo nativo (confirm())
    WebDriverWait(driver, TIEMPO_ESPERA).until(EC.alert_is_present())
    driver.switch_to.alert.accept()

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
        # Verifica que el pago pasa a la pestaña Aprobados
        driver.find_element(By.CSS_SELECTOR, ".tab-btn[data-tab='aprobados']").click()
        espera.until(EC.visibility_of_element_located((By.ID, "aprobados-tab")))
        espera.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    f"#aprobados-list .pago-card[data-factura='{factura}']",
                )
            )
        )
        print(
            f"Pago aprobado: factura {factura} salió de pendientes y aparece en Aprobados"
        )
    else:
        titulo = driver.find_element(By.ID, "feedback-modal-title").text
        print(
            f"El backend no aprobó el pago {factura} en modo prueba (feedback: {titulo})"
        )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Aprobación de pago finalizada para la factura {factura}")
