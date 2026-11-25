import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from helpers import estilo_css, quitar_hover

URL_PRODUCTOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/productos"
TIEMPO_ESPERA = 10

# Nombre de la marca de producto que se va a crear (queda registrada en la BD)
NOMBRE_MARCA = "Marca Interfaz"


def esperar_feedback_exito(espera, mensaje):
    """FeedbackModal global. OJO: el interceptor de feedback-modal.js muestra
    primero su modal generico (titulo 'Acción exitosa') al resolver el POST;
    productos.js lo sobreescribe con titulo 'Éxito' y su mensaje definitivo
    despues de recargar los selects. Esta espera solo acepta el mensaje
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


def test_crear_marca(driver):
    driver.get(URL_PRODUCTOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # La tabla se llena por JS: esperar una fila real
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-productos tr[data-id]")))

    assert driver.title == "Ituaccesorio - Productos"

    # --- El formulario de marcas vive dentro del modal 'Registrar producto' ---
    driver.find_element(By.ID, "btn-registrar-producto").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-producto")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-producto-title").text == "Registrar producto"

    boton_nueva_marca = driver.find_element(By.ID, "btn-nueva-marca")
    assert boton_nueva_marca.text.strip() == "Nueva marca"
    boton_nueva_marca.click()
    espera.until(EC.visibility_of_element_located((By.ID, "p-marca-nueva-wrap")))
    # El boton alterna a 'Cancelar' mientras el campo de nueva marca esta abierto
    assert boton_nueva_marca.text.strip() == "Cancelar"

    boton_guardar_marca = driver.find_element(By.ID, "btn-guardar-marca")
    assert boton_guardar_marca.text.strip() == "Guardar marca"
    assert estilo_css(driver, boton_guardar_marca, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Guardar marca' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_guardar_marca, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Guardar marca' deberia ser oscuro"
    )

    driver.find_element(By.ID, "p-marca-nueva").send_keys(NOMBRE_MARCA)
    # Guardar la marca (POST /api/productos/marcas)
    boton_guardar_marca.click()

    # El JS recarga el select y deja la marca nueva seleccionada
    espera.until(
        lambda navegador: (
            Select(navegador.find_element(By.ID, "p-marca"))
            .first_selected_option.text
            == NOMBRE_MARCA
        )
        or False
    )

    # --- Feedback global de exito con el mensaje definitivo del JS ---
    _, mensaje = esperar_feedback_exito(
        espera, f'Marca "{NOMBRE_MARCA}" creada correctamente.'
    )

    # El campo de nueva marca se cierra y el boton vuelve a 'Nueva marca'
    espera.until(EC.invisibility_of_element_located((By.ID, "p-marca-nueva-wrap")))
    assert boton_nueva_marca.text.strip() == "Nueva marca"
    print(f"Marca creada: {NOMBRE_MARCA} (feedback: {mensaje})")
