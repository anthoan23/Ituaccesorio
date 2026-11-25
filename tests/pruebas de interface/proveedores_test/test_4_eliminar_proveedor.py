import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

URL_PROVEEDORES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/proveedores"
TIEMPO_ESPERA = 10

# Nombre del proveedor que la cadena creo/modifico y aqui elimina
NOMBRE_PROVEEDOR = "Proveedor Interfaz Editado"


def esperar_feedback_exito(espera, mensaje):
    """FeedbackModal global. OJO: el interceptor de feedback-modal.js muestra
    primero su modal generico (titulo 'Acción exitosa') al resolver el DELETE;
    proveedores.js lo sobreescribe con titulo 'Éxito' y su mensaje definitivo
    despues de recargar la tabla. Esta espera solo acepta el mensaje
    definitivo y luego espera el autocierre del modal."""
    def mensaje_definitivo(navegador):
        modal = navegador.find_element(By.ID, "feedback-modal")
        if modal.get_attribute("hidden"):
            return False
        titulo = navegador.find_element(By.ID, "feedback-modal-title").text.strip()
        texto = navegador.find_element(By.ID, "feedback-modal-message").text.strip()
        return (titulo, texto) if titulo == "Éxito" and mensaje in texto else False

    titulo, texto = espera.until(mensaje_definitivo)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    return titulo, texto


def test_eliminar_proveedor(driver):
    driver.get(URL_PROVEEDORES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Filtrar por nombre para que la fila quede visible y clickeable
    buscador = driver.find_element(
        By.CSS_SELECTOR, ".proveedores-grid .table-controls__input"
    )
    buscador.send_keys(NOMBRE_PROVEEDOR)
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-proveedores']//tr[td[3][normalize-space(.)='{NOMBRE_PROVEEDOR}']]",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']").click()

    # --- Modal de confirmacion creado por el JS (consulta productos asociados) ---
    espera.until(
        EC.visibility_of_element_located((By.ID, "confirmacion-modal-proveedores"))
    )
    quitar_hover(driver)
    assert driver.find_element(
        By.CSS_SELECTOR, "#confirmacion-modal-proveedores .ui-modal__title"
    ).text == "Confirmar acción"
    mensaje = driver.find_element(
        By.CSS_SELECTOR, "#confirmacion-modal-proveedores .confirm-modal__message"
    ).text.strip()
    assert mensaje == (
        f'¿Seguro que deseas eliminar el proveedor "{NOMBRE_PROVEEDOR}"? '
        "Esta acción no se puede deshacer."
    ), f"El texto de confirmacion no menciona al proveedor: '{mensaje}'"

    # --- Boton 'Eliminar': estilo peligro (texto y fondo rojo tenue) ---
    boton_confirmar = driver.find_element(By.ID, "btn-confirmar-accion-proveedores")
    assert boton_confirmar.text.strip() == "Eliminar"
    assert "ui-btn--danger" in boton_confirmar.get_attribute("class")
    assert estilo_css(driver, boton_confirmar, "color") == "rgb(239, 68, 68)", (
        "El texto de 'Eliminar' deberia ser el rojo de peligro del tema"
    )
    assert estilo_css(driver, boton_confirmar, "backgroundColor") == (
        "rgba(220, 38, 38, 0.2)"
    ), "El fondo de 'Eliminar' deberia ser rojo tenue"

    boton_cancelar = driver.find_element(By.ID, "btn-cancelar-confirmacion-proveedores")
    assert boton_cancelar.text.strip() == "Cancelar"
    assert "ui-btn--ghost" in boton_cancelar.get_attribute("class")
    assert estilo_css(driver, boton_cancelar, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Cancelar' deberia ser el ghost del tema oscuro"

    boton_confirmar.click()

    espera.until(
        EC.invisibility_of_element_located((By.ID, "confirmacion-modal-proveedores"))
    )

    # --- Feedback global de exito: menciona el nombre del proveedor ---
    _, mensaje_feedback = esperar_feedback_exito(
        espera, f'Proveedor "{NOMBRE_PROVEEDOR}" eliminado correctamente.'
    )

    espera.until(EC.invisibility_of_element_located((By.XPATH, (
        f"//*[@id='tabla-proveedores']//tr[td[3][normalize-space(.)='{NOMBRE_PROVEEDOR}']"
    ))))
    print(f"Proveedor eliminado: {NOMBRE_PROVEEDOR} (feedback: {mensaje_feedback})")
