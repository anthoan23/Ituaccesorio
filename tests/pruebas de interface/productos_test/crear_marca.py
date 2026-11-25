import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

URL_PRODUCTOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5001').rstrip('/')}/productos"
TIEMPO_ESPERA = 10

# Nombre de la marca de producto que se va a crear
NOMBRE_MARCA = "Marca Prueba"


def test_crear_marca(driver):
    driver.get(URL_PRODUCTOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # El formulario de marcas vive dentro del modal "Registrar producto"
    driver.find_element(By.ID, "btn-registrar-producto").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-producto")))

    # Mostrar el campo de nueva marca y escribir el nombre
    driver.find_element(By.ID, "btn-nueva-marca").click()
    espera.until(EC.visibility_of_element_located((By.ID, "p-marca-nueva-wrap")))
    driver.find_element(By.ID, "p-marca-nueva").send_keys(NOMBRE_MARCA)

    # Guardar la marca (POST /api/productos/marcas)
    driver.find_element(By.ID, "btn-guardar-marca").click()

    # El JS recarga el select y deja la marca nueva seleccionada
    espera.until(
        lambda navegador: Select(
            navegador.find_element(By.ID, "p-marca")
        ).first_selected_option.text
        == NOMBRE_MARCA
    )

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Marca creada: {NOMBRE_MARCA}")
