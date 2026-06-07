from flask import Blueprint, jsonify, request, g
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.bitacora import registrar_en_bitacora
from app.models.roles import Rol

roles_blueprint = Blueprint("roles", __name__)


def _usuario_actual():
    """Obtiene el ID del usuario actual"""
    user = getattr(g, 'user', None)
    if not user:
        return "SYSTEM"
    if isinstance(user, dict):
        return str(user.get("usuario_id") or user.get("id") or "SYSTEM")
    return str(getattr(user, "usuario_id", None) or getattr(user, "id", None) or "SYSTEM")


@roles_blueprint.route("/api/roles", methods=["GET"])
@jwt_required
@tiene_permiso('Usuarios', 'consultar')
def api_listar_roles():
    rol_model = Rol()
    roles = rol_model.listar_roles()
    return jsonify({"success": True, "roles": roles or []})


@roles_blueprint.route("/api/roles", methods=["POST"])
@jwt_required
@tiene_permiso('Usuarios', 'registrar')
def api_crear_rol():
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre", "").strip()
    descripcion = data.get("descripcion", "").strip()

    if not nombre:
        return jsonify({"success": False, "error": "El nombre del rol es obligatorio."}), 400

    rol_model = Rol(nombre=nombre, descripcion=descripcion)
    mensaje = rol_model.agregar_rol()

    if "exitosamente" in mensaje:
        registrar_en_bitacora(
            accion="Crear rol",
            descripcion=f"Se creó el rol: {nombre}",
            usuario_id=_usuario_actual(),
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje, "id": rol_model.id}), 201

    return jsonify({"success": False, "error": mensaje}), 400


@roles_blueprint.route("/api/roles/<rol_id>", methods=["PUT"])
@jwt_required
@tiene_permiso('Usuarios', 'modificar')
def api_actualizar_rol(rol_id):
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre", "").strip()
    descripcion = data.get("descripcion", "").strip()

    if not nombre:
        return jsonify({"success": False, "error": "El nombre del rol es obligatorio."}), 400

    rol_model = Rol(id=rol_id, nombre=nombre, descripcion=descripcion)
    mensaje = rol_model.actualizar_rol()

    if "exitosamente" in mensaje:
        registrar_en_bitacora(
            accion="Actualizar rol",
            descripcion=f"Se actualizó el rol ID: {rol_id} - Nuevo nombre: {nombre}",
            usuario_id=_usuario_actual(),
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400


@roles_blueprint.route("/api/roles/<rol_id>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Usuarios', 'eliminar')
def api_eliminar_rol(rol_id):
    rol_model = Rol(id=rol_id)
    mensaje = rol_model.eliminar_rol()

    if "exitosamente" in mensaje:
        registrar_en_bitacora(
            accion="Eliminar rol",
            descripcion=f"Se eliminó el rol ID: {rol_id}",
            usuario_id=_usuario_actual(),
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400