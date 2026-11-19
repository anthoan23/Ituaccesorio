"""Prueba de humo del módulo Validación de pagos.

Verifica que el servidor de pruebas está activo y responde con lo
correcto: pide la página del módulo por HTTP real (no usa el
test_client de Flask) y comprueba que responde 200 con HTML de verdad.
SOLO pasa si el servidor de pruebas está activo; si no, falla con la
orden para levantarlo. Superficial a propósito: no prueba CRUD ni
lógica de negocio (eso son pruebas de integración).

La dirección del servidor está fijada en conftest.py (variable
SERVIDOR) y la petición se hace con el fixture `pedir`.
"""


def test_pagina_responde_y_renderiza(pedir):
    """El servidor de pruebas responde 200 y devuelve HTML real para /admin/validar-pagos."""
    respuesta = pedir("/admin/validar-pagos")

    assert (
        respuesta.status_code == 200
    ), f"/admin/validar-pagos respondió " + str(respuesta.status_code)
    assert (
        "<html" in respuesta.text.lower()
    ), f"/admin/validar-pagos no devolvió un documento HTML"
