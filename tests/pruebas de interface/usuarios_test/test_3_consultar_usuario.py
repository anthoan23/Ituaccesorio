import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# [nombre] - el usuario que la cadena creo y modifico en los tests anteriores
DATOS_USUARIO = ["Usuario Interfaz Editado"]


def test_consultar_usuario(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Filtrar por nombre para que la fila quede visible
    buscador = driver.find_element(
        By.CSS_SELECTOR, "#tab-panel-usuarios .table-controls__input"
    )
    buscador.send_keys(DATOS_USUARIO[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-usuarios']//tr[td[2][normalize-space(.)='{DATOS_USUARIO[0]}']]",
            )
        )
    )

    # La tabla de usuarios no tiene boton de detalle; se consultan los datos
    # directamente de la fila (la columna 1 lleva el chip con el ID)
    nombre = fila.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
    cedula = fila.find_element(By.CSS_SELECTOR, "td:nth-child(3)").text
    rol = fila.find_element(By.CSS_SELECTOR, "td:nth-child(4)").text
    id_chip = fila.find_element(By.CSS_SELECTOR, "td:nth-child(1) .chip").text

    assert nombre == DATOS_USUARIO[0]
    assert id_chip.strip() != "", "La fila deberia mostrar el ID del usuario"
    assert cedula.strip() != "", "La cedula del usuario llego vacia"
    assert rol.strip() != "", "El rol del usuario llego vacio"

    # La fila solo ofrece editar y eliminar (no existe boton de 'ver')
    assert fila.find_elements(By.CSS_SELECTOR, "button[data-action='edit-usuario']")
    assert fila.find_elements(By.CSS_SELECTOR, "button[data-action='delete-usuario']")
    assert not fila.find_elements(By.CSS_SELECTOR, "button[data-action='ver']")
    print(f"Usuario consultado: {nombre} - cedula {cedula} - rol {rol} - id {id_chip}")
