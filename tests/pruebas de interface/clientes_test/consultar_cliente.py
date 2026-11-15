import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_CLIENTES = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/clientes"
TIEMPO_ESPERA = 10

# [cedula, nombre, apellido, celular]
DATOS_CLIENTE = ["65432109", "Cliente", "Prueba", "04141234567"]


def test_consultar_cliente(driver):
    driver.get(URL_CLIENTES)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    fila = espera.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[@id='tabla-clientes']//tr[td[1][normalize-space(.)='{DATOS_CLIENTE[0]}']]",
            )
        )
    )

    nombre = fila.find_element(By.CSS_SELECTOR, "td:nth-child(3)").text
    apellido = fila.find_element(By.CSS_SELECTOR, "td:nth-child(4)").text
    celular = fila.find_element(By.CSS_SELECTOR, "td:nth-child(5)").text
    assert nombre == DATOS_CLIENTE[1]
    assert apellido == DATOS_CLIENTE[2]
    assert celular == DATOS_CLIENTE[3]

    fila.find_element(By.CSS_SELECTOR, "button[data-action='ver']").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-ver-cliente")))

    assert driver.find_element(By.ID, "detalle-cliente-id").text == DATOS_CLIENTE[0]
    assert driver.find_element(By.ID, "detalle-cliente-tipo").text == "Persona Natural"
    assert driver.find_element(By.ID, "detalle-cliente-nombre").text == (
        f"{DATOS_CLIENTE[1]} {DATOS_CLIENTE[2]}"
    )

    driver.find_element(By.CSS_SELECTOR, "#modal-ver-cliente [data-close-modal]").click()
    espera.until(EC.invisibility_of_element_located((By.ID, "modal-ver-cliente")))
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Cliente consultado: {DATOS_CLIENTE[0]} - {nombre} {apellido}")
