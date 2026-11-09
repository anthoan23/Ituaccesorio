import os
from datetime import datetime

def guardar_captura(driver, nombre="error"):
    os.makedirs("tests/pruebas de interface/evidencia", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = os.path.join("tests/pruebas de interface/evidencia", f"{nombre}_{timestamp}.png")
    try:
        driver.save_screenshot(ruta)
        print(f"Captura guardada en: {ruta}")
    except Exception as e:
        print(f"No se pudo guardar la captura: {e}")
    return ruta

