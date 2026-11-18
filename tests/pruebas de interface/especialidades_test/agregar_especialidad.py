import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_ESPECIALIDADES = (
    f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/especialidades"
)
TIEMPO_ESPERA = 10

# [nombre, descripcion]
DATOS_ESPECIALIDAD = [
    "Especialidad Prueba",
    "Descripcion de especialidad de prueba",
]


def test_crear_especialidad(driver):
    driver.get(URL_ESPECIALIDADES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    espera.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#tabla-especialidades tr[data-id]")
        )
    )

    driver.find_element(
        By.CSS_SELECTOR, "#form-especialidad input[name='nombre_especialidad']"
    ).send_keys(DATOS_ESPECIALIDAD[0])
    driver.find_element(
        By.CSS_SELECTOR, "#form-especialidad textarea[name='descripcion_especialidad']"
    ).send_keys(DATOS_ESPECIALIDAD[1])
    driver.find_element(
        By.CSS_SELECTOR, "#form-especialidad button[type='submit']"
    ).click()

    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//*[@id='tabla-especialidades']//tr"
                f"[td[2][normalize-space(.)='{DATOS_ESPECIALIDAD[0]}']]",
            )
        )
    )
    assert DATOS_ESPECIALIDAD[1] in fila.text
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Especialidad creada: {DATOS_ESPECIALIDAD[0]}")
