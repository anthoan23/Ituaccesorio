from flask import Blueprint, jsonify, render_template, request, redirect, url_for, make_response, g
import os
import requests
import traceback
import mysql.connector
from app.models.login import LoginManager
from app.utils.decorators import jwt_required
from app.utils.jwt_utils import clear_auth_cookies, set_auth_cookies
from app.models.permisos import Permiso
from app.models.modulos import Modulo
from app.models.clientes import Clientes as GestionClientes
from app.utils.validators import validar_email, validar_numero

login_blueprint = Blueprint("login", __name__)

IS_TEST_MODE = os.getenv('ENTORNO_PRUEBA', 'false').lower() in ('1', 'true', 'yes', 'on')

@login_blueprint.route("/login", methods=["GET"])
def pagina_login():
    return render_template(
        "login_phone.html",
        recaptcha_site_key=os.getenv("RECAPTCHA_SITE_KEY", ""),
        is_test_mode=IS_TEST_MODE
    )


@login_blueprint.route("/api/login", methods=["POST"])
def validar_login():
    try:
        datos = request.get_json(silent=True) or {}
        
        # OBTENER EL ESTADO DEL MODO PRUEBA
        is_test_mode = os.getenv('ENTORNO_PRUEBA', 'false').lower() in ('1', 'true', 'yes', 'on')
        
        if is_test_mode:
            print("⚠️ Modo de prueba activo: Saltando validación de reCAPTCHA.")
            # EN MODO PRUEBA, SALTAMOS LA VALIDACIÓN DEL CAPTCHA
        else:
            # Validar captcha solo si NO estamos en modo prueba
            recaptcha_token = datos.get("recaptcha")
            secret = os.getenv("RECAPTCHA_SECRET_KEY")
            
            if not secret:
                return jsonify({"success": False, "error": "Captcha no configurado."}), 500
            if not recaptcha_token:
                return jsonify({"success": False, "error": "Completa el captcha para continuar."}), 400
            
            try:
                response = requests.post(
                    "https://www.google.com/recaptcha/api/siteverify",
                    data={"secret": secret, "response": recaptcha_token, "remoteip": request.remote_addr},
                    timeout=5
                )
                data = response.json()
            except requests.RequestException:
                return jsonify({"success": False, "error": "No se pudo validar el captcha. Intenta nuevamente."}), 500
            
            if not data.get("success"):
                return jsonify({"success": False, "error": "Captcha inválido. Intenta nuevamente."}), 400

        nombre = datos.get("nombre")
        password = datos.get("password")

        if not nombre or not password:
            return jsonify({"success": False, "error": "Usuario y contraseña son obligatorios."}), 400

        login_manager = LoginManager()
        usuario = login_manager.validar_usuario(nombre, password)
        
        if not usuario:
            return jsonify({"success": False, "error": "Credenciales inválidas."}), 401

        es_cliente = str(usuario.get("rol_nombre") or "").strip().lower() == "cliente"
        perfil_completo = True
        
        if es_cliente:
            perfil_completo = login_manager.verificar_perfil_completo_cliente(usuario.get("cedula"))
        
        # Cargar permisos del usuario
        permisos = {}
        if usuario.get("rol_id") == 1 or str(usuario.get("rol_nombre") or "").lower() == 'admin':
            modulo_model = Modulo()
            modulos = modulo_model.listar_modulos() or []
            for modulo in modulos:
                permisos[modulo['nombre']] = {
                    'consultar': True,
                    'registrar': True,
                    'modificar': True,
                    'eliminar': True
                }
        elif usuario.get("id"):
            permiso_model = Permiso()
            permisos_db = permiso_model.obtener_permisos_usuario(usuario.get("id")) or []
            for p in permisos_db:
                permisos[p['modulo_nombre']] = {
                    'consultar': bool(p.get('consultar', False)),
                    'registrar': bool(p.get('registrar', False)),
                    'modificar': bool(p.get('modificar', False)),
                    'eliminar': bool(p.get('eliminar', False))
                }
        
        payload = {
            "id": usuario.get("id"),
            "usuario_nombre": usuario.get("nombre"),
            "cedula": usuario.get("cedula"),
            "rol_id": usuario.get("rol_id"),
            "rol_nombre": usuario.get("rol_nombre"),
            "foto_perfil": usuario.get("foto_perfil"),
            "perfil_completo": perfil_completo,
            "permisos": permisos,
        }
        
        resp = make_response(jsonify({
            "success": True,
            "message": "Inicio de sesión exitoso.",
            "require_profile_completion": es_cliente and not perfil_completo,
        }))
        
        return set_auth_cookies(resp, payload)
        
    except Exception as error:
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
            return jsonify({"success": False, "error": "Error de base de datos. Intente de nuevo."}), 500
        
        return jsonify({"success": False, "error": "Ocurrió un error inesperado. Intente de nuevo."}), 500


@login_blueprint.route("/api/registro/cliente/paso-1", methods=["POST"])
def registro_cliente_paso_1():
    try:
        datos = request.get_json(silent=True) or {}
        
        # Validaciones (formato, duplicados) en Usuarios.agregar_usuario vía
        # LoginManager.crear_usuario: el controller no valida nada.
        nombre_usuario = str(datos.get("nombre") or "").strip()
        cedula = str(datos.get("cedula") or "").strip()
        password = str(datos.get("password") or "").strip()

        login_manager = LoginManager()

        rol_cliente = login_manager.obtener_rol_cliente()

        if not rol_cliente:
            return jsonify({"success": False, "error": "No existe el rol Cliente configurado."}), 500

        usuario_id, error, es_duplicado = login_manager.crear_usuario(
            nombre_usuario, cedula, password, rol_cliente["id"]
        )

        if error:
            return jsonify({"success": False, "error": error}), (409 if es_duplicado else 400)

        # Cargar permisos
        permisos = {}
        permiso_model = Permiso()
        permisos_db = permiso_model.obtener_permisos_usuario(usuario_id) or []
        for p in permisos_db:
            permisos[p['modulo_nombre']] = {
                'consultar': bool(p.get('consultar', False)),
                'registrar': bool(p.get('registrar', False)),
                'modificar': bool(p.get('modificar', False)),
                'eliminar': bool(p.get('eliminar', False))
            }

        payload = {
            "id": usuario_id,
            "usuario_nombre": nombre_usuario,
            "cedula": int(cedula),
            "rol_id": rol_cliente["id"],
            "rol_nombre": rol_cliente["nombre"],
            "foto_perfil": None,
            "perfil_completo": False,
            "permisos": permisos,
        }
        
        resp = make_response(jsonify({
            "success": True,
            "message": "Cuenta creada. Completa tu perfil.",
            "require_profile_completion": True,
        }))
        
        return set_auth_cookies(resp, payload)
        
    except Exception as error:
        print(f"ERROR EN PASO-1: {type(error).__name__}: {str(error)}")
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Error interno: {str(error)}"}), 500


@login_blueprint.route("/api/registro/cliente/paso-2", methods=["POST"])
@jwt_required
def registro_cliente_paso_2():
    try:
        usuario = getattr(g, 'user', None)
        if not usuario:
            return jsonify({"success": False, "error": "No autorizado"}), 401
        
        if isinstance(usuario, dict):
            nombre_rol = usuario.get("rol_nombre", "")
            cedula = usuario.get("cedula", "")
            usuario_id = usuario.get("id", "")
            usuario_nombre = usuario.get("usuario_nombre", "")
            rol_id = usuario.get("rol_id", "")
            foto_perfil = usuario.get("foto_perfil", "")
        else:
            nombre_rol = getattr(usuario, "rol_nombre", "")
            cedula = getattr(usuario, "cedula", "")
            usuario_id = getattr(usuario, "id", "")
            usuario_nombre = getattr(usuario, "usuario_nombre", "")
            rol_id = getattr(usuario, "rol_id", "")
            foto_perfil = getattr(usuario, "foto_perfil", "")
        
        if str(nombre_rol or "").strip().lower() != "cliente":
            return jsonify({"success": False, "error": "Solo clientes pueden completar este registro."}), 403

        if not cedula:
            return jsonify({"success": False, "error": "No se encontró la cédula."}), 400

        datos = request.get_json(silent=True) or {}
        nombre = str(datos.get("nombre") or "").strip()
        apellido = str(datos.get("apellido") or "").strip()
        celular = str(datos.get("celular") or "").strip()
        correo = str(datos.get("correo") or "").strip()
        direccion = str(datos.get("direccion") or "").strip()

        # Validaciones (obligatoriedad, formato de celular/correo, nombre y
        # apellido) en el modelo: Clientes.crear_cliente → registrar_persona_natural.
        modelo_clientes = GestionClientes()
        
        try:
            cedula_int = int(cedula)
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "La cédula debe ser numérica."}), 400
        existente = modelo_clientes.obtener_cliente_por_id(cedula_int)
        if existente:
            # Recargar permisos
            permisos = {}
            if rol_id == 1:
                modulo_model = Modulo()
                modulos = modulo_model.listar_modulos() or []
                for modulo in modulos:
                    permisos[modulo['nombre']] = {
                        'consultar': True, 'registrar': True, 'modificar': True, 'eliminar': True
                    }
            else:
                permiso_model = Permiso()
                permisos_db = permiso_model.obtener_permisos_usuario(usuario_id) or []
                for p in permisos_db:
                    permisos[p['modulo_nombre']] = {
                        'consultar': bool(p.get('consultar', False)),
                        'registrar': bool(p.get('registrar', False)),
                        'modificar': bool(p.get('modificar', False)),
                        'eliminar': bool(p.get('eliminar', False))
                    }
            
            payload = {
                "id": usuario_id,
                "usuario_nombre": usuario_nombre,
                "cedula": int(cedula),
                "rol_id": rol_id,
                "rol_nombre": nombre_rol,
                "foto_perfil": foto_perfil,
                "perfil_completo": True,
                "permisos": permisos,
            }
            resp = make_response(jsonify({"success": True, "message": "Perfil ya completado."}))
            return set_auth_cookies(resp, payload)

        # Dato crudo: el modelo normaliza y valida
        cliente_creado = modelo_clientes.crear_cliente(
            cliente_id=int(cedula),
            nombre=nombre,
            apellido=apellido,
            celular=celular,
            correo=correo if correo else None,
            direccion=direccion if direccion else None
        )
        
        if not cliente_creado:
            return jsonify({"success": False, "error": "No se pudo crear el perfil del cliente."}), 500
        
        # Recargar permisos
        permisos = {}
        if rol_id == 1:
            modulo_model = Modulo()
            modulos = modulo_model.listar_modulos() or []
            for modulo in modulos:
                permisos[modulo['nombre']] = {
                    'consultar': True, 'registrar': True, 'modificar': True, 'eliminar': True
                }
        else:
            permiso_model = Permiso()
            permisos_db = permiso_model.obtener_permisos_usuario(usuario_id) or []
            for p in permisos_db:
                permisos[p['modulo_nombre']] = {
                    'consultar': bool(p.get('consultar', False)),
                    'registrar': bool(p.get('registrar', False)),
                    'modificar': bool(p.get('modificar', False)),
                    'eliminar': bool(p.get('eliminar', False))
                }
        
        payload = {
            "id": usuario_id,
            "usuario_nombre": usuario_nombre,
            "cedula": int(cedula),
            "rol_id": rol_id,
            "rol_nombre": nombre_rol,
            "foto_perfil": foto_perfil,
            "perfil_completo": True,
            "permisos": permisos,
        }
        resp = make_response(jsonify({"success": True, "message": "Perfil completado correctamente."}))
        return set_auth_cookies(resp, payload)
        
    except Exception as error:
        print(f"Error en paso-2: {error}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(error)}), 500


@login_blueprint.route('/logout', methods=['GET'])
def logout():
    resp = redirect(url_for('login.pagina_login'))
    return clear_auth_cookies(resp)