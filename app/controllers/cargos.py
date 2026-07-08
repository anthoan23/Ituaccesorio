from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.cargos import Cargo
from app.utils.validators import validar_texto, validar_texto_numero

cargos_blueprint = Blueprint("cargos", __name__)


@cargos_blueprint.route("/cargos", methods=["GET"])
@jwt_required
@tiene_permiso('Cargos', 'consultar')
def pagina_cargos():
    return render_template(
        "cargos.html",
        show_navbar=True,
        show_notifications=True,
        active_page="cargos",
    )


@cargos_blueprint.route("/api/cargos", methods=["GET"])
@jwt_required
@tiene_permiso('Cargos', 'consultar')
def api_listar_cargos():
    cargo_model = Cargo()
    cargos = cargo_model.listar_cargos()
    return jsonify(cargos)


@cargos_blueprint.route("/api/cargos", methods=["POST"])
@jwt_required
@tiene_permiso('Cargos', 'registrar')
def api_agregar_cargo():
    data = request.get_json(silent=True) or request.form
    nombre_cargo = data.get("nombre_cargo", "").strip()
    descripcion_cargo = data.get("descripcion_cargo", "").strip()

    validar_nombre = validar_texto(nombre_cargo, 3, 30, "Nombre")
    if validar_nombre:
        return jsonify({"success": False, "message": validar_nombre}), 400

    validar_descripcion = validar_texto_numero(descripcion_cargo, 3, 250, "Descripción")
    if validar_descripcion:
        return jsonify({"success": False, "message": validar_descripcion}), 400

    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    cargo_model = Cargo(
        nombre_cargo=nombre_cargo,
        descripcion_cargo=descripcion_cargo,
        usuario_id=usuario_id
    )
    
    mensaje = cargo_model.agregar_cargo()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 201
    else:
        return jsonify({"success": False, "message": mensaje}), 400


@cargos_blueprint.route("/api/cargos", methods=["PUT"])
@jwt_required
@tiene_permiso('Cargos', 'modificar')
def api_actualizar_cargo():
    data = request.get_json(silent=True) or request.form
    cargo_id = data.get("id_cargo", "").strip()
    nombre_cargo = data.get("nombre_cargo", "").strip()
    descripcion_cargo = data.get("descripcion_cargo", "").strip()

    validar_cargo_id = validar_texto_numero(cargo_id, 9, 10, "ID del Cargo")
    if validar_cargo_id:
        return jsonify({"success": False, "message": validar_cargo_id}), 400
    
    validar_nombre = validar_texto(nombre_cargo, 3, 30, "Nombre")
    if validar_nombre:
        return jsonify({"success": False, "message": validar_nombre}), 400
    
    validar_descripcion = validar_texto_numero(descripcion_cargo, 3, 250, "Descripción")
    if validar_descripcion:
        return jsonify({"success": False, "message": validar_descripcion}), 400

    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    cargo_model = Cargo(
        id_cargo=cargo_id,
        nombre_cargo=nombre_cargo,
        descripcion_cargo=descripcion_cargo,
        usuario_id=usuario_id
    )
    
    mensaje = cargo_model.actualizar_cargo()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "message": mensaje}), 400


@cargos_blueprint.route("/api/cargos", methods=["DELETE"])
@jwt_required
@tiene_permiso('Cargos', 'eliminar')
def api_eliminar_cargo():
    data = request.get_json(silent=True) or request.form
    cargo_id = data.get("id_cargo", "").strip()

    validar_cargo_id = validar_texto_numero(cargo_id, 9, 10, "ID del Cargo")
    if validar_cargo_id:
        return jsonify({"success": False, "message": validar_cargo_id}), 400

    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    cargo_model = Cargo(
        id_cargo=cargo_id,
        usuario_id=usuario_id
    )
    
    mensaje = cargo_model.eliminar_cargo()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200
    else:
        return jsonify({"success": False, "message": mensaje}), 400