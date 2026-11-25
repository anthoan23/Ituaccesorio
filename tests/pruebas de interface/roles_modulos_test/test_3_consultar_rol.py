import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# [nombre, descripcion] - el registro que la cadena crea/modifica y luego elimina
DATOS_ROL = ["Rol Editado", "Descripcion del rol editada"]


def test_consultar_rol(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Los roles viven en la pestaña "Roles" de la vista de usuarios
    driver.find_element(By.ID, "tab-roles").click()

    # Filtrar por nombre para que la fila quede visible
    buscador = driver.find_element(By.CSS_SELECTOR, "#tab-panel-roles .table-controls__input")
    buscador.send_keys(DATOS_ROL[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-roles']//tr[td[1][normalize-space(.)='{DATOS_ROL[0]}']]",
            )
        )
    )

    # La fila debe mostrar exactamente los datos registrados
    nombre = fila.find_element(By.CSS_SELECTOR, "td:nth-child(1)").text
    descripcion = fila.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
    assert nombre == DATOS_ROL[0]
    assert descripcion == DATOS_ROL[1]

    # El rol de prueba no es admin/cliente, asi que SI tiene boton eliminar
    assert fila.find_elements(By.CSS_SELECTOR, "button[data-action='delete-rol']"), (
        "El rol de prueba deberia exponer el boton eliminar (no esta protegido)"
    )
    print(f"Rol consultado: {nombre} - {descripcion}")
