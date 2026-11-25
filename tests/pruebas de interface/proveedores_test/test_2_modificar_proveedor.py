import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

URL_PROVEEDORES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/proveedores"
TIEMPO_ESPERA = 10

# [nombre_actual, nombre_nuevo] - el proveedor que creo test_1_crear_proveedor
DATOS_PROVEEDOR = ["Proveedor Interfaz", "Proveedor Interfaz Editado"]


def esperar_feedback_exito(espera, mensaje):
    """FeedbackModal global. OJO: el interceptor de feedback-modal.js muestra
    primero su modal generico (titulo 'Acción exitosa') al resolver el PUT;
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


def test_modificar_proveedor(driver):
    driver.get(URL_PROVEEDORES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Filtrar por nombre para que la fila quede visible y clickeable
    buscador = driver.find_element(
        By.CSS_SELECTOR, ".proveedores-grid .table-controls__input"
    )
    buscador.send_keys(DATOS_PROVEEDOR[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-proveedores']//tr[td[3][normalize-space(.)='{DATOS_PROVEEDOR[0]}']]",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='editar']").click()

    # --- Modal 'Modificar proveedor': titulo y campos precargados por el JS ---
    espera.until(EC.visibility_of_element_located((By.ID, "modal-proveedor-editar")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-proveedor-editar-title").text == (
        "Modificar proveedor"
    )
    espera.until(
        lambda navegador: navegador.find_element(By.ID, "e-nombre").get_attribute(
            "value"
        )
        == DATOS_PROVEEDOR[0]
    )
    rif = driver.find_element(By.ID, "e-rif")
    assert rif.get_attribute("value") != "", "El RIF deberia venir precargado"

    # --- Boton 'Guardar cambios': fondo amarillo con texto oscuro ---
    boton_guardar = driver.find_element(
        By.CSS_SELECTOR, "#form-proveedor-editar button[type='submit']"
    )
    assert boton_guardar.text.strip() == "Guardar cambios"
    assert estilo_css(driver, boton_guardar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Guardar cambios' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_guardar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Guardar cambios' deberia ser oscuro"
    )

    nombre = driver.find_element(By.ID, "e-nombre")
    nombre.clear()
    nombre.send_keys(DATOS_PROVEEDOR[1])
    boton_guardar.click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-proveedor-editar")))

    # --- Feedback global de exito con el mensaje definitivo del JS ---
    _, mensaje = esperar_feedback_exito(espera, "Proveedor actualizado correctamente.")

    # La tabla se re-renderiza: refrescar el filtro para ver la fila editada
    buscador.clear()
    buscador.send_keys(DATOS_PROVEEDOR[1])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-proveedores']//tr[td[3][normalize-space(.)='{DATOS_PROVEEDOR[1]}']]",
            )
        )
    )
    assert DATOS_PROVEEDOR[1] in fila.text
    print(
        f"Proveedor modificado: {DATOS_PROVEEDOR[0]} -> {DATOS_PROVEEDOR[1]} "
        f"(feedback: {mensaje})"
    )
