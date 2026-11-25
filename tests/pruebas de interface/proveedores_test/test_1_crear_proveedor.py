import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from helpers import estilo_css, quitar_hover

URL_PROVEEDORES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/proveedores"
TIEMPO_ESPERA = 10

# [rif, nombre, tipo, prefijo, sufijo, correo, limite_credito, direccion]
# La cadena CRUD crea/modifica/consulta/elimina este registro.
DATOS_PROVEEDOR = [
    "J-80076543-2",
    "Proveedor Interfaz",
    "Nacional",
    "0414",
    "7654321",
    "proveedor.interfaz@ituaccesorio.com",
    "1500",
    "Barquisimeto",
]


def esperar_feedback_exito(espera, mensaje):
    """FeedbackModal global. OJO: el interceptor de feedback-modal.js muestra
    primero su modal generico (titulo 'Acción exitosa') al resolver el POST;
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


def test_crear_proveedor(driver):
    driver.get(URL_PROVEEDORES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    # La tabla se llena por JS: esperar una fila real (con chip de RIF)
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-proveedores tr .chip")))

    # --- Verificaciones visuales de la pagina ---
    assert driver.title == "Ituaccesorio - Proveedores"
    assert espera.until(
        lambda d: d.find_element(By.CSS_SELECTOR, ".hero__title").text
    ) == "Proveedores"
    assert driver.find_element(By.CSS_SELECTOR, ".breadcrumb__current").text == "Proveedores"
    # textContent (texto del DOM), porque el CSS renderiza los th en mayusculas
    encabezados = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, ".table thead th")
    ]
    assert encabezados == ["RIF", "ID", "Proveedor", "Tipo", "Teléfono", "Dirección", "Acciones"]

    # --- Botones del heroe: 'Registrar proveedor' primario y 'Reportes' ghost ---
    boton_registrar = driver.find_element(
        By.CSS_SELECTOR, "[data-open-modal='modal-proveedor-crear']"
    )
    assert boton_registrar.text.strip() == "Registrar proveedor"
    assert estilo_css(driver, boton_registrar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Registrar proveedor' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_registrar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Registrar proveedor' deberia ser oscuro"
    )
    boton_reportes = driver.find_element(By.ID, "btn-reportes")
    assert boton_reportes.text.strip() == "Reportes"
    assert estilo_css(driver, boton_reportes, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Reportes' deberia ser el ghost del tema oscuro"

    # --- Modal 'Registrar proveedor': titulo, labels y acciones ---
    boton_registrar.click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-proveedor-crear")))
    quitar_hover(driver)
    assert driver.find_element(By.ID, "modal-proveedor-crear-title").text == (
        "Registrar proveedor"
    )
    labels = [
        span.get_attribute("textContent").strip()
        for span in driver.find_elements(
            By.CSS_SELECTOR, "#form-proveedor-crear label.field > span"
        )
    ]
    assert labels == [
        "RIF del proveedor", "Proveedor *", "Tipo", "Teléfono",
        "Correo", "Límite de crédito", "Dirección",
    ]

    boton_guardar = driver.find_element(
        By.CSS_SELECTOR, "#form-proveedor-crear button[type='submit']"
    )
    assert boton_guardar.text.strip() == "Guardar"
    assert estilo_css(driver, boton_guardar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Guardar' deberia ser amarillo"
    )
    boton_cancelar = driver.find_element(
        By.CSS_SELECTOR, "#form-proveedor-crear [data-close-modal]"
    )
    assert boton_cancelar.text.strip() == "Cancelar"
    assert "ui-btn--ghost" in boton_cancelar.get_attribute("class")

    driver.find_element(By.ID, "c-id").send_keys(DATOS_PROVEEDOR[0])
    driver.find_element(By.ID, "c-nombre").send_keys(DATOS_PROVEEDOR[1])
    Select(driver.find_element(By.ID, "c-tipo")).select_by_visible_text(
        DATOS_PROVEEDOR[2]
    )
    Select(driver.find_element(By.ID, "c-celular-prefijo")).select_by_visible_text(
        DATOS_PROVEEDOR[3]
    )
    driver.find_element(By.ID, "c-celular-sufijo").send_keys(DATOS_PROVEEDOR[4])
    driver.find_element(By.ID, "c-correo").send_keys(DATOS_PROVEEDOR[5])
    driver.find_element(By.ID, "c-limite").send_keys(DATOS_PROVEEDOR[6])
    driver.find_element(By.ID, "c-direccion").send_keys(DATOS_PROVEEDOR[7])
    boton_guardar.click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-proveedor-crear")))

    # --- Feedback global de exito con el mensaje definitivo del JS ---
    _, mensaje = esperar_feedback_exito(espera, "Proveedor creado correctamente.")

    # --- Fila creada: filtrar con el buscador de la tabla para dejarla visible ---
    buscador = driver.find_element(
        By.CSS_SELECTOR, ".proveedores-grid .table-controls__input"
    )
    buscador.send_keys(DATOS_PROVEEDOR[1])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-proveedores']//tr[td[3][normalize-space(.)='{DATOS_PROVEEDOR[1]}']]",
            )
        )
    )
    assert DATOS_PROVEEDOR[0] in fila.text
    assert fila.find_element(
        By.CSS_SELECTOR, "td:nth-child(4)"
    ).get_attribute("textContent").strip() == DATOS_PROVEEDOR[2]
    assert fila.find_element(
        By.CSS_SELECTOR, "td:nth-child(5)"
    ).get_attribute("textContent").strip() == (
        f"{DATOS_PROVEEDOR[3]}{DATOS_PROVEEDOR[4]}"
    )

    # --- Botones de accion de la fila: orden y colores (ver, editar, eliminar) ---
    boton_ver = fila.find_element(By.CSS_SELECTOR, "button[data-action='ver']")
    boton_editar = fila.find_element(By.CSS_SELECTOR, "button[data-action='editar']")
    boton_eliminar = fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']")
    assert boton_ver.get_attribute("aria-label") == "Ver"
    assert boton_editar.get_attribute("aria-label") == "Modificar"
    assert boton_eliminar.get_attribute("aria-label") == "Eliminar"
    assert estilo_css(driver, boton_ver, "borderTopColor") == "rgb(0, 122, 255)", (
        "El borde de ver deberia ser azul"
    )
    assert estilo_css(driver, boton_editar, "borderTopColor") == "rgb(243, 197, 0)", (
        "El borde de editar deberia ser amarillo"
    )
    assert estilo_css(driver, boton_eliminar, "borderTopColor") == "rgb(220, 38, 38)", (
        "El borde de eliminar deberia ser rojo"
    )
    print(f"Proveedor creado: {DATOS_PROVEEDOR[1]} (feedback: {mensaje})")
