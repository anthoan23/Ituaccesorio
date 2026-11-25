import base64
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

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

    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//tbody[@id='tabla-ordenes-servicio']//tr[@data-id='{id_orden}']",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-accion='tomar-orden']").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    driver.find_element(
        By.XPATH, "//section[contains(@class,'vista-1')]//button[@data-view-target='vista-5']"
    ).click()
    fila_asignada = espera.until(
        EC.presence_of_element_located(
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

    # ---------------------------------------------------------------
    # PASO 3: abrir el modal de fotos y subir la imagen con send_keys
    # (el modal usa un input[type=file] real: #fotos-input)
    # ---------------------------------------------------------------
    driver.find_element(
        By.XPATH,
        "//section[contains(@class,'vista-2')]//button[@data-open-modal='modal-fotos-registrar']",
    ).click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-fotos-registrar")))

    driver.find_element(By.ID, "fotos-input").send_keys(RUTA_FOTO)

    # El JS muestra la previsualizacion y habilita el boton de subida
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#fotos-preview .photo-preview-item")
        )
    )
    espera.until(lambda d: d.find_element(By.ID, "btn-subir-fotos").is_enabled())
    driver.find_element(By.ID, "btn-subir-fotos").click()

    espera.until(EC.invisibility_of_element_located((By.ID, "modal-fotos-registrar")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # --- Verificar la confirmacion: el detalle se recarga y la foto
    # aparece en la seccion de fotos de la vista-2 ---
    espera.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#order-photos .foto-item"))
    )

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Foto subida al taller: {RUTA_FOTO} en la orden {id_orden}")
