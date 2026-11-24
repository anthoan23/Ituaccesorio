"""Prueba de humo de todas las páginas del sistema (en un solo lugar).

El arreglo URLS (abajo) concentra todas las rutas a verificar y una sola
prueba parametrizada las recorre: pide cada página por HTTP real (no usa
el test_client de Flask) y comprueba que responde 200 con HTML de verdad.
Superficial a propósito: no prueba CRUD ni lógica de negocio (eso son
pruebas de integración).

SOLO pasa si el servidor de pruebas está activo; si no lo está, falla
con la orden para levantarlo.

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

SERVIDOR = "http://127.0.0.1:5001"

# Todas las rutas a probar: tuplas (módulo, ruta). Para añadir una
# página nueva al humo, agrega una tupla aquí y nada más.
URLS = [
    ("Dashboard", "/"),
    ("Login", "/login"),
    ("Clientes", "/clientes"),
    ("Productos", "/productos"),
    ("Inventario", "/inventario"),
    ("Catálogo", "/catalogo"),
    ("Pagar", "/pagar"),
    ("Proveedores", "/proveedores"),
    ("Órdenes de compra", "/ordenes_compra"),
    ("Órdenes de servicio", "/ordenes-servicio"),
    ("Órdenes de entregas", "/ordenes_entregas"),
    ("Entregas", "/entregas"),
    ("Taller", "/taller"),
    ("Taller celular", "/taller_celular/OS-0001"),
    ("Trade-in (clientes)", "/trade-in"),
    ("Trade-in (empleados)", "/empleados/tradein"),
    ("Empleados", "/empleados"),
    ("Especialidades", "/especialidades"),
    ("Cargos", "/cargos"),
    ("Usuarios", "/usuarios"),
    ("Bitácora", "/bitacora"),
    ("Backup", "/backup"),
    ("Reportes de ventas", "/admin/reportes-ventas"),
    ("Validación de pagos", "/admin/validar-pagos"),
]


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


@pytest.mark.parametrize("modulo,ruta", URLS, ids=[modulo for modulo, _ in URLS])
def test_pagina_responde_y_renderiza(pedir, modulo, ruta):
    """El servidor de pruebas responde 200 y devuelve HTML real para cada ruta."""
    respuesta = pedir(ruta)

    assert (
        respuesta.status_code == 200
    ), f"{ruta} respondió " + str(respuesta.status_code)
    assert (
        "<html" in respuesta.text.lower()
    ), f"{ruta} no devolvió un documento HTML"
