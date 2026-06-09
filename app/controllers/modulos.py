from flask import Blueprint, jsonify, request, g
from app.utils.decorators import jwt_required, solo_roles
from app.models.bitacora import registrar_en_bitacora
from app.models.modulos import Modulo

modulos_blueprint = Blueprint("modulos", __name__)


@modulos_blueprint.route("/api/modulos", methods=["GET"])
@jwt_required
@solo_roles(['admin'])
def api_listar_modulos():
    modulo_model = Modulo()
    modulos = modulo_model.listar_modulos()
    return jsonify({"success": True, "modulos": modulos or []})


@modulos_blueprint.route("/api/modulos", methods=["POST"])
@jwt_required
@solo_roles(['admin'])
def api_crear_modulo():
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre", "").strip()
    descripcion = data.get("descripcion", "").strip()

    if not nombre:
        return jsonify({"success": False, "error": "El nombre del módulo es obligatorio."}), 400

    modulo_model = Modulo(nombre=nombre, descripcion=descripcion)
    mensaje = modulo_model.agregar_modulo()

    if "exitosamente" in mensaje:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Crear módulo",
            descripcion=f"Se creó el módulo: {nombre}",
            usuario_id=usuario_id,
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje, "id": modulo_model.id}), 201

    return jsonify({"success": False, "error": mensaje}), 400


@modulos_blueprint.route("/api/modulos/<modulo_id>", methods=["PUT"])
@jwt_required
@solo_roles(['admin'])
def api_actualizar_modulo(modulo_id):
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre", "").strip()
    descripcion = data.get("descripcion", "").strip()

    if not nombre:
        return jsonify({"success": False, "error": "El nombre del módulo es obligatorio."}), 400

    modulo_model = Modulo(id=modulo_id, nombre=nombre, descripcion=descripcion)
    mensaje = modulo_model.actualizar_modulo()

    if "exitosamente" in mensaje:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Actualizar módulo",
            descripcion=f"Se actualizó el módulo ID: {modulo_id} - Nuevo nombre: {nombre}",
            usuario_id=usuario_id,
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400


@modulos_blueprint.route("/api/modulos/<modulo_id>", methods=["DELETE"])
@jwt_required
@solo_roles(['admin'])
def api_eliminar_modulo(modulo_id):
    modulo_model = Modulo(id=modulo_id)
    mensaje = modulo_model.eliminar_modulo()

    if "exitosamente" in mensaje:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Eliminar módulo",
            descripcion=f"Se eliminó el módulo ID: {modulo_id}",
            usuario_id=usuario_id,
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400