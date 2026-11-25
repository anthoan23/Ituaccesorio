import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_USUARIOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/usuarios"
TIEMPO_ESPERA = 10

# [nombre, descripcion]
DATOS_ROL = ["Rol Prueba", "Rol de prueba de interface"]


def test_consultar_rol(driver):
    driver.get(URL_USUARIOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    driver.find_element(By.ID, "tab-roles").click()
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-roles']//tr[td[1][normalize-space(.)='{DATOS_ROL[0]}']]",
            )
        )
    )

    nombre = fila.find_element(By.CSS_SELECTOR, "td:nth-child(1)").text
    descripcion = fila.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
    assert nombre == DATOS_ROL[0]
    assert descripcion == DATOS_ROL[1]
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Rol consultado: {nombre} - {descripcion}")
