import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from helpers import estilo_css, esperar_feedback, quitar_hover

URL_ORDENES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/ordenes-servicio"
URL_TALLER = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/taller"
TIEMPO_ESPERA = 10

# ----------------------------------------------------------------------
# Prueba de interface: liberar una orden asignada desde el modulo
# Taller (vista-5 "Reparaciones asignadas", boton "Liberar orden" de la
# fila). El SP sp_liberar_orden_servicio mueve la orden de "Asignada" a
# "En proceso", por lo que deja de listarse en reparaciones asignadas y
# vuelve a la tabla de ordenes del taller con el nuevo estado.
# AUTOCONTENIDA: crea primero su propia orden temporal en
# /ordenes-servicio, la toma en el taller y luego la libera. El registro
# queda persistido en la BD (no se elimina al terminar).
# NOTAS:
# - taller.js obtiene el id del empleado logueado del localStorage/JWT;
#   en modo prueba no hay login, por lo que se simula con execute_script.
# - Los endpoints /api/taller/asignar-orden, liberar-orden y
#   reparaciones-asignadas usan g.user.get("cedula"), incompatible con
#   el usuario SimpleNamespace de ENTORNO_PRUEBA (fallan con 500); la
#   prueba sigue el flujo real de la UI y requiere sesion real (JWT).
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


def test_liberar_orden_taller(driver):
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
    # PASO 2: tomar la orden en el taller para que quede asignada
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

    # La orden asignada aparece en la vista "Reparaciones asignadas"
    driver.find_element(
        By.XPATH, "//section[contains(@class,'vista-1')]//button[@data-view-target='vista-5']"
    ).click()
    assert driver.find_element(By.ID, "breadcrumb-section").text == "Reparaciones asignadas"

    # Encabezados de la tabla de asignadas (textContent por el text-transform)
    encabezados = [
        th.get_attribute("textContent").strip()
        for th in driver.find_elements(By.CSS_SELECTOR, ".vista-5 .table thead th")
    ]
    assert encabezados == ["ID orden", "Modelo", "Fecha ingreso", "Acciones"]

    fila_asignada = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//tbody[@id='tabla-reparaciones-asignadas']//tr[@data-id='{id_orden}']",
            )
        )
    )

    # --- Iconos de la fila asignada: ver detalle (verde) y liberar (rojo) ---
    quitar_hover(driver)
    boton_ver = fila_asignada.find_element(By.CSS_SELECTOR, "button[data-accion='ver-detalle']")
    boton_liberar = fila_asignada.find_element(
        By.CSS_SELECTOR, "button[data-accion='liberar-orden']"
    )
    assert estilo_css(driver, boton_ver.find_element(By.TAG_NAME, "svg"), "color") == (
        "rgb(34, 197, 94)"
    ), "El icono de 'Ver detalle' deberia ser verde"
    assert estilo_css(driver, boton_liberar, "borderTopColor") == "rgb(220, 38, 38)", (
        "El borde de 'Liberar orden' deberia ser rojo"
    )
    assert estilo_css(driver, boton_liberar.find_element(By.TAG_NAME, "svg"), "color") == (
        "rgb(220, 38, 38)"
    ), "El icono de 'Liberar orden' deberia ser rojo"

    # ---------------------------------------------------------------
    # PASO 3: liberar la orden asignada
    # ---------------------------------------------------------------
    boton_liberar.click()

    # --- Feedback global de exito: taller.js no muestra mensaje propio al
    # liberar; el interceptor de feedback-modal.js muestra el modal
    # generico de exito para el POST a /api/taller/liberar-orden ---
    _, mensaje = esperar_feedback(
        espera,
        tipo="success",
        titulo="Acción exitosa",
        mensaje="Registro realizado satisfactoriamente.",
    )

    # --- Verificar la confirmacion: la orden deja de estar asignada y
    # vuelve a la tabla de ordenes del taller con estado "En proceso" ---
    espera.until(
        EC.invisibility_of_element_located(
            (
                By.XPATH,
                f"//tbody[@id='tabla-reparaciones-asignadas']//tr[@data-id='{id_orden}']",
            )
        )
    )
    fila_liberada = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//tbody[@id='tabla-ordenes-servicio']//tr"
                f"[@data-id='{id_orden}' and td[2]//span[normalize-space(.)='En proceso']]",
            )
        )
    )
    estado = fila_liberada.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text.strip()
    assert estado == "En proceso"

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Orden liberada en el taller: {id_orden} -> estado '{estado}' (feedback: {mensaje})")
