import os
from flask import Flask, render_template, g, request
from flask_talisman import Talisman
from dotenv import load_dotenv
from flask_seasurf import SeaSurf
from types import SimpleNamespace
from app.utils.jwt_utils import decode_token

# Cargar las variables de entorno
load_dotenv()

# Variables de entorno
IS_TEST_MODE = os.getenv('ENTORNO_PRUEBA', 'false').lower() in ('1', 'true', 'yes', 'on')


def create_app():
    """Fábrica de aplicaciones Flask."""
    
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # --- CONFIGURACIÓN DE LA APLICACIÓN ---
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'views'),  # <--- Apunta a views/ en la raíz
        static_folder=os.path.join(base_dir, 'app', 'static'),  # app/static/
        static_url_path='/static'
    )
    
    # Configuración general
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "clave_secreta_para_desarrollo"),
        SEND_FILE_MAX_AGE_DEFAULT=0,
        # Configuraciones de bases de datos
        DB_HOST1=os.getenv('DB_HOST1', 'db1'),
        DB_NAME1=os.getenv('DB_NAME1', 'ituaccesoriobd'),
        DB_HOST2=os.getenv('DB_HOST2', 'db2'),
        DB_NAME2=os.getenv('DB_NAME2', 'seguridad'),
        DB_USER=os.getenv('DB_USER', 'user_flask'),
        DB_PASSWORD=os.getenv('DB_PASSWORD', '12345678'),
        DB_PASSWORD2=os.getenv('DB_PASSWORD2', os.getenv('DB_PASSWORD', '12345678')),
    )
    
    # --- SEGURIDAD ---
    csp = {
        'default-src': ["'self'"],
        'style-src': ["'self'", 'https://fonts.googleapis.com'],
        'style-src-elem': ["'self'", 'https://fonts.googleapis.com', 'https://unpkg.com', 'https://cdn.jsdelivr.net'],
        'script-src': ["'self'", 'https://unpkg.com', 'https://cdn.jsdelivr.net', 'https://www.google.com', 'https://www.gstatic.com', 'https://www.recaptcha.net'],
        'script-src-elem': ["'self'", 'https://unpkg.com', 'https://cdn.jsdelivr.net', 'https://www.google.com', 'https://www.gstatic.com', 'https://www.recaptcha.net'],
        'img-src': ["'self'", 'data:', 'blob:', 'https://www.google.com', 'https://www.gstatic.com', 'https://www.recaptcha.net', 'https://images.unsplash.com', 'https://plus.unsplash.com', 'https://picsum.photos'],
        'font-src': ["'self'", 'https://fonts.gstatic.com', 'data:'],
        'frame-src': ["'self'", 'https://www.google.com', 'https://www.recaptcha.net'],
        'child-src': ["'self'", 'https://www.google.com', 'https://www.recaptcha.net'],
        'connect-src': ["'self'", 'https://www.google.com', 'https://www.gstatic.com', 'https://www.recaptcha.net'],
    }
    
    if IS_TEST_MODE:
        talisman = Talisman(app, force_https=False, content_security_policy=None)
        app.config['CSRF_DISABLE'] = True
        csrf = SeaSurf(app)
    else:
        talisman = Talisman(app, content_security_policy=csp)
        csrf = SeaSurf(app)
    
    # --- REGISTRO DE BLUEPRINTS ---
    from app.controllers.backup import backup_blueprint
    from app.controllers.bitacora import bitacora_blueprint
    from app.controllers.cargos import cargos_blueprint
    from app.controllers.clientes import clientes_blueprint
    from app.controllers.empleados import empleados_blueprint
    from app.controllers.entregas import entregas_blueprint
    from app.controllers.especialidades import especialidades_blueprint
    from app.controllers.home_controller import home_blueprint
    from app.controllers.inventario import inventario_blueprint
    from app.controllers.james import james_blueprint
    from app.controllers.login import login_blueprint
    from app.controllers.notificaciones import notificaciones_blueprint
    from app.controllers.ordenes_compra import ordenes_compra_blueprint
    from app.controllers.ordenes_entregas import ordenes_entregas_blueprint
    from app.controllers.ordenes_servicio import ordenes_servicio_blueprint
    from app.controllers.productos import productos_blueprint
    from app.controllers.proveedores import proveedores_blueprint
    from app.controllers.reportes_ventas import reportes_ventas_blueprint
    from app.controllers.taller import taller_blueprint
    from app.controllers.tradein import tradein_blueprint
    from app.controllers.tradein_empleados import tradein_empleados_blueprint
    from app.controllers.usuarios import usuarios_blueprint
    from app.controllers.validacion_pagos import validacion_pagos_blueprint
    from app.controllers.ventas import ventas_blueprint
    from app.controllers.taller_celular import taller_celular_blueprint
    
    # Registrar cada blueprint con su prefijo de URL
    app.register_blueprint(home_blueprint, url_prefix='/')
    app.register_blueprint(login_blueprint, url_prefix='/')
    app.register_blueprint(usuarios_blueprint, url_prefix='/')
    app.register_blueprint(cargos_blueprint, url_prefix='/')
    app.register_blueprint(especialidades_blueprint, url_prefix='/')
    app.register_blueprint(empleados_blueprint, url_prefix='/')
    app.register_blueprint(clientes_blueprint, url_prefix='/')
    app.register_blueprint(productos_blueprint, url_prefix='/')
    app.register_blueprint(inventario_blueprint, url_prefix='/')
    app.register_blueprint(proveedores_blueprint, url_prefix='/')
    app.register_blueprint(ordenes_compra_blueprint, url_prefix='/')
    app.register_blueprint(ordenes_entregas_blueprint, url_prefix='/')
    app.register_blueprint(entregas_blueprint, url_prefix='/')
    app.register_blueprint(ordenes_servicio_blueprint, url_prefix='/')
    app.register_blueprint(taller_blueprint, url_prefix='/')
    app.register_blueprint(bitacora_blueprint, url_prefix='/')
    app.register_blueprint(backup_blueprint, url_prefix='/')
    app.register_blueprint(tradein_blueprint, url_prefix='/')
    app.register_blueprint(tradein_empleados_blueprint, url_prefix='/')
    app.register_blueprint(validacion_pagos_blueprint, url_prefix='/')
    app.register_blueprint(reportes_ventas_blueprint, url_prefix='/')
    app.register_blueprint(ventas_blueprint, url_prefix='/')
    app.register_blueprint(notificaciones_blueprint, url_prefix='/')
    app.register_blueprint(james_blueprint, url_prefix='/')
    app.register_blueprint(taller_celular_blueprint, url_prefix='/')
    
    # --- HOOKS DE REQUEST ---
    @app.before_request
    def load_user_from_jwt():
        """Carga el usuario desde el token JWT en las cookies."""
        token = request.cookies.get('access_token')
        if not token:
            auth = request.headers.get('Authorization', '')
            if auth.startswith('Bearer '):
                token = auth.split(' ', 1)[1].strip()

        payload = decode_token(token or "")
        if payload:
            g.user = SimpleNamespace(**payload)
        else:
            if IS_TEST_MODE:
                g.user = SimpleNamespace(
                    id_usuario=999,
                    username="test_admin",
                    rol_id=1,
                    rol_nombre="admin",
                    permisos={}
                )
            else:
                g.user = None

    @app.after_request
    def disable_html_cache(response):
        """Deshabilita el caché para páginas HTML."""
        content_type = response.headers.get("Content-Type", "")
        if content_type.startswith("text/html"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response
    
    # --- MANEJADORES DE ERRORES ---
    @app.errorhandler(404)
    def pagina_no_encontrada(error):
        """Página 404 personalizada."""
        return render_template('404.html'), 404
    
    return app