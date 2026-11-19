"""Configuración de las pruebas de humo (compartida por todos los módulos).

Estas pruebas golpean un servidor REAL en marcha (no usan el test_client
de Flask): piden la página de cada módulo por HTTP y verifican que
responde 200 con HTML de verdad. Por eso SOLO pasan si el servidor de
pruebas está activo; si no lo está, fallan con la orden para levantarlo.

La dirección del servidor está FIJADA aquí abajo (variable SERVIDOR):
cámbiala en este archivo si el servidor corre en otro puerto o host.

Nota: si el servidor corre en modo real (ENTORNO_PRUEBA=false, como el
dev server de Docker), las páginas protegidas redirigen a /login; la
prueba igual pasa porque el servidor respondió con una página válida.
Para verificar el render de cada módulo, levanta el servidor en modo
prueba (ENTORNO_PRUEBA=true).
"""
import pytest
import requests

SERVIDOR = "http://127.0.0.1:5000"


@pytest.fixture
def pedir():
    """Pide una ruta del servidor de pruebas por HTTP real.

    Si el servidor no está activo o no responde, falla con la orden
    para levantarlo (la prueba no pasa "en vacío").
    """

    def _pedir(ruta):
        try:
            return requests.get(SERVIDOR + ruta, timeout=10)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            pytest.fail(
                f"El servidor de pruebas ({SERVIDOR}) no está activo. "
                "Levántalo con: docker-compose up --build"
            )

    return _pedir
