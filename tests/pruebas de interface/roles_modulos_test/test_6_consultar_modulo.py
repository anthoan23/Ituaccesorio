import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# [nombre, descripcion] - el registro que la cadena crea/modifica y luego elimina
DATOS_MODULO = ["ModuloEditado", "Descripcion del modulo editada"]


def test_consultar_modulo(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Los módulos viven en la pestaña "Módulos" de la vista de usuarios
    driver.find_element(By.ID, "tab-modulos").click()

    # Filtrar por nombre para que la fila quede visible
    buscador = driver.find_element(By.CSS_SELECTOR, "#tab-panel-modulos .table-controls__input")
    buscador.send_keys(DATOS_MODULO[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-modulos']//tr[td[1][normalize-space(.)='{DATOS_MODULO[0]}']]",
            )
        )
    )

    # La fila debe mostrar exactamente los datos registrados
    nombre = fila.find_element(By.CSS_SELECTOR, "td:nth-child(1)").text
    descripcion = fila.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
    assert nombre == DATOS_MODULO[0]
    assert descripcion == DATOS_MODULO[1]
    print(f"Modulo consultado: {nombre} - {descripcion}")
