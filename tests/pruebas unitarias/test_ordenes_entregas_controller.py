from unittest.mock import patch

from flask import Flask, g

from app.controllers.ordenes_entregas import api_registrar_entrega


def test_registrar_entrega_usa_empleado_seleccionado_sin_id_en_token():
    app = Flask(__name__)
    endpoint = api_registrar_entrega.__wrapped__.__wrapped__

    with app.test_request_context(
        "/api/ordenes_entregas/OC000001/registrar",
        method="POST",
        json={"id_empleado": "123456", "fecha_entrega": "2026-01-15"},
    ):
        g.user = {}
        with patch("app.controllers.ordenes_entregas.Empleados") as empleados, patch(
            "app.controllers.ordenes_entregas.OrdenEntregaModel"
        ) as modelo_entrega:
            empleados.return_value.consultar_empleado.return_value = {
                "nombre": "Ana",
                "apellido": "Pérez",
            }
            modelo_entrega.return_value.registrar_entrega.return_value = True

            response, status = endpoint("OC000001")

    assert status == 200
    assert response.get_json()["success"] is True
    modelo_entrega.assert_called_once_with(
        id_orden="OC000001",
        recibido_por="Ana Pérez",
        fecha_entrega="2026-01-15",
        id_empleado=123456,
        usuario_id=None,
    )
