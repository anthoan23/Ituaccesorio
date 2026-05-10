from flask import Blueprint, jsonify, render_template, request
from app.utils.decorators import jwt_required

from app.models.empleados import Empleados

empleados_blueprint = Blueprint("empleados", __name__)


@empleados_blueprint.route("/empleados", methods=["GET"])
@jwt_required
def pagina_empleados():
    return render_template(
        "empleados.html",
    )

@empleados_blueprint.route("/api/empleados", methods=["GET"])
@jwt_required
def api_listar_empleados():
    empleados = Empleados()
    resultado = empleados.listar_empleados()
    return jsonify(resultado)


@empleados_blueprint.route("/api/empleados", methods=["POST"])
@jwt_required
def api_agregar_empleado():
    datos = request.get_json(silent=True) or {}

    cedula = str(datos.get("cedula", "")).strip()
    nombre = str(datos.get("nombre", "")).strip()
    apellido = str(datos.get("apellido", "")).strip()
    celular = str(datos.get("celular", "")).strip()
    correo = str(datos.get("correo", "")).strip()
    direccion = str(datos.get("direccion", "")).strip()

    if not all([cedula, nombre, apellido, celular, correo, direccion]):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Todos los campos son obligatorios.",
                }
            ),
            400,
        )

    modelo = Empleados()

    try:
        mensaje = modelo.agregar_empleado(
            cedula=cedula,
            nombre=nombre,
            apellido=apellido,
            celular=celular,
            correo=correo,
            direccion=direccion,
        )

        if isinstance(mensaje, str) and "exitosamente" in mensaje.lower():
            return jsonify({"success": True, "message": mensaje}), 201

        return jsonify({"success": False, "error": mensaje or "No se pudo agregar el empleado."}), 400
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500
