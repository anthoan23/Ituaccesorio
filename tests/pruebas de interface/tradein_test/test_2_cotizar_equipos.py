import os
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from helpers import esperar_feedback

URL_TRADEIN = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/trade-in"
TIEMPO_ESPERA = 10

# Etiquetas reales de las casillas de fallas (views/tradein.html / FALLAS_COTIZACION)
FALLAS_PRUEBA = ["LCD", "Mica"]

# PRERREQUISITO: equipos Apple en existencias y repuestos con costo en la BD
# (el backend deduce el costo del repuesto). El ID de inventario del equipo debe
# ser numérico porque /api/trade-in/cotizar lo valida con validar_numero (1-10 dígitos).
#
# MECANISMO DE FEEDBACK DE ESTE MODULO: tradein.js NO usa FeedbackModal propio;
# el resultado (monto, deducciones, mensajes) se pinta inline en la tarjeta
# "Resultado estimado" (#tradein-mensajes con <p class="success|warning|error">).
# Ademas, el interceptor global de feedback-modal.js envuelve window.fetch y
# muestra el modal de exito generico para todo POST /api/... no excluido
# (titulo 'Acción exitosa', mensaje 'Registro realizado satisfactoriamente.'),
# que aqui se verifica con esperar_feedback.


def test_cotizar_equipos(driver):
    driver.get(URL_TRADEIN)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#tradein-equipo option:not([value=''])")
        )
    )

    # ---------------------------------------------------------------
    # (1) Enviar sin equipo: validacion del front (sin fetch) -> error
    # inline en #tradein-mensajes y montos en cero, sin modal de feedback
    # ---------------------------------------------------------------
    driver.find_element(By.ID, "tradein-submit").click()
    espera.until(
        EC.text_to_be_present_in_element(
            (By.ID, "tradein-mensajes"), "Selecciona un equipo para continuar."
        )
    )
    assert driver.find_element(By.ID, "tradein-monto").text == "$0.00"
    assert driver.find_element(By.ID, "tradein-total-fallas").text == "0"
    assert not driver.find_elements(
        By.CSS_SELECTOR, "#feedback-modal:not([hidden])"
    ), "No deberia abrirse el modal de feedback sin equipo seleccionado"

    # ---------------------------------------------------------------
    # (2) Equipo bloqueado (liberado = no): alerta visible y 'Cotizar'
    # deshabilitado por el JS
    # ---------------------------------------------------------------
    driver.find_element(By.CSS_SELECTOR, "input[name='liberado'][value='no']").click()
    alerta = espera.until(
        EC.visibility_of_element_located((By.ID, "tradein-liberacion-alerta"))
    )
    assert alerta.text.strip() == (
        "Lo sentimos, el equipo debe estar liberado para calificar."
    )
    assert not driver.find_element(By.ID, "tradein-submit").is_enabled(), (
        "'Cotizar' deberia deshabilitarse con el equipo bloqueado"
    )

    # ---------------------------------------------------------------
    # (3) Equipo liberado: la alerta se oculta y el boton se habilita
    # ---------------------------------------------------------------
    driver.find_element(By.CSS_SELECTOR, "input[name='liberado'][value='si']").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "tradein-liberacion-alerta")))
    espera.until(lambda d: d.find_element(By.ID, "tradein-submit").is_enabled())

    # ---------------------------------------------------------------
    # (4) Cotizar con LCD y Mica marcadas
    # ---------------------------------------------------------------
    # Seleccionar el primer equipo (índice 0 = "Selecciona un equipo")
    equipo = Select(driver.find_element(By.ID, "tradein-equipo"))
    equipo.select_by_index(1)

    # Marcar las fallas por su etiqueta visible (LCD y Mica)
    for etiqueta in FALLAS_PRUEBA:
        driver.find_element(
            By.XPATH,
            f"//label[contains(@class,'tradein-check')]"
            f"[span[normalize-space()='{etiqueta}']]/input",
        ).click()

    # Enviar el formulario de cotización
    driver.find_element(By.ID, "tradein-submit").click()

    # Esperar el resultado del fetch a /api/trade-in/cotizar
    espera.until(
        EC.text_to_be_present_in_element(
            (By.ID, "tradein-total-fallas"), str(len(FALLAS_PRUEBA))
        )
    )
    for etiqueta in FALLAS_PRUEBA:
        espera.until(
            EC.presence_of_element_located(
                (By.XPATH, f"//ul[@id='tradein-detalles']//li[contains(., '{etiqueta}')]")
            )
        )

    monto = driver.find_element(By.ID, "tradein-monto").text
    assert re.match(r"^\$\d[\d,]*\.\d{2}$", monto), f"Monto estimado inválido: {monto}"
    precio_base = driver.find_element(By.ID, "tradein-base").text
    deduccion = driver.find_element(By.ID, "tradein-deduccion").text
    assert re.match(r"^\$\d[\d,]*\.\d{2}$", precio_base), f"Precio base inválido: {precio_base}"
    assert re.match(r"^\$\d[\d,]*\.\d{2}$", deduccion), f"Deducción inválida: {deduccion}"

    # Cada falla marcada genera su advertencia inline con el porcentaje aplicado
    mensajes = driver.find_element(By.ID, "tradein-mensajes").text
    assert "Se aplicó" in mensajes, f"El panel de mensajes no muestra las deducciones: '{mensajes}'"
    assert "por LCD." in mensajes, f"Falta la advertencia de LCD: '{mensajes}'"
    assert "por Mica." in mensajes, f"Falta la advertencia de Mica: '{mensajes}'"

    # El finally del JS restaura el texto del boton tras la cotizacion
    espera.until(lambda d: d.find_element(By.ID, "tradein-submit").text.strip() == "Cotizar")

    # --- Feedback global del interceptor de feedback-modal.js (POST /api/...) ---
    _, mensaje = esperar_feedback(
        espera,
        tipo="success",
        titulo="Acción exitosa",
        mensaje="Registro realizado satisfactoriamente.",
    )

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Cotización generada: {monto} | Total fallas: {len(FALLAS_PRUEBA)} "
        f"({', '.join(FALLAS_PRUEBA)}) (feedback: {mensaje})"
    )
