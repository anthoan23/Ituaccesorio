import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_ESPECIALIDADES = (
    f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/especialidades"
)
TIEMPO_ESPERA = 10

# [nombre_actual, nombre_nuevo, descripcion_nueva]
DATOS_ESPECIALIDAD = [
    "Especialidad Prueba",
    "Especialidad Editada",
    "Descripcion de especialidad editada",
]


def test_modificar_especialidad(driver):
    driver.get(URL_ESPECIALIDADES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//*[@id='tabla-especialidades']//tr"
                f"[td[2][normalize-space(.)='{DATOS_ESPECIALIDAD[0]}']]",
            )
        )
    )
    fila.find_element(By.CSS_SELECTOR, "button[data-action='editar']").click()

    espera.until(
        EC.visibility_of_element_located((By.ID, "modal-editar-especialidad"))
    )
    nombre = driver.find_element(By.ID, "editar-nombre-especialidad")
    nombre.clear()
    nombre.send_keys(DATOS_ESPECIALIDAD[1])
    descripcion = driver.find_element(By.ID, "editar-descripcion-especialidad")
    descripcion.clear()
    descripcion.send_keys(DATOS_ESPECIALIDAD[2])
    driver.find_element(
        By.CSS_SELECTOR, "#form-editar-especialidad button[type='submit']"
    ).click()

    espera.until(
        EC.invisibility_of_element_located((By.ID, "modal-editar-especialidad"))
    )
    espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//*[@id='tabla-especialidades']//tr"
                f"[td[2][normalize-space(.)='{DATOS_ESPECIALIDAD[1]}']]",
            )
        )
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(
        f"Especialidad modificada: {DATOS_ESPECIALIDAD[0]} -> {DATOS_ESPECIALIDAD[1]}"
    )
