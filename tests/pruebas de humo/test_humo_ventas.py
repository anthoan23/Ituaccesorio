"""Pruebas de humo del módulo Ventas.

Verifican que el servidor de pruebas está activo y responde con lo
correcto: piden las páginas del módulo por HTTP real (no usan el
test_client de Flask) y comprueban que responden 200 con HTML de
verdad. SOLO pasan si el servidor de pruebas está activo; si no,
fallan con la orden para levantarlo. Superficiales a propósito: no
prueban CRUD ni lógica de negocio (eso son pruebas de integración).

La dirección del servidor está fijada en conftest.py (variable
SERVIDOR) y las peticiones se hacen con el fixture `pedir`.
"""


def test_pagina_catalogo_responde_y_renderiza(pedir):
    """El servidor de pruebas responde 200 y devuelve HTML real para /catalogo."""
    respuesta = pedir("/catalogo")

    assert (
        respuesta.status_code == 200
    ), f"/catalogo respondió " + str(respuesta.status_code)
    assert (
        "<html" in respuesta.text.lower()
    ), f"/catalogo no devolvió un documento HTML"


def test_pagina_pagos_responde_y_renderiza(pedir):
    """El servidor de pruebas responde 200 y devuelve HTML real para /pagar."""
    respuesta = pedir("/pagar")

    assert (
        respuesta.status_code == 200
    ), f"/pagar respondió " + str(respuesta.status_code)
    assert (
        "<html" in respuesta.text.lower()
    ), f"/pagar no devolvió un documento HTML"

