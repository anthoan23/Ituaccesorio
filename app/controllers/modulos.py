from flask import Blueprint, jsonify, request, g
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.bitacora import registrar_en_bitacora
from app.models.modulos import Modulo

modulos_blueprint = Blueprint("modulos", __name__)


def _usuario_actual():
    """Obtiene el ID del usuario actual"""
    user = getattr(g, 'user', None)
    if not user:
        return "SYSTEM"
    if isinstance(user, dict):
        return str(user.get("usuario_id") or user.get("id") or "SYSTEM")
    return str(getattr(user, "usuario_id", None) or getattr(user, "id", None) or "SYSTEM")


@modulos_blueprint.route("/api/modulos", methods=["GET"])
@jwt_required
@tiene_permiso('Usuarios', 'consultar')
def api_listar_modulos():
    modulo_model = Modulo()
    modulos = modulo_model.listar_modulos()
    return jsonify({"success": True, "modulos": modulos or []})


@modulos_blueprint.route("/api/modulos", methods=["POST"])
@jwt_required
@tiene_permiso('Usuarios', 'registrar')
def api_crear_modulo():
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre", "").strip()
    descripcion = data.get("descripcion", "").strip()

    if not nombre:
        return jsonify({"success": False, "error": "El nombre del módulo es obligatorio."}), 400

    modulo_model = Modulo(nombre=nombre, descripcion=descripcion)
    mensaje = modulo_model.agregar_modulo()

    if "exitosamente" in mensaje:
        registrar_en_bitacora(
            accion="Crear módulo",
            descripcion=f"Se creó el módulo: {nombre}",
            usuario_id=_usuario_actual(),
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje, "id": modulo_model.id}), 201

    return jsonify({"success": False, "error": mensaje}), 400


@modulos_blueprint.route("/api/modulos/<modulo_id>", methods=["PUT"])
@jwt_required
@tiene_permiso('Usuarios', 'modificar')
def api_actualizar_modulo(modulo_id):
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre", "").strip()
    descripcion = data.get("descripcion", "").strip()

    if not nombre:
        return jsonify({"success": False, "error": "El nombre del módulo es obligatorio."}), 400

    modulo_model = Modulo(id=modulo_id, nombre=nombre, descripcion=descripcion)
    mensaje = modulo_model.actualizar_modulo()

    if "exitosamente" in mensaje:
        registrar_en_bitacora(
            accion="Actualizar módulo",
            descripcion=f"Se actualizó el módulo ID: {modulo_id} - Nuevo nombre: {nombre}",
            usuario_id=_usuario_actual(),
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400


@modulos_blueprint.route("/api/modulos/<modulo_id>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Usuarios', 'eliminar')
def api_eliminar_modulo(modulo_id):
    modulo_model = Modulo(id=modulo_id)
    mensaje = modulo_model.eliminar_modulo()

    if "exitosamente" in mensaje:
        registrar_en_bitacora(
            accion="Eliminar módulo",
            descripcion=f"Se eliminó el módulo ID: {modulo_id}",
            usuario_id=_usuario_actual(),
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400