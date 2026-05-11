from flask import Blueprint, jsonify, render_template, request

from app.models.gestion_usuarios import GestionUsuarios
from app.utils.decorators import jwt_required

usuarios_blueprint = Blueprint("usuarios", __name__)


def _respuesta_error(mensaje, status=400):
    return jsonify({"success": False, "error": mensaje}), status


def _bool(valor):
    if isinstance(valor, bool):
        return valor
    if valor is None:
        return 0
    if isinstance(valor, (int, float)):
        return 1 if int(valor) != 0 else 0
    texto = str(valor).strip().lower()
    return 1 if texto in {"1", "true", "on", "si", "yes"} else 0


@usuarios_blueprint.route("/usuarios", methods=["GET"])
@jwt_required
def pagina_usuarios():
    return render_template(
        "usuarios.html",
        show_navbar=True,
        show_notifications=True,
        active_page="usuarios",
    )


@usuarios_blueprint.route("/api/usuarios", methods=["GET"])
@jwt_required
def listar_usuarios():
    modelo = GestionUsuarios()
    datos = modelo.listar_usuarios() or []
    return jsonify({"success": True, "usuarios": datos})


@usuarios_blueprint.route("/api/usuarios", methods=["POST"])
@jwt_required
def crear_usuario():
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    cedula_personal = datos.get("cedula_personal")
    password = (datos.get("password") or "").strip()
    rol_id = datos.get("rol_id")
    foto_perfil = (datos.get("foto_perfil") or None)

    if not nombre or not cedula_personal or not password or not rol_id:
        return _respuesta_error("Nombre, cedula, password y rol son obligatorios.")

    modelo = GestionUsuarios()
    try:
        nuevo_id = modelo.crear_usuario(nombre, int(cedula_personal), password, int(rol_id), foto_perfil)
        return jsonify({"success": True, "message": "Usuario creado.", "id": nuevo_id})
    except Exception as error:
        return _respuesta_error(str(error))


@usuarios_blueprint.route("/api/usuarios/<usuario_id>", methods=["PUT"])
@jwt_required
def actualizar_usuario(usuario_id):
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    cedula_personal = datos.get("cedula_personal")
    password = (datos.get("password") or "").strip()
    rol_id = datos.get("rol_id")
    foto_perfil = (datos.get("foto_perfil") or None)

    if not nombre or not cedula_personal or not rol_id:
        return _respuesta_error("Nombre, cedula y rol son obligatorios.")

    modelo = GestionUsuarios()
    try:
        if password:
            resultado = modelo.actualizar_usuario_con_password(
                usuario_id,
                nombre,
                int(cedula_personal),
                password,
                int(rol_id),
                foto_perfil,
            )
        else:
            resultado = modelo.actualizar_usuario(
                usuario_id,
                nombre,
                int(cedula_personal),
                int(rol_id),
                foto_perfil,
            )
        return jsonify({"success": True, "message": "Usuario actualizado.", "result": resultado})
    except Exception as error:
        return _respuesta_error(str(error))


@usuarios_blueprint.route("/api/usuarios/<usuario_id>", methods=["DELETE"])
@jwt_required
def eliminar_usuario(usuario_id):
    modelo = GestionUsuarios()
    try:
        modelo.eliminar_usuario(usuario_id)
        return jsonify({"success": True, "message": "Usuario eliminado."})
    except Exception as error:
        return _respuesta_error(str(error))


@usuarios_blueprint.route("/api/roles", methods=["GET"])
@jwt_required
def listar_roles():
    modelo = GestionUsuarios()
    datos = modelo.listar_roles() or []
    return jsonify({"success": True, "roles": datos})


@usuarios_blueprint.route("/api/roles", methods=["POST"])
@jwt_required
def crear_rol():
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    descripcion = (datos.get("descripcion") or "").strip()

    if not nombre:
        return _respuesta_error("El nombre del rol es obligatorio.")

    modelo = GestionUsuarios()
    try:
        nuevo_id = modelo.crear_rol(nombre, descripcion)
        return jsonify({"success": True, "message": "Rol creado.", "id": nuevo_id})
    except Exception as error:
        return _respuesta_error(str(error))


@usuarios_blueprint.route("/api/roles/<int:rol_id>", methods=["PUT"])
@jwt_required
def actualizar_rol(rol_id):
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    descripcion = (datos.get("descripcion") or "").strip()

    if not nombre:
        return _respuesta_error("El nombre del rol es obligatorio.")

    modelo = GestionUsuarios()
    try:
        resultado = modelo.actualizar_rol(rol_id, nombre, descripcion)
        return jsonify({"success": True, "message": "Rol actualizado.", "result": resultado})
    except Exception as error:
        return _respuesta_error(str(error))


@usuarios_blueprint.route("/api/roles/<int:rol_id>", methods=["DELETE"])
@jwt_required
def eliminar_rol(rol_id):
    modelo = GestionUsuarios()
    try:
        modelo.eliminar_rol(rol_id)
        return jsonify({"success": True, "message": "Rol eliminado."})
    except Exception as error:
        return _respuesta_error(str(error))


@usuarios_blueprint.route("/api/modulos", methods=["GET"])
@jwt_required
def listar_modulos():
    modelo = GestionUsuarios()
    datos = modelo.listar_modulos() or []
    return jsonify({"success": True, "modulos": datos})


@usuarios_blueprint.route("/api/modulos", methods=["POST"])
@jwt_required
def crear_modulo():
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    descripcion = (datos.get("descripcion") or "").strip()

    if not nombre:
        return _respuesta_error("El nombre del modulo es obligatorio.")

    modelo = GestionUsuarios()
    try:
        nuevo_id = modelo.crear_modulo(nombre, descripcion)
        return jsonify({"success": True, "message": "Modulo creado.", "id": nuevo_id})
    except Exception as error:
        return _respuesta_error(str(error))


@usuarios_blueprint.route("/api/modulos/<int:modulo_id>", methods=["PUT"])
@jwt_required
def actualizar_modulo(modulo_id):
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    descripcion = (datos.get("descripcion") or "").strip()

    if not nombre:
        return _respuesta_error("El nombre del modulo es obligatorio.")

    modelo = GestionUsuarios()
    try:
        resultado = modelo.actualizar_modulo(modulo_id, nombre, descripcion)
        return jsonify({"success": True, "message": "Modulo actualizado.", "result": resultado})
    except Exception as error:
        return _respuesta_error(str(error))


@usuarios_blueprint.route("/api/modulos/<int:modulo_id>", methods=["DELETE"])
@jwt_required
def eliminar_modulo(modulo_id):
    modelo = GestionUsuarios()
    try:
        modelo.eliminar_modulo(modulo_id)
        return jsonify({"success": True, "message": "Modulo eliminado."})
    except Exception as error:
        return _respuesta_error(str(error))


@usuarios_blueprint.route("/api/permisos", methods=["GET"])
@jwt_required
def listar_permisos():
    modelo = GestionUsuarios()
    datos = modelo.listar_permisos() or []
    return jsonify({"success": True, "permisos": datos})


@usuarios_blueprint.route("/api/permisos", methods=["POST"])
@jwt_required
def guardar_permiso():
    datos = request.get_json(silent=True) or {}
    rol_id = datos.get("rol_id")
    modulo_id = datos.get("modulo_id")

    if not rol_id or not modulo_id:
        return _respuesta_error("Rol y modulo son obligatorios.")

    modelo = GestionUsuarios()
    try:
        resultado = modelo.guardar_permiso(
            int(rol_id),
            int(modulo_id),
            _bool(datos.get("registrar")),
            _bool(datos.get("modificar")),
            _bool(datos.get("eliminar")),
        )
        return jsonify({"success": True, "message": "Permiso guardado.", "result": resultado})
    except Exception as error:
        return _respuesta_error(str(error))


@usuarios_blueprint.route("/api/permisos", methods=["DELETE"])
@jwt_required
def eliminar_permiso():
    datos = request.get_json(silent=True) or {}
    rol_id = datos.get("rol_id")
    modulo_id = datos.get("modulo_id")

    if not rol_id or not modulo_id:
        return _respuesta_error("Rol y modulo son obligatorios.")

    modelo = GestionUsuarios()
    try:
        modelo.eliminar_permiso(int(rol_id), int(modulo_id))
        return jsonify({"success": True, "message": "Permiso eliminado."})
    except Exception as error:
        return _respuesta_error(str(error))
