from flask import Blueprint, jsonify, render_template, request, redirect, url_for, make_response, g
import os
import requests
import mysql.connector

from app.models.clientes import GestionClientes
from app.models.usuarios import Usuarios
from app.utils.decorators import jwt_required
from app.utils.jwt_utils import create_token

login_blueprint = Blueprint("login", __name__)


def _respuesta_error_por_excepcion(error):
    if isinstance(error, mysql.connector.IntegrityError):
        errno = getattr(error, "errno", None)
        if errno == 1062:
            return jsonify({"success": False, "error": "Ya existe un registro con esos datos."}), 409
        return jsonify({"success": False, "error": "No se pudo guardar la información por una restricción de datos."}), 409
    if isinstance(error, (ValueError, TypeError)):
        return jsonify({"success": False, "error": "Hay datos inválidos en la solicitud."}), 400
    return jsonify({"success": False, "error": "Ocurrió un error inesperado."}), 500


def _es_rol_cliente(nombre_rol):
    return str(nombre_rol or "").strip().lower() == "cliente"


def _perfil_cliente_completo(cedula):
    if not cedula:
        return False
    modelo_clientes = GestionClientes()
    return bool(modelo_clientes.obtener_cliente_por_id(int(cedula)))


def _validar_recaptcha(token, remote_ip):
    secret = os.getenv("RECAPTCHA_SECRET_KEY")
    if not secret:
        return False, "Captcha no configurado."
    if not token:
        return False, "Completa el captcha para continuar."
    payload = {"secret": secret, "response": token}
    if remote_ip:
        payload["remoteip"] = remote_ip
    try:
        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data=payload,
            timeout=5
        )
        data = response.json()
    except requests.RequestException:
        return False, "No se pudo validar el captcha. Intenta nuevamente."
    if data.get("success"):
        return True, ""
    return False, "Captcha inválido. Intenta nuevamente."


@login_blueprint.route("/login", methods=["GET"])
def pagina_login():
    # Servir la vista de login para teléfono en la ruta /login
    return render_template(
        "login_phone.html",
        recaptcha_site_key=os.getenv("RECAPTCHA_SITE_KEY", "")
    )

@login_blueprint.route("/api/login", methods=["POST"])
def validar_login():
    datos = request.get_json(silent=True) or {}
    modelo = Usuarios()

    try:
        recaptcha_token = datos.get("recaptcha")
        recaptcha_ok, recaptcha_error = _validar_recaptcha(recaptcha_token, request.remote_addr)
        if not recaptcha_ok:
            status = 500 if recaptcha_error == "Captcha no configurado." else 400
            return jsonify({"success": False, "error": recaptcha_error}), status

        nombre = datos.get("nombre")
        password = datos.get("password")

        if not nombre or not password:
            return jsonify({"success": False, "error": "El nombre y la contraseña son obligatorios."}), 400

        resultados = modelo.validar(nombre, password)
        if resultados:
            usuario = resultados[0]
            perfil_completo = True
            if _es_rol_cliente(usuario.get("nombre_rol")):
                perfil_completo = _perfil_cliente_completo(usuario.get("cedula_personal"))
            # Create JWT payload
            payload = {
                "usuario_id": usuario.get("id"),
                "usuario_nombre": usuario.get("nombre"),
                "cedula": usuario.get("cedula_personal"),
                "rol_id": usuario.get("rol_id"),
                "nombre_rol": usuario.get("nombre_rol"),
                "foto_perfil": usuario.get("foto_perfil"),
                "perfil_completo": perfil_completo,
            }
            token = create_token(payload)
            resp = make_response(
                jsonify(
                    {
                        "success": True,
                        "message": "Inicio de sesión exitoso.",
                        "require_profile_completion": _es_rol_cliente(usuario.get("nombre_rol")) and not perfil_completo,
                    }
                )
            )
            resp.set_cookie('access_token', token, httponly=True, samesite='Lax', secure=False, path='/')
            return resp
        else:
            return jsonify({"success": False, "error": "Credenciales inválidas."}), 401
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400   


@login_blueprint.route("/api/registro/cliente/paso-1", methods=["POST"])
def registro_cliente_paso_1():
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    cedula = (datos.get("cedula") or "").strip()
    password = (datos.get("password") or "").strip()

    if not nombre or not cedula or not password:
        return jsonify({"success": False, "error": "Usuario, cédula y contraseña son obligatorios."}), 400

    modelo = Usuarios()
    rol_cliente = modelo.obtener_rol_por_nombre("Cliente")
    if not rol_cliente:
        return jsonify({"success": False, "error": "No existe el rol Cliente configurado en el sistema."}), 500

    try:
        cedula_num = int(cedula)
        usuario_id = modelo.crear_usuario(nombre, cedula_num, password, int(rol_cliente.get("id")))
        if not usuario_id:
            return jsonify({"success": False, "error": "No se pudo crear la cuenta."}), 500

        payload = {
            "usuario_id": usuario_id,
            "usuario_nombre": nombre,
            "cedula": cedula_num,
            "rol_id": int(rol_cliente.get("id")),
            "nombre_rol": rol_cliente.get("nombre"),
            "foto_perfil": None,
            "perfil_completo": False,
        }
        token = create_token(payload)
        resp = make_response(
            jsonify(
                {
                    "success": True,
                    "message": "Cuenta creada. Falta completar tu perfil.",
                    "require_profile_completion": True,
                }
            )
        )
        resp.set_cookie('access_token', token, httponly=True, samesite='Lax', secure=False, path='/')
        return resp
    except Exception as error:
        return _respuesta_error_por_excepcion(error)


@login_blueprint.route("/api/registro/cliente/paso-2", methods=["POST"])
@jwt_required
def registro_cliente_paso_2():
    usuario = getattr(g, "user", {}) or {}
    if not _es_rol_cliente(usuario.get("nombre_rol")):
        return jsonify({"success": False, "error": "Solo los usuarios con rol Cliente pueden completar este registro."}), 403

    cedula = usuario.get("cedula")
    if not cedula:
        return jsonify({"success": False, "error": "No se encontró la cédula activa para completar el perfil."}), 400

    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    apellido = (datos.get("apellido") or "").strip()
    celular = (datos.get("celular") or "").strip()
    correo = (datos.get("correo") or "").strip()
    direccion = (datos.get("direccion") or "").strip()
    tipo = "Regular"

    if not nombre or not apellido or not celular:
        return jsonify({"success": False, "error": "Nombre, apellido y celular son obligatorios."}), 400

    modelo_clientes = GestionClientes()
    existente = modelo_clientes.obtener_cliente_por_id(int(cedula))
    if existente:
        return jsonify({"success": False, "error": "El perfil del cliente ya está completo."}), 409

    try:
        modelo_clientes.crear_cliente_con_id(int(cedula), nombre, apellido, celular, correo, direccion, tipo)
        payload = {
            "usuario_id": usuario.get("usuario_id"),
            "usuario_nombre": usuario.get("usuario_nombre"),
            "cedula": int(cedula),
            "rol_id": usuario.get("rol_id"),
            "nombre_rol": usuario.get("nombre_rol"),
            "foto_perfil": usuario.get("foto_perfil"),
            "perfil_completo": True,
        }
        token = create_token(payload)
        resp = make_response(jsonify({"success": True, "message": "Perfil completado correctamente."}))
        resp.set_cookie('access_token', token, httponly=True, samesite='Lax', secure=False, path='/')
        return resp
    except Exception as error:
        return _respuesta_error_por_excepcion(error)



@login_blueprint.route('/logout', methods=['GET'])
def logout():
    resp = redirect(url_for('login.pagina_login'))
    resp.set_cookie('access_token', '', expires=0, path='/')
    return resp


