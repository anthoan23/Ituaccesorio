from flask import Blueprint, jsonify, request, g
from app.utils.decorators import jwt_required, solo_roles
from app.models.bitacora import registrar_en_bitacora
from app.models.roles import Rol

roles_blueprint = Blueprint("roles", __name__)


@roles_blueprint.route("/api/roles", methods=["GET"])
@jwt_required
@solo_roles(['admin'])
def api_listar_roles():
    rol_model = Rol()
    roles = rol_model.listar_roles()
    return jsonify({"success": True, "roles": roles or []})


@roles_blueprint.route("/api/roles", methods=["POST"])
@jwt_required
@solo_roles(['admin'])
def api_crear_rol():
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre", "").strip()
    descripcion = data.get("descripcion", "").strip()

    if not nombre:
        return jsonify({"success": False, "error": "El nombre del rol es obligatorio."}), 400

    rol_model = Rol(nombre=nombre, descripcion=descripcion)
    mensaje = rol_model.agregar_rol()

    if "exitosamente" in mensaje:
        # Obtener usuario desde g.user
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Crear rol",
            descripcion=f"Se creó el rol: {nombre}",
            usuario_id=usuario_id,
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje, "id": rol_model.id}), 201

    return jsonify({"success": False, "error": mensaje}), 400


@roles_blueprint.route("/api/roles/<rol_id>", methods=["PUT"])
@jwt_required
@solo_roles(['admin'])
def api_actualizar_rol(rol_id):
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre", "").strip()
    descripcion = data.get("descripcion", "").strip()

    if not nombre:
        return jsonify({"success": False, "error": "El nombre del rol es obligatorio."}), 400

    # Verificar que no se esté modificando el rol Admin
    rol_existente = Rol(id=rol_id)
    rol_data = rol_existente.obtener_rol_por_id()
    
    if rol_data and rol_data.get("nombre", "").lower() == "admin":
        usuario_actual = g.user.get("rol_nombre") if isinstance(g.user, dict) else getattr(g.user, "rol_nombre", "")
        if usuario_actual != "admin":
            return jsonify({"success": False, "error": "No se puede modificar el rol Admin."}), 403

    rol_model = Rol(id=rol_id, nombre=nombre, descripcion=descripcion)
    mensaje = rol_model.actualizar_rol()

    if "exitosamente" in mensaje:
        # Obtener usuario desde g.user
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Actualizar rol",
            descripcion=f"Se actualizó el rol ID: {rol_id} - Nuevo nombre: {nombre}",
            usuario_id=usuario_id,
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400


@roles_blueprint.route("/api/roles/<rol_id>", methods=["DELETE"])
@jwt_required
@solo_roles(['admin'])
def api_eliminar_rol(rol_id):
    # Verificar que no se esté eliminando el rol Admin
    rol_existente = Rol(id=rol_id)
    rol_data = rol_existente.obtener_rol_por_id()
    
    if rol_data and rol_data.get("nombre", "").lower() == "admin":
        return jsonify({"success": False, "error": "No se puede eliminar el rol Admin."}), 403

    rol_model = Rol(id=rol_id)
    mensaje = rol_model.eliminar_rol()

    if "exitosamente" in mensaje:
        # Obtener usuario desde g.user
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Eliminar rol",
            descripcion=f"Se eliminó el rol ID: {rol_id}",
            usuario_id=usuario_id,
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400