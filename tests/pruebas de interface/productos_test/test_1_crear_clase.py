import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import estilo_css, quitar_hover

URL_PRODUCTOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/productos"
TIEMPO_ESPERA = 10

# Nombre de la clase de producto que se va a crear (queda registrada en la BD)
NOMBRE_CLASE = "Clase Interfaz"


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


def test_crear_clase(driver):
    driver.get(URL_PRODUCTOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # La tabla se llena por JS: esperar una fila real
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-productos tr[data-id]")))

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == "Ituaccesorio - Productos"
    assert espera.until(
        lambda d: d.find_element(By.CSS_SELECTOR, ".hero__title").text
    ) == "Productos"
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Productos"
    # textContent (texto del DOM), porque el CSS renderiza los th en mayusculas
    encabezados = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, ".products-table thead th")
    ]
    assert encabezados == ["Imagen", "Producto / Código", "Marca", "Clase", "Acciones"]
    # Esta tabla usa su propio paginador (PAGE_SIZE 10) y no buscador de texto
    assert driver.find_element(By.ID, "pager-anterior").text.strip() == "‹ Anterior"
    assert driver.find_element(By.ID, "pager-siguiente").text.strip() == "Siguiente ›"

    # --- Botones del heroe: 'Registrar producto' primario y 'Reportes' ghost ---
    boton_registrar = driver.find_element(By.ID, "btn-registrar-producto")
    assert boton_registrar.text.strip() == "Registrar producto"
    assert estilo_css(driver, boton_registrar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Registrar producto' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_registrar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Registrar producto' deberia ser oscuro"
    )
    boton_reportes = driver.find_element(By.ID, "btn-reportes")
    assert boton_reportes.text.strip() == "Reportes"
    assert estilo_css(driver, boton_reportes, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Reportes' deberia ser el ghost del tema oscuro"

    # --- El formulario de clases vive dentro del modal 'Registrar producto' ---
    boton_registrar.click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-producto")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-producto-title").text == "Registrar producto"

    boton_nueva_clase = driver.find_element(By.ID, "btn-nueva-clase")
    assert boton_nueva_clase.text.strip() == "Nueva clase"
    boton_nueva_clase.click()
    espera.until(EC.visibility_of_element_located((By.ID, "p-clase-nueva-wrap")))
    # El boton alterna a 'Cancelar' mientras el campo de nueva clase esta abierto
    assert boton_nueva_clase.text.strip() == "Cancelar"

    boton_guardar_clase = driver.find_element(By.ID, "btn-guardar-clase")
    assert boton_guardar_clase.text.strip() == "Guardar clase"
    assert estilo_css(driver, boton_guardar_clase, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Guardar clase' deberia ser amarillo"
    )

    driver.find_element(By.ID, "p-clase-nueva").send_keys(NOMBRE_CLASE)
    # Guardar la clase (POST /api/productos/clases)
    boton_guardar_clase.click()

    # El JS recarga el select y deja la clase nueva seleccionada
    espera.until(
        lambda navegador: (
            Select(navegador.find_element(By.ID, "p-clase"))
            .first_selected_option.text
            == NOMBRE_CLASE
        )
        or False
    )
    assert (
        Select(driver.find_element(By.ID, "p-clase")).first_selected_option.text
        == NOMBRE_CLASE
    )

    # --- Feedback global de exito con el mensaje definitivo del JS ---
    _, mensaje = esperar_feedback_exito(
        espera, f'Clase "{NOMBRE_CLASE}" creada correctamente.'
    )

    # El campo de nueva clase se cierra y el boton vuelve a 'Nueva clase'
    espera.until(EC.invisibility_of_element_located((By.ID, "p-clase-nueva-wrap")))
    assert boton_nueva_clase.text.strip() == "Nueva clase"
    print(f"Clase creada: {NOMBRE_CLASE} (feedback: {mensaje})")
