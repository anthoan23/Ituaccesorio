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

@empleados_blueprint.route("/api/cargos", methods=["GET"])
@jwt_required
def api_listar_cargos():
    empleados = Empleados()
    resultado = empleados.listar_cargos()
    return jsonify(resultado)

@empleados_blueprint.route("/api/especialidades", methods=["GET"])
@jwt_required
def api_listar_especialidades():
    empleados = Empleados()
    resultado = empleados.listar_especialidades()
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
    
    
@empleados_blueprint.route("/api/cargos", methods=["POST"])
@jwt_required
def api_agregar_cargo():
    datos = request.get_json(silent=True) or {}

    cargo = str(datos.get("cargo", "")).strip()

    if not cargo:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "El nombre del cargo es obligatorio.",
                }
            ),
            400,
        )

    modelo = Empleados()

    try:
        mensaje = modelo.agregar_cargo(cargo=cargo)

        if isinstance(mensaje, str) and "exitosamente" in mensaje.lower():
            return jsonify({"success": True, "message": mensaje}), 201

        return jsonify({"success": False, "error": mensaje or "No se pudo agregar el cargo."}), 400
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500

@empleados_blueprint.route("/api/especialidades", methods=["POST"])
@jwt_required
def api_agregar_especialidad():
    datos = request.get_json(silent=True) or {}

    especialidad = str(datos.get("especialidad", "")).strip()

    if not especialidad:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "El nombre de la especialidad es obligatorio.",
                }
            ),
            400,
        )

    modelo = Empleados()

    try:
        mensaje = modelo.agregar_especialidad(especialidad=especialidad)

        if isinstance(mensaje, str) and "exitosamente" in mensaje.lower():
            return jsonify({"success": True, "message": mensaje}), 201

        return jsonify({"success": False, "error": mensaje or "No se pudo agregar la especialidad."}), 400
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500

@empleados_blueprint.route("/api/empleados/<id_empleado>", methods=["DELETE"])
@jwt_required
def api_eliminar_empleado(id_empleado):
    modelo = Empleados()

    try:
        mensaje = modelo.eliminar_empleado(id_em=id_empleado)

        if isinstance(mensaje, str) and "eliminado" in mensaje.lower():
            return jsonify({"success": True, "message": mensaje}), 200

        return jsonify({"success": False, "error": mensaje or "No se pudo eliminar el empleado."}), 400
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500
    
@empleados_blueprint.route("/api/cargos/<n_cargo>", methods=["DELETE"])
@jwt_required
def api_eliminar_cargo(n_cargo):
    modelo = Empleados()

    try:
        mensaje = modelo.eliminar_cargo(n_cargo=n_cargo)

        if isinstance(mensaje, str) and "eliminado" in mensaje.lower():
            return jsonify({"success": True, "message": mensaje}), 200

        return jsonify({"success": False, "error": mensaje or "No se pudo eliminar el cargo."}), 400
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500

@empleados_blueprint.route("/api/especialidades/<n_especialidad>", methods=["DELETE"])
@jwt_required
def api_eliminar_especialidad(n_especialidad):
    modelo = Empleados()

    try:
        mensaje = modelo.eliminar_especialidad(n_especialidad=n_especialidad)

        if isinstance(mensaje, str) and ("eliminado" in mensaje.lower() or "eliminada" in mensaje.lower()):
            return jsonify({"success": True, "message": mensaje}), 200

        return jsonify({"success": False, "error": mensaje or "No se pudo eliminar la especialidad."}), 400
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500
    
@empleados_blueprint.route("/api/empleados/<id_empleado>", methods=["PUT"])
@jwt_required
def api_actualizar_empleado(id_empleado):
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
        mensaje = modelo.actualizar_empleado(
            id_empleado=id_empleado,
            nombre=nombre,
            apellido=apellido,
            celular=celular,
            correo=correo,
            direccion=direccion,
        )

        if isinstance(mensaje, str) and "actualizado" in mensaje.lower():
            return jsonify({"success": True, "message": mensaje}), 200

        return jsonify({"success": False, "error": mensaje or "No se pudo actualizar el empleado."}), 400
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500

@empleados_blueprint.route("/api/cargos/<id_cargo>", methods=["PUT"])
@jwt_required
def api_actualizar_cargo(id_cargo):
    datos = request.get_json(silent=True) or {}

    cargo_nuevo = str(datos.get("cargo_nuevo", "")).strip()
  

    if not cargo_nuevo:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "El nombre del cargo es obligatorio.",
                }
            ),
            400,
        )

    # permitir id original en body (`id_viejo`), si viene usarlo
    cargo_viejo = datos.get('id_viejo')
  
    modelo = Empleados()

    try:
        mensaje = modelo.actualizar_cargo(id_cargo=id_cargo, cargo_n=cargo_nuevo, cargo_v=cargo_viejo)

        if isinstance(mensaje, str) and "exitos" in mensaje.lower():
            return jsonify({"success": True, "message": mensaje}), 200

        return jsonify({"success": False, "error": mensaje or "No se pudo actualizar el cargo."}), 400
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500

@empleados_blueprint.route("/api/especialidades/<id_especialidad>", methods=["PUT"])
@jwt_required
def api_actualizar_especialidad(id_especialidad):
    datos = request.get_json(silent=True) or {}

    especialidad_nuevo = str(datos.get("especialidad_nuevo", "")).strip()

    if not especialidad_nuevo:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "El nombre de la especialidad es obligatorio.",
                }
            ),
            400,
        )

    # permitir nombre original en body (`especialidad_viejo`), si viene usarlo
    especialidad_vieja = str(datos.get("especialidad_viejo", "")).strip()
  
    modelo = Empleados()

    try:
        mensaje = modelo.actualizar_especialidad(
            id_especialidad=id_especialidad,
            especialidad_n=especialidad_nuevo,
            especialidad_v=especialidad_vieja,
        )

        if isinstance(mensaje, str) and "exitos" in mensaje.lower():
            return jsonify({"success": True, "message": mensaje}), 200

        return jsonify({"success": False, "error": mensaje or "No se pudo actualizar la especialidad."}), 400
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500