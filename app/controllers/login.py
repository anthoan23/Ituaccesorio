from flask import Blueprint, jsonify, render_template, request, redirect, url_for, make_response, g
import os
import re
import requests
import traceback
from app.models.login import LoginManager
from app.utils.decorators import jwt_required
from app.utils.jwt_utils import clear_auth_cookies, set_auth_cookies

login_blueprint = Blueprint("login", __name__)


def _respuesta_error_por_excepcion(error):
    """Maneja errores y devuelve respuesta JSON"""
    print(f"ERROR DETALLADO: {type(error).__name__}: {str(error)}")
    traceback.print_exc()
    
    if isinstance(error, mysql.connector.IntegrityError):
        errno = getattr(error, "errno", None)
        if errno == 1062:
            return jsonify({"success": False, "error": "Ya existe un registro con esos datos."}), 409
        return jsonify({"success": False, "error": "No se pudo guardar la información por una restricción de datos."}), 409
    if isinstance(error, (ValueError, TypeError)):
        return jsonify({"success": False, "error": f"Datos inválidos: {str(error)}"}), 400
    if isinstance(error, mysql.connector.Error):
        return jsonify({"success": False, "error": f"Error de base de datos: {str(error)}"}), 500
    
    return jsonify({"success": False, "error": f"Ocurrió un error inesperado: {str(error)}"}), 500


def _validar_recaptcha(token, remote_ip):
    """Valida el token de reCAPTCHA"""
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


def _es_rol_cliente(nombre_rol):
    """Verifica si el rol es cliente"""
    return str(nombre_rol or "").strip().lower() == "cliente"


@login_blueprint.route("/login", methods=["GET"])
def pagina_login():
    """Página de login"""
    return render_template(
        "login_phone.html",
        recaptcha_site_key=os.getenv("RECAPTCHA_SITE_KEY", "")
    )


@login_blueprint.route("/api/login", methods=["POST"])
def validar_login():
    """Endpoint de login"""
    try:
        datos = request.get_json(silent=True) or {}
        
        # Validar captcha
        recaptcha_token = datos.get("recaptcha")
        recaptcha_ok, recaptcha_error = _validar_recaptcha(recaptcha_token, request.remote_addr)
        if not recaptcha_ok:
            status = 500 if "no configurado" in recaptcha_error else 400
            return jsonify({"success": False, "error": recaptcha_error}), status

        nombre = datos.get("nombre")
        password = datos.get("password")

        if not nombre or not password:
            return jsonify({"success": False, "error": "Usuario y contraseña son obligatorios."}), 400

        # Validar credenciales
        login_manager = LoginManager()
        usuario = login_manager.validar_usuario(nombre, password)
        
        if not usuario:
            return jsonify({"success": False, "error": "Credenciales inválidas."}), 401

        # Verificar si es cliente y tiene perfil completo
        es_cliente = _es_rol_cliente(usuario.get("rol_nombre"))
        perfil_completo = True
        
        if es_cliente:
            perfil_completo = login_manager.verificar_perfil_completo_cliente(usuario.get("cedula"))
        
        # Preparar payload para la cookie
        payload = {
            "usuario_id": usuario.get("id"),
            "usuario_nombre": usuario.get("nombre"),
            "cedula": usuario.get("cedula"),
            "rol_id": usuario.get("rol_id"),
            "nombre_rol": usuario.get("rol_nombre"),
            "foto_perfil": usuario.get("foto_perfil"),
            "perfil_completo": perfil_completo,
        }
        
        resp = make_response(jsonify({
            "success": True,
            "message": "Inicio de sesión exitoso.",
            "require_profile_completion": es_cliente and not perfil_completo,
        }))
        
        return set_auth_cookies(resp, payload)
        
    except Exception as error:
        return _respuesta_error_por_excepcion(error)


@login_blueprint.route("/api/registro/cliente/paso-1", methods=["POST"])
def registro_cliente_paso_1():
    """Primer paso: crear solo el usuario"""
    import traceback
    import sys
    
    try:
        datos = request.get_json(silent=True) or {}
        
        print("=" * 50)
        print("DATOS RECIBIDOS:", datos)
        print("=" * 50)
        
        nombre_usuario = datos.get("nombre", "").strip()
        cedula = datos.get("cedula", "").strip()
        password = datos.get("password", "").strip()

        print(f"Usuario: {nombre_usuario}, Cédula: {cedula}, Password length: {len(password)}")

        # Validaciones
        if not nombre_usuario:
            return jsonify({"success": False, "error": "El nombre de usuario es obligatorio."}), 400
        
        if not cedula:
            return jsonify({"success": False, "error": "La cédula es obligatoria."}), 400
        
        if not password:
            return jsonify({"success": False, "error": "La contraseña es obligatoria."}), 400

        if not cedula.isdigit():
            return jsonify({"success": False, "error": "La cédula debe contener solo números."}), 400

        if len(password) < 6:
            return jsonify({"success": False, "error": "La contraseña debe tener al menos 6 caracteres."}), 400

        # Obtener login manager
        login_manager = LoginManager()

        # Verificar si ya existe
        if login_manager.verificar_usuario_existe_por_cedula(cedula):
            return jsonify({"success": False, "error": "Ya existe un usuario con esta cédula."}), 409

        if login_manager.verificar_usuario_existe_por_nombre(nombre_usuario):
            return jsonify({"success": False, "error": "El nombre de usuario ya está en uso."}), 409

        # Obtener rol cliente
        rol_cliente = login_manager.obtener_rol_cliente()
        print(f"Rol cliente encontrado: {rol_cliente}")
        
        if not rol_cliente:
            return jsonify({"success": False, "error": "No existe el rol Cliente configurado."}), 500

        # Crear usuario
        usuario_id = login_manager.crear_usuario(nombre_usuario, cedula, password, rol_cliente["id"])
        
        print(f"Usuario creado con ID: {usuario_id}")
        
        if not usuario_id:
            return jsonify({"success": False, "error": "No se pudo crear la cuenta. Verifica los logs del servidor."}), 500

        # Preparar payload para la cookie
        payload = {
            "usuario_id": usuario_id,
            "usuario_nombre": nombre_usuario,
            "cedula": int(cedula),
            "rol_id": rol_cliente["id"],
            "nombre_rol": rol_cliente["nombre"],
            "foto_perfil": None,
            "perfil_completo": False,
        }
        
        resp = make_response(jsonify({
            "success": True,
            "message": "Cuenta creada. Completa tu perfil.",
            "require_profile_completion": True,
        }))
        
        return set_auth_cookies(resp, payload)
        
    except Exception as error:
        print("=" * 50)
        print("ERROR EN PASO-1:")
        print("Tipo:", type(error).__name__)
        print("Mensaje:", str(error))
        print("Traceback completo:")
        traceback.print_exc()
        print("=" * 50)
        
        return jsonify({
            "success": False, 
            "error": f"Error interno: {str(error)}"
        }), 500

@login_blueprint.route("/api/registro/cliente/paso-2", methods=["POST"])
@jwt_required
def registro_cliente_paso_2():
    """Segundo paso: completar perfil del cliente"""
    try:
        usuario = getattr(g, "user", {}) or {}
        
        if not _es_rol_cliente(usuario.get("nombre_rol")):
            return jsonify({"success": False, "error": "Solo clientes pueden completar este registro."}), 403

        cedula = usuario.get("cedula")
        if not cedula:
            return jsonify({"success": False, "error": "No se encontró la cédula."}), 400

        datos = request.get_json(silent=True) or {}
        nombre = datos.get("nombre", "").strip()
        apellido = datos.get("apellido", "").strip()
        celular = datos.get("celular", "").strip()
        correo = datos.get("correo", "").strip()
        direccion = datos.get("direccion", "").strip()

        if not nombre or not apellido:
            return jsonify({"success": False, "error": "Nombre y apellido son obligatorios."}), 400

        if not celular:
            return jsonify({"success": False, "error": "El número de celular es obligatorio."}), 400
        
        # Limpiar y validar celular
        celular_limpio = re.sub(r'[\s\-\(\)\+]', '', celular)
        if not celular_limpio.isdigit() or len(celular_limpio) < 10:
            return jsonify({"success": False, "error": "Ingrese un número de teléfono válido (mínimo 10 dígitos)."}), 400

        # Validar correo si se proporcionó
        if correo:
            email_pattern = r'^[^\s@]+@([^\s@]+\.)+[^\s@]+$'
            if not re.match(email_pattern, correo):
                return jsonify({"success": False, "error": "Ingrese un correo electrónico válido."}), 400

        login_manager = LoginManager()

        # Crear perfil de cliente
        cliente_creado = login_manager.crear_cliente_natural(
            cedula=str(cedula),
            nombre=nombre,
            apellido=apellido,
            celular=celular_limpio,
            correo=correo if correo else None,
            direccion=direccion if direccion else None
        )

        if not cliente_creado:
            return jsonify({"success": False, "error": "No se pudo crear el perfil del cliente."}), 500

        # Actualizar payload
        payload = {
            "usuario_id": usuario.get("usuario_id"),
            "usuario_nombre": usuario.get("usuario_nombre"),
            "cedula": int(cedula),
            "rol_id": usuario.get("rol_id"),
            "nombre_rol": usuario.get("nombre_rol"),
            "foto_perfil": usuario.get("foto_perfil"),
            "perfil_completo": True,
        }
        
        resp = make_response(jsonify({
            "success": True,
            "message": "Perfil completado correctamente."
        }))
        
        return set_auth_cookies(resp, payload)
        
    except Exception as error:
        return _respuesta_error_por_excepcion(error)


@login_blueprint.route('/logout', methods=['GET'])
def logout():
    """Cierra la sesión del usuario"""
    resp = redirect(url_for('login.pagina_login'))
    return clear_auth_cookies(resp)