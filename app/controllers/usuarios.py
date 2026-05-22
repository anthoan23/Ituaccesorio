import os
import uuid

from flask import Blueprint, jsonify, render_template, request, g, current_app
import mysql.connector
from werkzeug.utils import secure_filename

from app.models.usuarios import Usuarios
from app.utils.decorators import jwt_required
from app.utils.jwt_utils import create_token

usuarios_blueprint = Blueprint("usuarios", __name__)


def _respuesta_error(mensaje, status=400):
    return jsonify({"success": False, "error": mensaje}), status


def _respuesta_por_excepcion(error):
    if isinstance(error, (ValueError, TypeError)):
        return _respuesta_error("Hay datos invalidos en la solicitud.", 400)

    if isinstance(error, mysql.connector.IntegrityError):
        errno = getattr(error, "errno", None)
        mensajes = {
            1062: "Ya existe un registro con esos datos.",
            1048: "Hay campos obligatorios sin completar.",
            1451: "No se puede eliminar porque el registro esta siendo usado.",
            1452: "La relacion indicada no existe o no es valida.",
        }
        return _respuesta_error(mensajes.get(errno, "No se pudo guardar la informacion por una restriccion de datos."), 409)

    if isinstance(error, mysql.connector.DataError):
        return _respuesta_error("El formato o tamaño de los datos no es valido.", 400)

    if isinstance(error, mysql.connector.ProgrammingError):
        return _respuesta_error("Ocurrio un error interno al procesar la solicitud.", 500)

    if isinstance(error, mysql.connector.OperationalError):
        return _respuesta_error("No fue posible conectar con la base de datos en este momento.", 503)

    if isinstance(error, mysql.connector.DatabaseError):
        return _respuesta_error("Se produjo un error al consultar la base de datos.", 500)

    return _respuesta_error("Ocurrio un error inesperado.", 500)


def _bool(valor):
    if isinstance(valor, bool):
        return valor
    if valor is None:
        return 0
    if isinstance(valor, (int, float)):
        return 1 if int(valor) != 0 else 0
    texto = str(valor).strip().lower()
    return 1 if texto in {"1", "true", "on", "si", "yes"} else 0


def _usuario_actual():
    usuario = getattr(g, "user", None)
    if not usuario:
        return {}
    if isinstance(usuario, dict):
        return usuario
    return {
        "usuario_id": getattr(usuario, "usuario_id", None),
        "usuario_nombre": getattr(usuario, "usuario_nombre", None),
        # Exponer la cédula bajo la clave unificada `cedula`
        "cedula": getattr(usuario, "cedula", None) or getattr(usuario, "cedula_personal", None),
        "cedula_personal": getattr(usuario, "cedula_personal", None),
        "rol_id": getattr(usuario, "rol_id", None),
        "nombre_rol": getattr(usuario, "nombre_rol", None),
        "foto_perfil": getattr(usuario, "foto_perfil", None),
        "perfil_completo": getattr(usuario, "perfil_completo", True),
    }


def _datos_solicitud():
    datos = request.get_json(silent=True)
    if datos is not None:
        return datos
    return request.form.to_dict()


def _guardar_foto_perfil(archivo):
    if not archivo or not getattr(archivo, "filename", ""):
        return None

    nombre_seguro = secure_filename(archivo.filename)
    _, extension = os.path.splitext(nombre_seguro)
    extension = extension.lower()[:10]
    nombre_final = f"{uuid.uuid4().hex}{extension}"

    carpeta_destino = os.path.join(current_app.static_folder, "img", "perfil")
    os.makedirs(carpeta_destino, exist_ok=True)

    ruta_fisica = os.path.join(carpeta_destino, nombre_final)
    archivo.save(ruta_fisica)
    return f"/static/img/perfil/{nombre_final}"


def _actualizar_cookie_usuario(resp, usuario_actual, usuario_db):
    payload = {
        "usuario_id": usuario_db.get("id"),
        "usuario_nombre": usuario_db.get("nombre"),
        "cedula": usuario_db.get("cedula_personal"),
        "rol_id": usuario_db.get("rol_id"),
        "nombre_rol": usuario_db.get("rol_nombre"),
        "foto_perfil": usuario_db.get("foto_perfil"),
        "perfil_completo": bool((usuario_actual or {}).get("perfil_completo", True)),
    }
    token = create_token(payload)
    resp.set_cookie("access_token", token, httponly=True, samesite="Lax", secure=False, path="/")
    return resp


@usuarios_blueprint.route("/usuarios", methods=["GET"])
@jwt_required
def pagina_usuarios():
    return render_template(
        "usuarios.html",
        show_navbar=True,
        show_notifications=True,
        active_page="usuarios",
        current_user=_usuario_actual(),
    )


@usuarios_blueprint.route("/api/usuarios", methods=["GET"])
@jwt_required
def listar_usuarios():
    modelo = Usuarios()
    datos = modelo.listar_usuarios() or []
    return jsonify({"success": True, "usuarios": datos})


@usuarios_blueprint.route("/api/usuarios/empleados", methods=["GET"])
@jwt_required
def listar_empleados():
    modelo = Usuarios()
    datos = modelo.listar_empleados() or []
    return jsonify({"success": True, "empleados": datos})


@usuarios_blueprint.route("/api/usuarios/mi-perfil", methods=["GET"])
@jwt_required
def obtener_mi_perfil():
    usuario_actual = _usuario_actual()
    usuario_id = usuario_actual.get("usuario_id")
    if not usuario_id:
        return _respuesta_error("No se pudo identificar al usuario actual.", 401)

    modelo = Usuarios()
    usuario = modelo.obtener_usuario_por_id(usuario_id)
    if not usuario:
        return _respuesta_error("El usuario actual no existe.", 404)

    return jsonify({"success": True, "usuario": usuario})


@usuarios_blueprint.route("/api/usuarios/mi-perfil", methods=["PUT"])
@jwt_required
def actualizar_mi_perfil():
    usuario_actual = _usuario_actual()
    usuario_id = usuario_actual.get("usuario_id")
    if not usuario_id:
        return _respuesta_error("No se pudo identificar al usuario actual.", 401)

    datos = _datos_solicitud() or {}
    nombre = (datos.get("nombre") or "").strip()
    password = (datos.get("password") or "").strip()

    if not nombre:
        return _respuesta_error("El nombre es obligatorio.")

    modelo = Usuarios()
    usuario_db_actual = modelo.obtener_usuario_por_id(usuario_id)
    if not usuario_db_actual:
        return _respuesta_error("El usuario actual no existe.", 404)

    foto_perfil = _guardar_foto_perfil(request.files.get("foto_perfil")) or usuario_db_actual.get("foto_perfil")

    try:
        modelo.actualizar_perfil_actual(usuario_id, nombre, password if password else None, foto_perfil)
        usuario_actualizado = modelo.obtener_usuario_por_id(usuario_id)
        if not usuario_actualizado:
            return _respuesta_error("No se pudo actualizar el perfil.", 500)

        resp = jsonify({"success": True, "message": "Perfil actualizado.", "usuario": usuario_actualizado})
        return _actualizar_cookie_usuario(resp, usuario_actual, usuario_actualizado)
    except Exception as error:
        return _respuesta_por_excepcion(error)


@usuarios_blueprint.route("/api/usuarios", methods=["POST"])
@jwt_required
def crear_usuario():
    datos = _datos_solicitud() or {}
    nombre = (datos.get("nombre") or "").strip()
    cedula_personal = datos.get("cedula") or datos.get("cedula_personal")
    password = (datos.get("password") or "").strip()
    rol_id = datos.get("rol_id")
    foto_perfil = _guardar_foto_perfil(request.files.get("foto_perfil")) or (datos.get("foto_perfil_actual") or datos.get("foto_perfil") or None)

    if not nombre or not cedula_personal or not password or not rol_id:
        return _respuesta_error("Nombre, cedula, password y rol son obligatorios.")

    modelo = Usuarios()
    if not modelo.verificar_empleado(cedula_personal):
        return _respuesta_error("La cedula no pertenece a un empleado registrado.")
    try:
        nuevo_id = modelo.crear_usuario(nombre, int(cedula_personal), password, int(rol_id), foto_perfil)
        if not nuevo_id:
            return _respuesta_error("No se pudo crear el usuario.")
        return jsonify({"success": True, "message": "Usuario creado.", "id": nuevo_id})
    except Exception as error:
        return _respuesta_por_excepcion(error)


@usuarios_blueprint.route("/api/usuarios/<usuario_id>", methods=["PUT"])
@jwt_required
def actualizar_usuario(usuario_id):
    datos = _datos_solicitud() or {}
    nombre = (datos.get("nombre") or "").strip()
    cedula_personal = datos.get("cedula") or datos.get("cedula_personal")
    password = (datos.get("password") or "").strip()
    rol_id = datos.get("rol_id")
    foto_perfil = _guardar_foto_perfil(request.files.get("foto_perfil")) or (datos.get("foto_perfil_actual") or datos.get("foto_perfil") or None)

    if not nombre or not cedula_personal or not rol_id:
        return _respuesta_error("Nombre, cedula y rol son obligatorios.")

    modelo = Usuarios()
    if not modelo.verificar_empleado(cedula_personal):
        return _respuesta_error("La cedula no pertenece a un empleado registrado.")
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
        return _respuesta_por_excepcion(error)


@usuarios_blueprint.route("/api/usuarios/<usuario_id>", methods=["DELETE"])
@jwt_required
def eliminar_usuario(usuario_id):
    modelo = Usuarios()
    try:
        usuario_actual = _usuario_actual()
        usuario_objetivo = modelo.obtener_usuario_por_id(usuario_id)

        if not usuario_objetivo:
            return _respuesta_error("El usuario no existe.", 404)

        if str(usuario_actual.get("usuario_id", "")).strip() == str(usuario_id).strip():
            return _respuesta_error("No puedes eliminar tu propio usuario.", 403)

        rol_actual = str(usuario_actual.get("nombre_rol", "")).strip().lower()
        rol_objetivo = str((usuario_objetivo or {}).get("rol_nombre", "")).strip().lower()

        if rol_objetivo == "admin" and rol_actual != "admin":
            return _respuesta_error("Solo otro admin puede eliminar este usuario.", 403)

        modelo.eliminar_usuario(usuario_id)
        return jsonify({"success": True, "message": "Usuario eliminado."})
    except Exception as error:
        return _respuesta_por_excepcion(error)


@usuarios_blueprint.route("/api/roles", methods=["GET"])
@jwt_required
def listar_roles():
    modelo = Usuarios()
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

    modelo = Usuarios()
    try:
        nuevo_id = modelo.crear_rol(nombre, descripcion)
        return jsonify({"success": True, "message": "Rol creado.", "id": nuevo_id})
    except Exception as error:
        return _respuesta_por_excepcion(error)


@usuarios_blueprint.route("/api/roles/<int:rol_id>", methods=["PUT"])
@jwt_required
def actualizar_rol(rol_id):
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    descripcion = (datos.get("descripcion") or "").strip()

    if not nombre:
        return _respuesta_error("El nombre del rol es obligatorio.")

    modelo = Usuarios()
    try:
        resultado = modelo.actualizar_rol(rol_id, nombre, descripcion)
        return jsonify({"success": True, "message": "Rol actualizado.", "result": resultado})
    except Exception as error:
        return _respuesta_por_excepcion(error)


@usuarios_blueprint.route("/api/roles/<int:rol_id>", methods=["DELETE"])
@jwt_required
def eliminar_rol(rol_id):
    modelo = Usuarios()
    try:
        roles = modelo.listar_roles() or []
        rol = next((item for item in roles if int(item.get("id", 0)) == int(rol_id)), None)
        nombre_rol = (rol or {}).get("nombre", "")
        if str(nombre_rol).strip().lower() in {"admin", "cliente"}:
            return _respuesta_error("El rol Admin y Cliente no se pueden eliminar.", 403)

        modelo.eliminar_rol(rol_id)
        return jsonify({"success": True, "message": "Rol eliminado."})
    except Exception as error:
        return _respuesta_por_excepcion(error)


@usuarios_blueprint.route("/api/modulos", methods=["GET"])
@jwt_required
def listar_modulos():
    modelo = Usuarios()
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

    modelo = Usuarios()
    try:
        nuevo_id = modelo.crear_modulo(nombre, descripcion)
        return jsonify({"success": True, "message": "Modulo creado.", "id": nuevo_id})
    except Exception as error:
        return _respuesta_por_excepcion(error)


@usuarios_blueprint.route("/api/modulos/<int:modulo_id>", methods=["PUT"])
@jwt_required
def actualizar_modulo(modulo_id):
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    descripcion = (datos.get("descripcion") or "").strip()

    if not nombre:
        return _respuesta_error("El nombre del modulo es obligatorio.")

    modelo = Usuarios()
    try:
        resultado = modelo.actualizar_modulo(modulo_id, nombre, descripcion)
        return jsonify({"success": True, "message": "Modulo actualizado.", "result": resultado})
    except Exception as error:
        return _respuesta_por_excepcion(error)


@usuarios_blueprint.route("/api/modulos/<int:modulo_id>", methods=["DELETE"])
@jwt_required
def eliminar_modulo(modulo_id):
    modelo = Usuarios()
    try:
        modelo.eliminar_modulo(modulo_id)
        return jsonify({"success": True, "message": "Modulo eliminado."})
    except Exception as error:
        return _respuesta_por_excepcion(error)


@usuarios_blueprint.route("/api/permisos", methods=["GET"])
@jwt_required
def listar_permisos():
    modelo = Usuarios()
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

    modelo = Usuarios()
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
        return _respuesta_por_excepcion(error)


@usuarios_blueprint.route("/api/permisos", methods=["DELETE"])
@jwt_required
def eliminar_permiso():
    datos = request.get_json(silent=True) or {}
    rol_id = datos.get("rol_id")
    modulo_id = datos.get("modulo_id")

    if not rol_id or not modulo_id:
        return _respuesta_error("Rol y modulo son obligatorios.")

    modelo = Usuarios()
    try:
        modelo.eliminar_permiso(int(rol_id), int(modulo_id))
        return jsonify({"success": True, "message": "Permiso eliminado."})
    except Exception as error:
        return _respuesta_por_excepcion(error)
