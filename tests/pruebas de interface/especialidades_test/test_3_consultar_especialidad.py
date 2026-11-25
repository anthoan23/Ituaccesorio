import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_ESPECIALIDADES = (
    f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/especialidades"
)
TIEMPO_ESPERA = 10

# [nombre, descripcion] - el registro que la cadena modifica
DATOS_ESPECIALIDAD = [
    "Especialidad Interfaz Editada",
    "Descripcion de especialidad editada",
]


def test_consultar_especialidad(driver):
    driver.get(URL_ESPECIALIDADES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # Filtrar por nombre para que la fila quede visible
    buscador = driver.find_element(
        By.CSS_SELECTOR, ".especialidades-table-card .table-controls__input"
    )
    buscador.send_keys(DATOS_ESPECIALIDAD[0])
    fila = espera.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//*[@id='tabla-especialidades']//tr"
                f"[td[2][normalize-space(.)='{DATOS_ESPECIALIDAD[0]}']]",
            )
        )
    )

    # La fila debe mostrar exactamente los datos registrados
    nombre = fila.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
    descripcion = fila.find_element(By.CSS_SELECTOR, "td:nth-child(3)").text
    assert nombre == DATOS_ESPECIALIDAD[0]
    assert descripcion == DATOS_ESPECIALIDAD[1]
    print(f"Especialidad consultada: {nombre} - {descripcion}")
