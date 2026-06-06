from flask import Blueprint, jsonify, render_template, request
from app.utils.decorators import jwt_required

from app.models.empleados import Empleados

empleados_blueprint = Blueprint("empleados", __name__)


@empleados_blueprint.route("/empleados", methods=["GET"])
@jwt_required
def pagina_empleados():
    return render_template(
        "empleados.html",
        show_navbar=True,
        show_notifications=True,
        active_page="empleados",
    )





@empleados_blueprint.route("/api/empleados", methods=["GET"])
@jwt_required
def api_listar_empleados():
    empleados = Empleados()
    resultado = empleados.listar_empleados()
    return jsonify(resultado)

@empleados_blueprint.route("/api/empleados/lista", methods=["GET"])
@jwt_required
def api_listar_empleados_cargos():
    empleados = Empleados()
    resultado1 = empleados.lista_crgos()
    resultado2 = empleados.lista_especialidades()
    return jsonify({"cargos": resultado1, "especialidades": resultado2})


@empleados_blueprint.route("/api/empleados/graficos", methods=["GET"])
@jwt_required
def api_listar_empleados_graficos():
    empleados = Empleados()
    resultado1 = empleados.listar_empleados_cargos()
    resultado2 = empleados.listar_empleados_especialidades()
    return jsonify({"cargos": resultado1, "especialidades": resultado2})




@empleados_blueprint.route("/api/empleados/consultar", methods=["POST"])
@jwt_required
def api_consultar_empleado():
    datos = request.get_json(silent=True) or {}
    cedula = str(datos.get("cedula", "")).strip()
    empleados = Empleados()
    resultado1 = empleados.consultar_empleado(cedula)
    
    if not resultado1:
        return jsonify({"success": False, "error": "Empleado no encontrado."}), 404
    
    if resultado1['cargo'] == 'Técnico':
        resultado2 = empleados.consultar_especialidades_empleado(cedula)
        return jsonify({"success": True, "empleado": resultado1, "especialidades": resultado2})
    
    return jsonify({"success": True, "empleado": resultado1})

@empleados_blueprint.route("/api/empleados", methods=["POST"])
@jwt_required
def api_agregar_empleado():
    datos = request.get_json(silent=True) or {}

    cedula = str(datos.get("cedula", "")).strip()
    cargo_id = str(datos.get("id_cargo", "")).strip()
    nombre = str(datos.get("nombre", "")).strip()
    apellido = str(datos.get("apellido", "")).strip()
    celular = str(datos.get("celular", "")).strip()
    correo = str(datos.get("correo", "")).strip()
    direccion = str(datos.get("direccion", "")).strip()
    # especialidades may be sent as a list of ids
    especialidades = datos.get('especialidades') or []
    if isinstance(especialidades, str):
        try:
            # try parsing JSON list
            import json
            especialidades = json.loads(especialidades)
        except Exception:
            # comma separated
            especialidades = [s.strip() for s in especialidades.split(',') if s.strip()]

    if not all([cedula, cargo_id, nombre, apellido, celular, correo, direccion]):
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
            cargo_id=cargo_id,
            nombre=nombre,
            apellido=apellido,
            celular=celular,
            correo=correo,
            direccion=direccion,
            especialidades=especialidades,
        )

        if isinstance(mensaje, str) and "exitosamente" in mensaje.lower():
            return jsonify({"success": True, "message": mensaje}), 201

        return jsonify({"success": False, "error": mensaje or "No se pudo agregar el empleado."}), 400
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500
    
    



    

    
@empleados_blueprint.route("/api/empleados/<id_empleado>", methods=["PUT"])
@jwt_required
def api_actualizar_empleado(id_empleado):
    datos = request.get_json(silent=True) or {}

    cedula = str(datos.get("cedula", "")).strip()
    cargo_id = str(datos.get("id_cargo", "")).strip()
    nombre = str(datos.get("nombre", "")).strip()
    apellido = str(datos.get("apellido", "")).strip()
    celular = str(datos.get("celular", "")).strip()
    correo = str(datos.get("correo", "")).strip()
    direccion = str(datos.get("direccion", "")).strip()
    especialidades = datos.get('especialidades') or []
    if isinstance(especialidades, str):
        try:
            import json
            especialidades = json.loads(especialidades)
        except Exception:
            especialidades = [s.strip() for s in especialidades.split(',') if s.strip()]

    if not all([cedula, cargo_id, nombre, apellido, celular, correo, direccion]):
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
            cargo_id=cargo_id,
            nombre=nombre,
            apellido=apellido,
            celular=celular,
            correo=correo,
            direccion=direccion,
            especialidades=especialidades,
        )

        if isinstance(mensaje, str) and "actualizado" in mensaje.lower():
            return jsonify({"success": True, "message": mensaje}), 200

        return jsonify({"success": False, "error": mensaje or "No se pudo actualizar el empleado."}), 400
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500


