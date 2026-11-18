import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

URL_PRODUCTOS = f"{os.getenv('ITU_URL_BASE', 'http://127.0.0.1:5000').rstrip('/')}/productos"
TIEMPO_ESPERA = 10

# Nombre de la clase de producto que se va a crear
NOMBRE_CLASE = "Clase Prueba"


def test_crear_clase(driver):
    driver.get(URL_PRODUCTOS)
    espera = WebDriverWait(driver, TIEMPO_ESPERA)
    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))

    # El formulario de clases vive dentro del modal "Registrar producto"
    driver.find_element(By.ID, "btn-registrar-producto").click()
    espera.until(EC.visibility_of_element_located((By.ID, "modal-producto")))

    # Mostrar el campo de nueva clase y escribir el nombre
    driver.find_element(By.ID, "btn-nueva-clase").click()
    espera.until(EC.visibility_of_element_located((By.ID, "p-clase-nueva-wrap")))
    driver.find_element(By.ID, "p-clase-nueva").send_keys(NOMBRE_CLASE)

    # Guardar la clase (POST /api/productos/clases)
    driver.find_element(By.ID, "btn-guardar-clase").click()

    # El JS recarga el select y deja la clase nueva seleccionada
    espera.until(
        lambda navegador: Select(
            navegador.find_element(By.ID, "p-clase")
        ).first_selected_option.text
        == NOMBRE_CLASE
    )

    espera.until(EC.invisibility_of_element_located((By.ID, "feedback-modal")))
    print(f"Clase creada: {NOMBRE_CLASE}")
