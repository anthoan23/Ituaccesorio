import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_CARGOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/cargos"
TIEMPO_ESPERA = 10

# [nombre, descripcion]
DATOS_CARGO = ["Cargo Editado", "Descripcion de cargo editada"]


def test_consultar_cargo(driver):
    driver.get(URL_CARGOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-cargos']//tr[td[2][normalize-space(.)='{DATOS_CARGO[0]}']]",
            )
        )
    )

    nombre = fila.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
    descripcion = fila.find_element(By.CSS_SELECTOR, "td:nth-child(3)").text
    assert nombre == DATOS_CARGO[0]
    assert descripcion == DATOS_CARGO[1]
    print(f"Cargo consultado: {nombre} - {descripcion}")
