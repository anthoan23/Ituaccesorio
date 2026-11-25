from flask import Flask

from app.controllers.tradein_empleados import _guardar_fotos


def test_modificacion_sin_archivos_no_requiere_subidas():
    app = Flask(__name__)

    with app.test_request_context(method="PUT"):
        assert _guardar_fotos(obligatorio=False) == ([], None)


def test_registro_sin_archivos_sigue_requiriendo_subidas():
    app = Flask(__name__)

    with app.test_request_context(method="POST"):
        assert _guardar_fotos() == (None, "No se subieron archivos")
