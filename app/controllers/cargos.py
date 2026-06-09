from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.bitacora import registrar_en_bitacora
from app.models.cargos import Cargo

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

    if not nombre_cargo:
        return jsonify({"success": False, "message": "El nombre del cargo es obligatorio."}), 400

    cargo_model = Cargo(
        nombre_cargo=nombre_cargo,
        descripcion_cargo=descripcion_cargo
    )
    mensaje = cargo_model.agregar_cargo()

    if "exitosamente" in mensaje:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Crear cargo",
            descripcion=f"Se creó el cargo: {nombre_cargo}",
            usuario_id=usuario_id,
            modulo_nombre="Cargos"
        )
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

    if not cargo_id:
        return jsonify({"success": False, "message": "El ID del cargo es obligatorio."}), 400
    if not nombre_cargo:
        return jsonify({"success": False, "message": "El nombre del cargo es obligatorio."}), 400

    cargo_model = Cargo(
        id_cargo=cargo_id,
        nombre_cargo=nombre_cargo,
        descripcion_cargo=descripcion_cargo
    )
    mensaje = cargo_model.actualizar_cargo()

    if "exitosamente" in mensaje:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Actualizar cargo",
            descripcion=f"Se actualizó el cargo ID: {cargo_id} - Nuevo nombre: {nombre_cargo}",
            usuario_id=usuario_id,
            modulo_nombre="Cargos"
        )
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "message": mensaje}), 400


@cargos_blueprint.route("/api/cargos", methods=["DELETE"])
@jwt_required
@tiene_permiso('Cargos', 'eliminar')
def api_eliminar_cargo():
    data = request.get_json(silent=True) or request.form
    cargo_id = data.get("id_cargo", "").strip()

    if not cargo_id:
        return jsonify({"success": False, "message": "El ID del cargo es obligatorio."}), 400

    cargo_model_temp = Cargo()
    cargo_existente = cargo_model_temp.obtener_cargo_por_id(cargo_id)
    nombre_cargo = cargo_existente.get("nombre_cargo") if cargo_existente else cargo_id

    cargo_model = Cargo(id_cargo=cargo_id)
    mensaje = cargo_model.eliminar_cargo()

    if "exitosamente" in mensaje:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Eliminar cargo",
            descripcion=f"Se eliminó el cargo ID: {cargo_id} - Nombre: {nombre_cargo}",
            usuario_id=usuario_id,
            modulo_nombre="Cargos"
        )
        return jsonify({"success": True, "message": mensaje}), 200
    else:
        return jsonify({"success": False, "message": mensaje}), 400