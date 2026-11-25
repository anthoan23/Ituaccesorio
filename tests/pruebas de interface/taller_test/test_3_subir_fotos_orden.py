import base64
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_ORDENES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/ordenes-servicio"
URL_TALLER = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/taller"
TIEMPO_ESPERA = 10

# ----------------------------------------------------------------------
# Prueba de interface: subir fotos del dispositivo desde el modulo
# Taller (vista-5 -> detalle -> vista-2 -> boton "Registrar fotos" ->
# modal #modal-fotos-registrar con input[type=file] #fotos-input).
# AUTOCONTENIDA: crea primero su propia orden temporal en
# /ordenes-servicio, la toma en el taller y le sube una foto PNG minima
# generada en runtime con base64 en /tmp/opencode/test_foto_taller.png.
# El registro (foto) queda persistido en la BD (no se elimina).
# NOTAS:
# - taller.js obtiene el id del empleado logueado del localStorage/JWT;
#   en modo prueba no hay login, por lo que se simula con execute_script.
# - La subida usa /api/taller/registrar-fotos, que NO depende de
#   g.user.get("cedula"), por lo que el envio funciona incluso en modo
#   prueba; el acceso a la vista-5 si requiere sesion real (ver nota).
# ----------------------------------------------------------------------

# [imei, modelo_custom, color, capacidad, patron, descripcion]
# El patron "L" se envia como trazo numerico 1-4-7-8-9 porque el campo
# solo acepta numeros del 1 al 9 separados por guiones.
DATOS_ORDEN = [
    "351111111111199",      # IMEI (15 digitos)
    "Modelo Custom Prueba", # modelo personalizado (se deja el select vacio)
    "Negro",                # color
    "128GB",                # capacidad
    "1-4-7-8-9",            # patron en forma de "L"
    "Pantalla rota",        # descripcion del problema
]

# Cliente natural [cedula, nombre, apellido, celular]
DATOS_CLIENTE = ["65432109", "Cliente", "Prueba", "04141234567"]

# PNG de 1x1 pixel minimo (generado en runtime a partir de base64)
FOTO_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
RUTA_FOTO = "/tmp/opencode/test_foto_taller.png"


def test_subir_fotos_taller(driver):
    # ---------------------------------------------------------------
    # PASO 0: generar la imagen PNG minima en runtime
    # ---------------------------------------------------------------
    os.makedirs(os.path.dirname(RUTA_FOTO), exist_ok=True)
    with open(RUTA_FOTO, "wb") as archivo:
        archivo.write(base64.b64decode(FOTO_BASE64))

    # ---------------------------------------------------------------
    # PASO 1: crear la orden temporal
    # ---------------------------------------------------------------
    driver.get(URL_ORDENES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(lambda d: len(Select(d.find_element(By.ID, "orden-modelo")).options) > 1)

    driver.find_element(By.ID, "btn-nueva-orden").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-nueva-orden")))

    driver.find_element(By.ID, "orden-id-equipo").send_keys(DATOS_ORDEN[0])
    driver.find_element(By.ID, "orden-modelo-custom").send_keys(DATOS_ORDEN[1])
    driver.find_element(By.ID, "orden-color").send_keys(DATOS_ORDEN[2])
    Select(driver.find_element(By.ID, "orden-capacidad")).select_by_visible_text(DATOS_ORDEN[3])
    driver.find_element(By.ID, "orden-patron").send_keys(DATOS_ORDEN[4])
    driver.find_element(By.ID, "orden-descripcion").send_keys(DATOS_ORDEN[5])

    driver.find_element(By.ID, "cliente-cedula").send_keys(DATOS_CLIENTE[0])
    driver.find_element(By.ID, "cliente-celular").send_keys(DATOS_CLIENTE[3])
    driver.find_element(By.ID, "cliente-nombre").send_keys(DATOS_CLIENTE[1])
    driver.find_element(By.ID, "cliente-apellido").send_keys(DATOS_CLIENTE[2])

    driver.find_element(By.CSS_SELECTOR, "#form-orden-servicio button[type='submit']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-revision-inicial")))
    driver.find_element(By.ID, "btn-confirmar-revision").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-revision-inicial")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    fila_nueva = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//tbody[@id='tabla-ordenes']/tr[td[4][normalize-space(.)='{DATOS_ORDEN[0]}']][1]",
            )
        )
    )
    id_orden = fila_nueva.find_element(By.CSS_SELECTOR, "td.col-id").text.strip()

    # ---------------------------------------------------------------
    # PASO 2: tomar la orden en el taller y abrir su detalle (vista-2)
    # ---------------------------------------------------------------
    driver.get(URL_TALLER)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    driver.execute_script(
        "window.localStorage.setItem('user', JSON.stringify({id_empleado: '1'}));"
    )

    buscador = driver.find_element(
        By.XPATH,
        "//section[contains(@class,'vista-1')]//input[contains(@class,'table-controls__input')]",
    )
    buscador.send_keys(id_orden)
    fila = espera.until(
        EC.visibility_of_element_located(
            (By.XPATH, f"//tbody[@id='tabla-ordenes-servicio']//tr[@data-id='{id_orden}']")
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-accion='tomar-orden']").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    driver.find_element(
        By.XPATH, "//section[contains(@class,'vista-1')]//button[@data-view-target='vista-5']"
    ).click()
    fila_asignada = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//tbody[@id='tabla-reparaciones-asignadas']//tr[@data-id='{id_orden}']",
            )
        )
    )
    fila_asignada.find_element(By.CSS_SELECTOR, "button[data-accion='ver-detalle']").click()

    espera.until(
        lambda d: d.find_element(By.XPATH, "//section[contains(@class,'vista-2')]").is_displayed()
    )
    espera.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#order-info .detail-group"))
    )

    # --- Verificaciones visuales del detalle (vista-2) ---
    # El JS reescribe el subtitulo de la tarjeta con la orden seleccionada
    subtitulo = driver.find_element(By.ID, "detalle-orden-subtitle")
    assert subtitulo.get_attribute("textContent").strip() == (
        f"Visualizando la información completa de la orden #{id_orden}"
    )
    etiquetas = [
        e.get_attribute("textContent").strip()
        for e in driver.find_elements(By.CSS_SELECTOR, "#order-info .detail-label")
    ]
    assert etiquetas == [
        "ID de la Orden:",
        "Estado:",
        "Cliente:",
        "Modelo:",
        "Descripción:",
        "Nota:",
    ]

    # --- Botones de la seccion de fotos: primario (amarillo), success
    # (verde) y ghost (tema oscuro) ---
    quitar_hover(driver)
    boton_registrar = driver.find_element(
        By.XPATH,
        "//section[contains(@class,'vista-2')]//button[@data-open-modal='modal-fotos-registrar']",
    )
    assert boton_registrar.text.strip() == "Registrar fotos"
    assert "ui-btn--primary" in boton_registrar.get_attribute("class")
    assert estilo_css(driver, boton_registrar, "backgroundColor") == "rgb(243, 197, 0)", (
        "El fondo de 'Registrar fotos' deberia ser amarillo"
    )
    assert estilo_css(driver, boton_registrar, "color") == "rgb(18, 18, 18)", (
        "El texto de 'Registrar fotos' deberia ser oscuro"
    )
    boton_celular = driver.find_element(By.ID, "btn-usar-celular")
    assert boton_celular.text.strip() == "Usar celular"
    assert estilo_css(driver, boton_celular, "color") == "rgb(34, 197, 94)", (
        "El texto de 'Usar celular' deberia ser verde"
    )
    assert estilo_css(driver, boton_celular, "backgroundColor") == "rgba(34, 197, 94, 0.08)", (
        "El fondo de 'Usar celular' deberia ser el success translucido"
    )
    boton_actualizar = driver.find_element(By.ID, "btn-actualizar-fotos")
    assert boton_actualizar.text.strip() == "Actualizar fotos"
    assert "ui-btn--ghost" in boton_actualizar.get_attribute("class")
    assert estilo_css(driver, boton_actualizar, "backgroundColor") == (
        "rgba(255, 255, 255, 0.06)"
    ), "El fondo de 'Actualizar fotos' deberia ser el ghost del tema oscuro"

    # ---------------------------------------------------------------
    # PASO 3: abrir el modal de fotos y subir la imagen con send_keys
    # (el modal usa un input[type=file] real: #fotos-input)
    # ---------------------------------------------------------------
    boton_registrar.click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-fotos-registrar")))
    quitar_hover(driver)

    # --- Modal 'Registrar fotos del dispositivo': titulo, dropzone y boton ---
    assert driver.find_element(By.ID, "modal-fotos-registrar-title").text == (
        "Registrar fotos del dispositivo"
    )
    dropzone = driver.find_element(By.ID, "photo-dropzone")
    assert dropzone.find_element(By.CSS_SELECTOR, ".photo-dropzone__title").text.strip() == (
        "Arrastra o haz clic"
    )
    assert dropzone.find_element(By.CSS_SELECTOR, ".photo-dropzone__subtitle").text.strip() == (
        "Sube fotos del dispositivo (JPG, PNG, WEBP)"
    )
    boton_subir = driver.find_element(By.ID, "btn-subir-fotos")
    assert boton_subir.text.strip() == "Subir fotos"
    # Sin fotos seleccionadas el boton llega deshabilitado desde la vista
    assert boton_subir.get_attribute("disabled") == "true", (
        "'Subir fotos' deberia llegar deshabilitado sin fotos seleccionadas"
    )

    driver.find_element(By.ID, "fotos-input").send_keys(RUTA_FOTO)

    # El JS muestra la previsualizacion y habilita el boton de subida
    espera.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#fotos-preview .photo-preview-item"))
    )
    espera.until(lambda d: d.find_element(By.ID, "btn-subir-fotos").is_enabled())
    boton_subir.click()

    # --- Feedback global de exito: feedback-modal.js intercepta el POST y
    # muestra primero el exito generico; taller.js sobreescribe el mismo
    # modal con titulo 'Aviso' y el mensaje del servidor (que incluye la
    # cantidad: "1 fotos subidas y registradas exitosamente") ---
    _, mensaje = esperar_feedback(
        espera,
        tipo="success",
        titulo="Aviso",
        mensaje="fotos subidas y registradas exitosamente",
    )

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-fotos-registrar")))

    # --- Verificar la confirmacion: el detalle se recarga y la foto
    # aparece en la seccion de fotos de la vista-2 ---
    espera.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#order-photos .foto-item"))
    )

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Foto subida al taller: {RUTA_FOTO} en la orden {id_orden} (feedback: {mensaje})")
