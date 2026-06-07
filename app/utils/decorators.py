from functools import wraps
from flask import request, jsonify, g, make_response, render_template
from app.utils.jwt_utils import decode_token, set_auth_cookies
from app.models.usuarios import Usuarios
from app.models.permisos import Permiso


def _get_bearer_token():
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return auth.split(' ', 1)[1].strip()
    return None


def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.cookies.get('access_token') or _get_bearer_token()
        payload = decode_token(token)

        if not payload:
            refresh_token = request.cookies.get('refresh_token')
            payload = decode_token(refresh_token)

        if not payload:
            return jsonify({"success": False, "error": "Autenticación requerida."}), 401

        # Attach user payload to g for handlers/templates
        g.user = payload
        response = make_response(func(*args, **kwargs))

        if request.cookies.get('access_token') or request.cookies.get('refresh_token'):
            set_auth_cookies(response, payload)

        return response

    return wrapper


def tiene_permiso(modulo_nombre, permiso_requerido):
   
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = getattr(g, 'user', None)
            
            # Verificar autenticación
            if not user:
                return jsonify({
                    "success": False, 
                    "error": "No autorizado. Inicie sesión nuevamente."
                }), 401
            
            # Obtener rol del usuario
            rol_id = user.get('rol_id')
            nombre_rol = user.get('nombre_rol', '').lower()
            
            if not rol_id:
                return jsonify({
                    "success": False, 
                    "error": "Usuario sin rol asignado."
                }), 403
            
            # ADMIN tiene todos los permisos (por ID o por nombre)
            if rol_id == 1 or nombre_rol == 'admin':
                return f(*args, **kwargs)
            
            # Verificar permiso en la base de datos usando el nuevo modelo Permiso
            permiso_model = Permiso()
            tiene_permiso = permiso_model.verificar_permiso(rol_id, modulo_nombre, permiso_requerido)
            
            if not tiene_permiso:
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

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = getattr(g, 'user', None)
            
            if not user:
                return jsonify({
                    "success": False, 
                    "error": "No autorizado. Inicie sesión nuevamente."
                }), 401
            
            nombre_rol = user.get('nombre_rol', '').lower()
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


def verificar_permiso_en_ruta(modulo_nombre, permiso_requerido):
    
    user = getattr(g, 'user', None)
    
    if not user:
        return False
    
    rol_id = user.get('rol_id')
    nombre_rol = user.get('nombre_rol', '').lower()
    
    # ADMIN tiene todos los permisos
    if rol_id == 1 or nombre_rol == 'admin':
        return True
    
    if not rol_id:
        return False
    
    # Usar el nuevo modelo Permiso
    permiso_model = Permiso()
    return permiso_model.verificar_permiso(rol_id, modulo_nombre, permiso_requerido)


def obtener_permisos_usuario_actual():
    """
    Obtiene todos los permisos del usuario actual aplicando la regla de negocio.
    
    Regla de negocio:
    - consultar = registrar OR modificar OR eliminar
    
    Returns:
        dict: Diccionario con los permisos del usuario
    """
    user = getattr(g, 'user', None)
    
    if not user:
        return {}
    
    usuario_id = user.get('usuario_id')
    nombre_rol = user.get('nombre_rol', '').lower()
    rol_id = user.get('rol_id')
    
    # ADMIN tiene todos los permisos (devolver todos los módulos con True)
    if rol_id == 1 or nombre_rol == 'admin':
        from app.models.modulos import Modulo
        modulo_model = Modulo()
        modulos = modulo_model.listar_modulos() or []
        permisos = {}
        for modulo in modulos:
            permisos[modulo['nombre']] = {
                'consultar': True,
                'registrar': True,
                'modificar': True,
                'eliminar': True
            }
        return permisos
    
    if not usuario_id:
        return {}
    
    # Usar el nuevo modelo Permiso
    permiso_model = Permiso()
    permisos_db = permiso_model.obtener_permisos_usuario(usuario_id) or []
    
    permisos = {}
    for p in permisos_db:
        # Los datos ya vienen con la regla de negocio aplicada desde el modelo
        permisos[p['modulo_nombre']] = {
            'consultar': bool(p.get('consultar', False)),
            'registrar': bool(p.get('registrar', False)),
            'modificar': bool(p.get('modificar', False)),
            'eliminar': bool(p.get('eliminar', False))
        }
    
    return permisos


def tiene_permiso_ruta(modulo_nombre, permiso_requerido):
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = getattr(g, 'user', None)
            
            if not user:
                return render_template('401.html'), 401
            
            rol_id = user.get('rol_id')
            nombre_rol = user.get('nombre_rol', '').lower()
            
            if rol_id == 1 or nombre_rol == 'admin':
                return f(*args, **kwargs)
            
            permiso_model = Permiso()
            tiene_permiso = permiso_model.verificar_permiso(rol_id, modulo_nombre, permiso_requerido)
            
            if not tiene_permiso:
                return render_template('403.html'), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator