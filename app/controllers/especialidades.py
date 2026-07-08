from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso
from app.utils.validators import validar_texto, validar_texto_numero
from app.models.especialidades import Especialidad

especialidades_blueprint = Blueprint("especialidades", __name__)


@especialidades_blueprint.route("/especialidades", methods=["GET"])
@jwt_required
@tiene_permiso('Especialidades', 'consultar')
def pagina_especialidades():
    return render_template(
        "especialidades.html",
        show_navbar=True,
        show_notifications=True,
        active_page="especialidades",
    )


@especialidades_blueprint.route("/api/especialidades", methods=["GET"])
@jwt_required
@tiene_permiso('Especialidades', 'consultar')
def api_listar_especialidades():
    especialidad_model = Especialidad()
    especialidades = especialidad_model.listar_especialidades()
    return jsonify(especialidades)


@especialidades_blueprint.route("/api/especialidades", methods=["POST"])
@jwt_required
@tiene_permiso('Especialidades', 'registrar')
def api_agregar_especialidad():
    data = request.get_json(silent=True) or request.form
    nueva_especialidad = data.get("nombre_especialidad", "").strip()
    descripcion_especialidad = data.get("descripcion_especialidad", "").strip()

    validar_nombre = validar_texto(nueva_especialidad, 3, 30, "Nombre de la especialidad")
    if validar_nombre:
        return jsonify({"success": False, "message": validar_nombre}), 400

    validar_descripcion = validar_texto_numero(descripcion_especialidad, 3, 250, "Descripción de la especialidad")
    if validar_descripcion:
        return jsonify({"success": False, "message": validar_descripcion}), 400

    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    especialidad_model = Especialidad(
        nombre_especialidad=nueva_especialidad,
        descripcion_especialidad=descripcion_especialidad,
        usuario_id=usuario_id
    )
    mensaje = especialidad_model.agregar_especialidad()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 201
    else:
        return jsonify({"success": False, "message": mensaje}), 400


@especialidades_blueprint.route("/api/especialidades", methods=["PUT"])
@jwt_required
@tiene_permiso('Especialidades', 'modificar')
def api_actualizar_especialidad():
    data = request.get_json(silent=True) or request.form
    especialidad_id = data.get("id_especialidad", "").strip()
    nombre_especialidad = data.get("nombre_especialidad", "").strip()
    descripcion_especialidad = data.get("descripcion_especialidad", "").strip()

    validar_id = validar_texto_numero(especialidad_id, 9, 10, "ID de la especialidad")
    if validar_id:
        return jsonify({"success": False, "message": validar_id}), 400

    validar_nombre = validar_texto(nombre_especialidad, 3, 30, "Nombre de la especialidad")
    if validar_nombre:
        return jsonify({"success": False, "message": validar_nombre}), 400

    validar_descripcion = validar_texto_numero(descripcion_especialidad, 3, 250, "Descripción de la especialidad")
    if validar_descripcion:
        return jsonify({"success": False, "message": validar_descripcion}), 400

    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    especialidad_model = Especialidad(
        id_especialidad=especialidad_id,
        nombre_especialidad=nombre_especialidad,
        descripcion_especialidad=descripcion_especialidad,
        usuario_id=usuario_id
    )
    mensaje = especialidad_model.actualizar_especialidad()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200
    else:
        return jsonify({"success": False, "message": mensaje}), 400


@especialidades_blueprint.route("/api/especialidades", methods=["DELETE"])
@jwt_required
@tiene_permiso('Especialidades', 'eliminar')
def api_eliminar_especialidad():
    data = request.get_json(silent=True) or request.form
    especialidad_id = data.get("id_especialidad", "").strip()

    validdar_id = validar_texto_numero(especialidad_id, 9, 10, "ID de la especialidad")
    if validdar_id:
        return jsonify({"success": False, "message": validdar_id}), 400

    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    especialidad_model = Especialidad(
        id_especialidad=especialidad_id,
        usuario_id=usuario_id
    )
    mensaje = especialidad_model.eliminar_especialidad()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200
    else:
        return jsonify({"success": False, "message": mensaje}), 400