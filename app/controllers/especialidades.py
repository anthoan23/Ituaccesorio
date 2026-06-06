from flask import Blueprint, jsonify, render_template, request
from app.utils.decorators import jwt_required

from app.models.especialidades import Especialidad

especialidades_blueprint = Blueprint("especialidades", __name__)

@especialidades_blueprint.route("/especialidades", methods=["GET"])
@jwt_required
def pagina_especialidades():
    return render_template(
        "especialidades.html",
        show_navbar=True,
        show_notifications=True,
        active_page="especialidades",
    )

@especialidades_blueprint.route("/api/especialidades", methods=["GET"])
@jwt_required
def api_listar_especialidades():
    especialidad_model = Especialidad()
    especialidades = especialidad_model.listar_especialidades()
    return jsonify(especialidades)

@especialidades_blueprint.route("/api/especialidades", methods=["POST"])
@jwt_required
def api_agregar_especialidad():
    data = request.get_json(silent=True) or request.form
    nueva_especialidad = data.get("nombre_especialidad", "").strip()
    descripcion_especialidad = data.get("descripcion_especialidad", "").strip()

    # Crear instancia con los datos
    especialidad_model = Especialidad(
        nombre_especialidad=nueva_especialidad,
        descripcion_especialidad=descripcion_especialidad
    )
    mensaje = especialidad_model.agregar_especialidad()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 201
    else:
        return jsonify({"success": False, "message": mensaje}), 400
    
@especialidades_blueprint.route("/api/especialidades", methods=["DELETE"])
@jwt_required
def api_eliminar_especialidad():
    data = request.get_json(silent=True) or request.form
    especialidad_id = data.get("id_especialidad", "").strip()

    # Crear instancia con el ID
    especialidad_model = Especialidad(id_especialidad=especialidad_id)
    mensaje = especialidad_model.eliminar_especialidad()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200
    else:
        return jsonify({"success": False, "message": mensaje}), 400
    
@especialidades_blueprint.route("/api/especialidades", methods=["PUT"])
@jwt_required
def api_actualizar_especialidad():
    data = request.get_json(silent=True) or request.form
    especialidad_id = data.get("id_especialidad", "").strip()
    nombre_especialidad = data.get("nombre_especialidad", "").strip()
    descripcion_especialidad = data.get("descripcion_especialidad", "").strip()

    # Crear instancia con todos los datos
    especialidad_model = Especialidad(
        id_especialidad=especialidad_id,
        nombre_especialidad=nombre_especialidad,
        descripcion_especialidad=descripcion_especialidad
    )
    mensaje = especialidad_model.actualizar_especialidad()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200
    else:
        return jsonify({"success": False, "message": mensaje}), 400