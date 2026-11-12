import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_ESPECIALIDADES = (
    f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/especialidades"
)
TIEMPO_ESPERA = 10

# [nombre]
DATOS_ESPECIALIDAD = ["Especialidad Editada"]


def test_eliminar_especialidad(driver):
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
    fila.find_element(By.CSS_SELECTOR, "button[data-action='eliminar']").click()

    espera.until(
        EC.visibility_of_element_located((By.ID, "modal-eliminar-especialidad"))
    )
    driver.find_element(By.ID, "btn-confirmar-eliminar-especialidad").click()

    espera.until(
        EC.invisibility_of_element_located((By.ID, "modal-eliminar-especialidad"))
    )
    espera.until(
        EC.invisibility_of_element_located(
            (
                By.XPATH,
                "//*[@id='tabla-especialidades']//tr"
                f"[td[2][normalize-space(.)='{DATOS_ESPECIALIDAD[0]}']]",
            )
        )
    )
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Especialidad eliminada: {DATOS_ESPECIALIDAD[0]}")
