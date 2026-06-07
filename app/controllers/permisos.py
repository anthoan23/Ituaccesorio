from flask import Blueprint, jsonify, request, g
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.bitacora import registrar_en_bitacora
from app.models.permisos import Permiso
from app.models.roles import Rol
from app.models.modulos import Modulo

permisos_blueprint = Blueprint("permisos", __name__)


def _usuario_actual():
    """Obtiene el ID del usuario actual"""
    user = getattr(g, 'user', None)
    if not user:
        return "SYSTEM"
    if isinstance(user, dict):
        return str(user.get("usuario_id") or user.get("id") or "SYSTEM")
    return str(getattr(user, "usuario_id", None) or getattr(user, "id", None) or "SYSTEM")


def _usuario_actual_datos():
    usuario = getattr(g, "user", None)
    if not usuario:
        return {}
    if isinstance(usuario, dict):
        return usuario
    return {
        "usuario_id": getattr(usuario, "usuario_id", None),
        "usuario_nombre": getattr(usuario, "usuario_nombre", None),
        "cedula": getattr(usuario, "cedula", None),
        "rol_id": getattr(usuario, "rol_id", None),
        "nombre_rol": getattr(usuario, "nombre_rol", None),
        "foto_perfil": getattr(usuario, "foto_perfil", None),
    }


def _bool(valor):
    if isinstance(valor, bool):
        return valor
    if valor is None:
        return 0
    if isinstance(valor, (int, float)):
        return 1 if int(valor) != 0 else 0
    texto = str(valor).strip().lower()
    return 1 if texto in {"1", "true", "on", "si", "yes"} else 0


@permisos_blueprint.route("/api/permisos/rol/<rol_id>", methods=["GET"])
@jwt_required
@tiene_permiso('Usuarios', 'consultar')
def api_obtener_permisos_por_rol(rol_id):
    """Obtiene todos los permisos de un rol específico aplicando la regla de negocio"""
    # Verificar que el rol existe
    rol_model = Rol(id=rol_id)
    if not rol_model.verificar_rol_por_id():
        return jsonify({"success": False, "error": f"El rol con ID {rol_id} no existe."}), 404

    permiso_model = Permiso(rol_id=rol_id)
    permisos = permiso_model.listar_permisos_completos_por_rol()

    return jsonify({
        "success": True,
        "rol_id": rol_id,
        "permisos": permisos or []
    })


@permisos_blueprint.route("/api/permisos/rol/<rol_id>", methods=["PUT"])
@jwt_required
@tiene_permiso('Usuarios', 'modificar')
def api_actualizar_permisos_rol(rol_id):
    """Actualiza todos los permisos de un rol específico"""
    data = request.get_json(silent=True) or {}
    permisos = data.get("permisos", [])

    if not permisos:
        return jsonify({"success": False, "error": "Se requiere la lista de permisos."}), 400

    # Verificar que el rol existe
    rol_model = Rol(id=rol_id)
    rol_existente = rol_model.obtener_rol_por_id()

    if not rol_existente:
        return jsonify({"success": False, "error": f"El rol con ID {rol_id} no existe."}), 404

    # Verificar permisos para modificar admin
    usuario_actual_rol = _usuario_actual_datos().get("nombre_rol", "").lower()
    nombre_rol = rol_existente.get("nombre", "").lower()

    if nombre_rol == "admin" and usuario_actual_rol != "admin":
        return jsonify({"success": False, "error": "No tienes permisos para modificar los permisos del rol Admin."}), 403

    # Preparar datos para guardado masivo
    permisos_data = []
    for permiso in permisos:
        modulo_id = permiso.get("modulo_id")
        if modulo_id:
            permisos_data.append({
                "modulo_id": modulo_id,
                "registrar": _bool(permiso.get("registrar", False)),
                "modificar": _bool(permiso.get("modificar", False)),
                "eliminar": _bool(permiso.get("eliminar", False))
            })

    if not permisos_data:
        return jsonify({"success": False, "error": "No hay permisos válidos para guardar."}), 400

    permiso_model = Permiso()
    exitosos, errores = permiso_model.guardar_permisos_masivos(rol_id, permisos_data)

    if errores:
        return jsonify({
            "success": False,
            "error": "Algunos permisos no se pudieron guardar.",
            "detalles": errores
        }), 500

    registrar_en_bitacora(
        accion="Actualizar permisos de rol",
        descripcion=f"Se actualizaron {exitosos} permisos para el rol ID: {rol_id} - {rol_existente.get('nombre', 'N/A')}",
        usuario_id=_usuario_actual(),
        modulo_nombre="Usuarios"
    )

    return jsonify({
        "success": True,
        "message": "Permisos actualizados correctamente.",
        "actualizados": exitosos
    })


@permisos_blueprint.route("/api/permisos/rol/<rol_id>/modulo/<modulo_id>", methods=["GET"])
@jwt_required
@tiene_permiso('Usuarios', 'consultar')
def api_obtener_permiso_especifico(rol_id, modulo_id):
    """Obtiene un permiso específico de un rol para un módulo aplicando la regla de negocio"""
    # Verificar que el rol existe
    rol_model = Rol(id=rol_id)
    if not rol_model.verificar_rol_por_id():
        return jsonify({"success": False, "error": f"El rol con ID {rol_id} no existe."}), 404

    # Verificar que el módulo existe
    modulo_model = Modulo(id=modulo_id)
    modulo = modulo_model.obtener_modulo_por_id()
    if not modulo:
        return jsonify({"success": False, "error": f"El módulo con ID {modulo_id} no existe."}), 404

    permiso_model = Permiso(rol_id=rol_id, modulo_id=modulo_id)
    permisos = permiso_model.listar_permisos_completos_por_rol()
    
    # Buscar el permiso específico
    permiso = None
    for p in (permisos or []):
        if p["modulo_id"] == int(modulo_id):
            permiso = p
            break

    return jsonify({
        "success": True,
        "permiso": {
            "rol_id": rol_id,
            "modulo_id": modulo_id,
            "modulo_nombre": modulo["nombre"],
            "consultar": permiso.get("consultar", False) if permiso else False,
            "registrar": permiso.get("registrar", False) if permiso else False,
            "modificar": permiso.get("modificar", False) if permiso else False,
            "eliminar": permiso.get("eliminar", False) if permiso else False,
        }
    })


@permisos_blueprint.route("/api/usuarios/mis-permisos", methods=["GET"])
@jwt_required
def api_obtener_mis_permisos():
    """Obtiene todos los permisos del usuario actual aplicando la regla de negocio"""
    usuario_id = _usuario_actual()
    if usuario_id == "SYSTEM":
        return jsonify({"success": False, "error": "No se pudo identificar al usuario."}), 401

    permiso_model = Permiso()
    permisos = permiso_model.obtener_permisos_usuario(usuario_id)

    return jsonify({"success": True, "permisos": permisos or []})