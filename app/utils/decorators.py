import os
from functools import wraps
from flask import request, jsonify, g, make_response, render_template, redirect, url_for
from app.utils.jwt_utils import decode_token, set_auth_cookies, verificar_firma_fotos

IS_TEST_MODE = os.getenv('ENTORNO_PRUEBA', 'false').lower() in ('1', 'true', 'yes', 'on')


def _get_bearer_token():
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return auth.split(' ', 1)[1].strip()
    return None


def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        if IS_TEST_MODE:
            return func(*args, **kwargs)

        token = request.cookies.get('access_token') or _get_bearer_token()
        payload = decode_token(token)

        if not payload:
            refresh_token = request.cookies.get('refresh_token')
            payload = decode_token(refresh_token)

        if not payload:
            return redirect(url_for('login.pagina_login'))

        # Attach user payload to g for handlers/templates
        g.user = payload
        response = make_response(func(*args, **kwargs))

        if request.cookies.get('access_token') or request.cookies.get('refresh_token'):
            set_auth_cookies(response, payload)

        return response

    return wrapper


def tiene_permiso(modulo_nombre, permiso_requerido):
    """
    Verifica permisos directamente desde g.user.permisos (sin consultar BD)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            if IS_TEST_MODE:
                return f(*args, **kwargs)

            user = getattr(g, 'user', None)
            
            # Verificar autenticación
            if not user:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
                    return jsonify({
                        "success": False, 
                        "error": "No autorizado. Inicie sesión nuevamente."
                    }), 401
                return redirect(url_for('login.pagina_login'))
            
            # Obtener datos del usuario
            rol_id = user.get('rol_id')
            nombre_rol = user.get('rol_nombre', '').lower()
            
            if not rol_id:
                return jsonify({
                    "success": False, 
                    "error": "Usuario sin rol asignado."
                }), 403
            
            # ADMIN tiene todos los permisos (por ID o por nombre)
            if rol_id == 1 or nombre_rol == 'admin':
                return f(*args, **kwargs)
            
            # Obtener permisos del payload
            permisos = user.get('permisos', {})
            modulo_permisos = permisos.get(modulo_nombre, {})
            tiene_acceso = modulo_permisos.get(permiso_requerido, False)
            
            if not tiene_acceso:
                # Para peticiones AJAX devolver JSON, para páginas normales devolver 403.html
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
                    return jsonify({
                        "success": False, 
                        "error": f"No tienes permiso para {permiso_requerido} en el módulo {modulo_nombre}."
                    }), 403
                return render_template('403.html'), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def solo_roles(roles_permitidos):
    """
    Verifica roles directamente desde g.user
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            
            if IS_TEST_MODE:
                return f(*args, **kwargs)
            
            user = getattr(g, 'user', None)
            
            if not user:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
                    return jsonify({
                        "success": False, 
                        "error": "No autorizado. Inicie sesión nuevamente."
                    }), 401
                return redirect(url_for('login.pagina_login'))
            
            nombre_rol = user.get('rol_nombre', '').lower()
            rol_id = user.get('rol_id')
            
            # Verificar si el rol está permitido
            rol_permitido = nombre_rol in [r.lower() for r in roles_permitidos]
            
            # Admin siempre tiene acceso
            if not rol_permitido and rol_id != 1 and nombre_rol != 'admin':
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
                    return jsonify({
                        "success": False, 
                        "error": f"Acceso denegado. Se requiere uno de los siguientes roles: {', '.join(roles_permitidos)}"
                    }), 403
                return render_template('403.html'), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def token_fotos_required(func):
    """
    Valida la firma corta de subida de fotos (taller_celular).

    La firma viaja en el query param 't' de la URL del QR (?t=...) o en el
    form 't', es HMAC(SECRET, "id_orden|expira") truncada y se verifica sin
    estado. El id_orden se toma del argumento de la ruta (URL) o del form.
    El payload se adjunta a g.token_payload (contiene 'id_orden').
    """
    @wraps(func)
    def wrapper(*args, **kwargs):

        if IS_TEST_MODE:
            return func(*args, **kwargs)

        firma = request.args.get('t') or request.form.get('t')

        # Flask entrega los parámetros de la URL como kwargs (ej. id_orden)
        id_orden = kwargs.get('id_orden')
        if not id_orden and args:
            id_orden = args[0]
        if not id_orden:
            id_orden = request.form.get('id_orden') or request.args.get('id_orden') or ''

        if not firma or not verificar_firma_fotos(id_orden, firma):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
                return jsonify({
                    "success": False,
                    "error": "Firma de subida de fotos inválida o expirada."
                }), 401
            return render_template('403.html'), 403

        g.token_payload = {"id_orden": str(id_orden)}
        return func(*args, **kwargs)

    return wrapper