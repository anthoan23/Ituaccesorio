from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.bitacora import registrar_en_bitacora
from app.models.empleados import Empleados

empleados_blueprint = Blueprint("empleados", __name__)


def _usuario_actual():
    """Obtiene el ID del usuario actual"""
    user = getattr(g, 'user', None)
    if not user:
        return "SYSTEM"
    if isinstance(user, dict):
        return str(user.get("usuario_id") or user.get("id") or "SYSTEM")
    return str(getattr(user, "usuario_id", None) or getattr(user, "id", None) or "SYSTEM")


@empleados_blueprint.route("/empleados", methods=["GET"])
@jwt_required
@tiene_permiso('Empleados', 'consultar')
def pagina_empleados():
    return render_template(
        "empleados.html",
        show_navbar=True,
        show_notifications=True,
        active_page="empleados",
    )


@empleados_blueprint.route("/api/empleados", methods=["GET"])
@jwt_required
@tiene_permiso('Empleados', 'consultar')
def api_listar_empleados():
    empleados_model = Empleados()
    resultado = empleados_model.listar_empleados()
    return jsonify(resultado)


@empleados_blueprint.route("/api/empleados/lista", methods=["GET"])
@jwt_required
@tiene_permiso('Empleados', 'consultar')
def api_listar_empleados_cargos():
    empleados_model = Empleados()
    resultado1 = empleados_model.listar_cargos()
    resultado2 = empleados_model.listar_especialidades()
    return jsonify({"cargos": resultado1, "especialidades": resultado2})


@empleados_blueprint.route("/api/empleados/graficos", methods=["GET"])
@jwt_required
@tiene_permiso('Empleados', 'consultar')
def api_listar_empleados_graficos():
    empleados_model = Empleados()
    resultado1 = empleados_model.listar_empleados_por_cargo()
    resultado2 = empleados_model.listar_empleados_por_especialidad()
    return jsonify({"cargos": resultado1, "especialidades": resultado2})


@empleados_blueprint.route("/api/empleados/consultar", methods=["POST"])
@jwt_required
@tiene_permiso('Empleados', 'consultar')
def api_consultar_empleado():
    datos = request.get_json(silent=True) or {}
    cedula = str(datos.get("cedula", "")).strip()
    
    if not cedula:
        return jsonify({"success": False, "error": "La cédula es obligatoria."}), 400
    
    empleados_model = Empleados(id_empleado=cedula)
    resultado1 = empleados_model.consultar_empleado()
    
    if not resultado1:
        return jsonify({"success": False, "error": "Empleado no encontrado."}), 404
    
    # Registrar en bitácora la consulta
    registrar_en_bitacora(
        accion="Consultar empleado",
        descripcion=f"Se consultó el empleado con cédula: {cedula}",
        usuario_id=_usuario_actual(),
        modulo_nombre="Empleados"
    )
    
    if resultado1['cargo'] == 'Técnico':
        empleados_model = Empleados(id_empleado=cedula)
        resultado2 = empleados_model.consultar_especialidades_empleado()
        return jsonify({"success": True, "empleado": resultado1, "especialidades": resultado2})
    
    return jsonify({"success": True, "empleado": resultado1})


@empleados_blueprint.route("/api/empleados", methods=["POST"])
@jwt_required
@tiene_permiso('Empleados', 'registrar')
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

    if not all([cedula, cargo_id, nombre, apellido]):
        return jsonify({
            "success": False,
            "error": "La cédula, cargo, nombre y apellido son obligatorios.",
        }), 400

    empleados_model = Empleados(
        id_empleado=cedula,
        id_cargo=cargo_id,
        nombre_empleado=nombre,
        apellido_empleado=apellido,
        celular_empleado=celular,
        correo_empleado=correo,
        direccion_empleado=direccion,
        especialidades=especialidades
    )
    
    mensaje = empleados_model.agregar_empleado()

    if "exitosamente" in mensaje:
        # Registrar en bitácora
        registrar_en_bitacora(
            accion="Crear empleado",
            descripcion=f"Se creó el empleado: {cedula} - {nombre} {apellido}",
            usuario_id=_usuario_actual(),
            modulo_nombre="Empleados"
        )
        return jsonify({"success": True, "message": mensaje}), 201
    
    return jsonify({"success": False, "error": mensaje}), 400


@empleados_blueprint.route("/api/empleados", methods=["PUT"])
@jwt_required
@tiene_permiso('Empleados', 'modificar')
def api_actualizar_empleado():
    datos = request.get_json(silent=True) or {}
    
    id_empleado = str(datos.get("id_empleado", "")).strip()
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

    # Validaciones
    if not id_empleado:
        return jsonify({"success": False, "error": "El ID del empleado es obligatorio."}), 400
    
    if not all([cedula, cargo_id, nombre, apellido]):
        return jsonify({
            "success": False,
            "error": "La cédula, cargo, nombre y apellido son obligatorios.",
        }), 400

    empleados_model = Empleados(
        id_empleado=id_empleado,
        id_cargo=cargo_id,
        nombre_empleado=nombre,
        apellido_empleado=apellido,
        celular_empleado=celular,
        correo_empleado=correo,
        direccion_empleado=direccion,
        especialidades=especialidades
    )
    
    mensaje = empleados_model.actualizar_empleado()

    if "exitosamente" in mensaje:
        # Registrar en bitácora
        registrar_en_bitacora(
            accion="Actualizar empleado",
            descripcion=f"Se actualizó el empleado ID: {id_empleado} - {nombre} {apellido}",
            usuario_id=_usuario_actual(),
            modulo_nombre="Empleados"
        )
        return jsonify({"success": True, "message": mensaje}), 200
    
    return jsonify({"success": False, "error": mensaje}), 400


@empleados_blueprint.route("/api/empleados", methods=["DELETE"])
@jwt_required
@tiene_permiso('Empleados', 'eliminar')
def api_eliminar_empleado():
    datos = request.get_json(silent=True) or {}
    id_empleado = str(datos.get("id_empleado", "")).strip()

    if not id_empleado:
        return jsonify({"success": False, "error": "El ID del empleado es obligatorio."}), 400

    # Obtener los datos del empleado antes de eliminar para la bitácora
    empleados_model = Empleados(id_empleado=id_empleado)
    empleado_existente = empleados_model.consultar_empleado()
    nombre_completo = f"{empleado_existente.get('nombre', '')} {empleado_existente.get('apellido', '')}" if empleado_existente else id_empleado

    mensaje = empleados_model.eliminar_empleado()

    if "exitosamente" in mensaje:
        # Registrar en bitácora
        registrar_en_bitacora(
            accion="Eliminar empleado",
            descripcion=f"Se eliminó el empleado ID: {id_empleado} - Nombre: {nombre_completo}",
            usuario_id=_usuario_actual(),
            modulo_nombre="Empleados"
        )
        return jsonify({"success": True, "message": mensaje}), 200
    
    return jsonify({"success": False, "error": mensaje}), 400


@empleados_blueprint.route("/api/empleados/tecnicos", methods=["GET"])
@jwt_required
@tiene_permiso('Empleados', 'consultar')
def api_listar_tecnicos():
    empleados_model = Empleados()
    tecnicos = empleados_model.listar_tecnicos()
    return jsonify(tecnicos)



