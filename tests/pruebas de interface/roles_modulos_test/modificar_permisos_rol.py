import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# Rol al que se le editan los permisos (creado y modificado en las pruebas anteriores)
ROL_OBJETIVO = "Rol Editado"
MENSAJE_EXITO = "Permisos actualizados correctamente"


def test_modificar_permisos_rol(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabla-usuarios tr")))

    # El editor de permisos vive dentro del modal de usuarios
    driver.find_element(By.ID, "btn-admin-usuarios").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-admin-usuarios")))

    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#form-usuario select[name='rol_id'] option:nth-child(2)")
        )
    )
    Select(driver.find_element(By.CSS_SELECTOR, "#form-usuario select[name='rol_id']")).select_by_visible_text(ROL_OBJETIVO)

    # La tabla de permisos por modulo se llena de forma asincrona
    casilla = espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#permisos-grid .permiso-item input[data-permiso='registrar']")
        )
    )
    estado_original = casilla.is_selected()
    casilla.click()  # marca o desmarca el permiso "Registrar" del primer modulo listado
    estado_esperado = not estado_original

    driver.find_element(By.ID, "btn-guardar-permisos").click()

    # El toast confirma el guardado y la tabla de permisos se vuelve a pintar
    espera.until(EC.text_to_be_present_in_element((By.ID, "toast"), MENSAJE_EXITO))
    espera.until(EC.staleness_of(casilla))
    casilla_nueva = driver.find_element(
        By.CSS_SELECTOR, "#permisos-grid .permiso-item input[data-permiso='registrar']"
    )
    assert casilla_nueva.is_selected() == estado_esperado
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Permisos del rol '{ROL_OBJETIVO}' actualizados (Registrar del primer modulo)")
