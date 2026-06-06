from flask import Blueprint, jsonify, render_template, request
from app.utils.decorators import jwt_required

from app.models.cargos import Cargo

cargos_blueprint = Blueprint("cargos", __name__)

@cargos_blueprint.route("/cargos", methods=["GET"])
@jwt_required
def pagina_cargos():
    return render_template(
        "cargos.html",
        show_navbar=True,
        show_notifications=True,
        active_page="cargos",
    )

@cargos_blueprint.route("/api/cargos", methods=["GET"])
@jwt_required
def api_listar_cargos():
    cargo_model = Cargo()
    cargos = cargo_model.listar_cargos()
    return jsonify(cargos)

@cargos_blueprint.route("/api/cargos", methods=["POST"])
@jwt_required
def api_agregar_cargo():
    data = request.get_json(silent=True) or request.form
    nombre_cargo = data.get("nombre_cargo", "").strip()
    descripcion_cargo = data.get("descripcion_cargo", "").strip()

    # Crear instancia con los datos y asignar a los atributos
    cargo_model = Cargo(
        nombre_cargo=nombre_cargo,
        descripcion_cargo=descripcion_cargo
    )
    mensaje = cargo_model.agregar_cargo()  # Sin parámetros

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 201
    else:
        return jsonify({"success": False, "message": mensaje}), 400

@cargos_blueprint.route("/api/cargos", methods=["PUT"])
@jwt_required
def api_actualizar_cargo():
    data = request.get_json(silent=True) or request.form
    cargo_id = data.get("id_cargo", "").strip()
    nombre_cargo = data.get("nombre_cargo", "").strip()
    descripcion_cargo = data.get("descripcion_cargo", "").strip()

    # Crear instancia con los datos y asignar a los atributos
    cargo_model = Cargo(
        id_cargo=cargo_id,
        nombre_cargo=nombre_cargo,
        descripcion_cargo=descripcion_cargo
    )
    mensaje = cargo_model.actualizar_cargo()  # Sin parámetros

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "message": mensaje}), 400

@cargos_blueprint.route("/api/cargos", methods=["DELETE"])
@jwt_required
def api_eliminar_cargo():
    data = request.get_json(silent=True) or request.form
    cargo_id = data.get("id_cargo", "").strip()

    # Crear instancia con el ID y asignar al atributo
    cargo_model = Cargo(id_cargo=cargo_id)
    mensaje = cargo_model.eliminar_cargo()  # Sin parámetros

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200
    else:
        return jsonify({"success": False, "message": mensaje}), 400