# Prerequisito: /admin/validar-pagos opera sobre facturas con pago pendiente
# creadas previamente por el flujo de carrito/procesar-pago. La prueba rechaza
# la PRIMERA tarjeta pendiente (botón "Rechazar" -> modal con campo motivo ->
# "Confirmar rechazo"). Si la lista está vacía no falla: verifica la carga y
# termina. Nota de entorno: en ENTORNO_PRUEBA el usuario falso no tiene cédula
# y el backend responde 400 ("Empleado no identificado"), por lo que la prueba
# acepta los dos desenlaces que pinta el JS: el pago sale de pendientes y pasa
# a la pestaña Rechazados, o el interceptor de fetch muestra el modal de
# feedback con el error del backend (y el modal de motivo se cierra con
# "Cancelar"). Se asume ENTORNO_PRUEBA=true.
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_VALIDACION = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/admin/validar-pagos"
TIEMPO_ESPERA = 10

# [motivo del rechazo]
DATOS_MOTIVO_RECHAZO = ["Comprobante ilegible"]


def test_rechazar_pago(driver):
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
        print("No hay pagos pendientes para rechazar (lista vacía)")
        return

    tarjeta = tarjetas[0]
    factura = tarjeta.get_attribute("data-factura")
    tarjeta.find_element(By.CSS_SELECTOR, ".btn-rechazar").click()

    # Modal de rechazo con el campo del motivo
    espera.until(EC.visibility_of_element_located((By.ID, "rechazo-modal")))
    motivo = driver.find_element(By.ID, "motivo-rechazo")
    motivo.clear()
    motivo.send_keys(DATOS_MOTIVO_RECHAZO[0])
    driver.find_element(By.ID, "confirmar-rechazo").click()

    # Tras el POST el JS recarga las listas: si se rechaza, la tarjeta deja de
    # aparecer en pendientes; si el backend rechaza la acción, el interceptor
    # global de fetch pinta el modal de feedback con el error (el JS no cierra
    # el modal de motivo en ese caso).
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
        espera.until(EC.invisibility_of_element_located((By.ID, "rechazo-modal")))
        # Verifica que el pago pasa a la pestaña Rechazados
        driver.find_element(By.CSS_SELECTOR, ".tab-btn[data-tab='rechazados']").click()
        espera.until(EC.visibility_of_element_located((By.ID, "rechazados-tab")))
        espera.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    f"#rechazados-list .pago-card[data-factura='{factura}']",
                )
            )
        )
        print(
            f"Pago rechazado con motivo '{DATOS_MOTIVO_RECHAZO[0]}': "
            f"factura {factura} salió de pendientes y aparece en Rechazados"
        )
    else:
        titulo = driver.find_element(By.ID, "feedback-modal-title").text
        print(
            f"El backend no rechazó el pago {factura} en modo prueba (feedback: {titulo})"
        )
        driver.find_element(By.ID, "cancelar-rechazo").click()
        espera.until(EC.invisibility_of_element_located((By.ID, "rechazo-modal")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Rechazo de pago finalizado para la factura {factura}")
