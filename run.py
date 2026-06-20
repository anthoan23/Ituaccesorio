from flask import Flask, render_template, g, request
import os
from flask_talisman import Talisman
from dotenv import load_dotenv
from flask_seasurf import SeaSurf
from app.controllers.home_controller import home_blueprint
from app.controllers.empleados import empleados_blueprint
from app.controllers.tradein import tradein_blueprint
from app.controllers.productos import productos_blueprint
from app.controllers.proveedores import proveedores_blueprint
from app.controllers.login import login_blueprint
from app.controllers.usuarios import usuarios_blueprint
from app.controllers.bitacora import bitacora_blueprint
from app.controllers.notificaciones import notificaciones_blueprint
from app.controllers.taller import taller_blueprint
from app.controllers.clientes import clientes_blueprint
from app.controllers.ordenes_servicio import ordenes_servicio_blueprint
from app.controllers.ventas import ventas_blueprint
from app.controllers.inventario import inventario_blueprint
from app.controllers.ordenes_compra import ordenes_compra_blueprint
from app.controllers.ordenes_entregas import ordenes_entregas_blueprint
from app.controllers.cargos import cargos_blueprint
from app.controllers.especialidades import especialidades_blueprint
from app.controllers.validacion_pagos import validacion_pagos_blueprint
from app.controllers.entregas import entregas_blueprint
from app.controllers.backup import backup_blueprint
from app.controllers.tradein_empleados import tradein_empleados_blueprint
from app.utils.jwt_utils import decode_token
from types import SimpleNamespace


load_dotenv()

is_test_mode = os.getenv('ENTORNO_PRUEBA', 'false').lower() in ('1', 'true', 'yes', 'on')

app = Flask(
    __name__,
    template_folder='views',
    static_folder='app/static',
    static_url_path='/static'
)

app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY"),
    SEND_FILE_MAX_AGE_DEFAULT=0,
)

csp = {
    'default-src': ["'self'"],
    'style-src': ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
    'style-src-elem': ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com', 'https://unpkg.com', 'https://cdn.jsdelivr.net'],
    'script-src': ["'self'", 'https://unpkg.com', 'https://cdn.jsdelivr.net', 'https://www.google.com', 'https://www.gstatic.com', 'https://www.recaptcha.net', "'unsafe-inline'"],
    'script-src-elem': ["'self'", 'https://unpkg.com', 'https://cdn.jsdelivr.net', 'https://www.google.com', 'https://www.gstatic.com', 'https://www.recaptcha.net'],
    'style-src': ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com', 'https://unpkg.com', 'https://cdn.jsdelivr.net'],
    'img-src': ["'self'", 'data:', 'blob:', 'https://www.google.com', 'https://www.gstatic.com', 'https://www.recaptcha.net', 'https://images.unsplash.com', 'https://plus.unsplash.com', 'https://picsum.photos'],
    'font-src': ["'self'", 'https://fonts.gstatic.com', 'data:'],
    'frame-src': ["'self'", 'https://www.google.com', 'https://www.recaptcha.net'],
    'child-src': ["'self'", 'https://www.google.com', 'https://www.recaptcha.net'],
    'connect-src': ["'self'", 'https://www.google.com', 'https://www.gstatic.com', 'https://www.recaptcha.net'],
}

if is_test_mode:
    # 1. Desactivar CSP por completo
    talisman = Talisman(app, force_https=False, content_security_policy=None)
    
    # 2. Desactivar CSRF mediante la configuración antes de inicializar SeaSurf
    app.config['CSRF_DISABLE'] = True
    csrf = SeaSurf(app)
else:
    # Configuración de producción normal
    talisman = Talisman(app, content_security_policy=csp)
    csrf = SeaSurf(app)
# Aqui se debe registrar el controlador
app.register_blueprint(home_blueprint)
app.register_blueprint(empleados_blueprint)
app.register_blueprint(tradein_blueprint)
app.register_blueprint(productos_blueprint)
app.register_blueprint(proveedores_blueprint)
app.register_blueprint(login_blueprint)
app.register_blueprint(usuarios_blueprint)
app.register_blueprint(bitacora_blueprint)
app.register_blueprint(notificaciones_blueprint)
app.register_blueprint(taller_blueprint)
app.register_blueprint(clientes_blueprint)
app.register_blueprint(ordenes_servicio_blueprint)
app.register_blueprint(ventas_blueprint)
app.register_blueprint(inventario_blueprint)
app.register_blueprint(ordenes_compra_blueprint)
app.register_blueprint(ordenes_entregas_blueprint)
app.register_blueprint(cargos_blueprint)
app.register_blueprint(especialidades_blueprint)
app.register_blueprint(validacion_pagos_blueprint)
app.register_blueprint(entregas_blueprint)
app.register_blueprint(backup_blueprint)
app.register_blueprint(tradein_empleados_blueprint)

@app.before_request
def load_user_from_jwt():
    token = request.cookies.get('access_token')
    if not token:
        auth = request.headers.get('Authorization', '')
        if auth.startswith('Bearer '):
            token = auth.split(' ', 1)[1].strip()

    payload = decode_token(token or "")
    if payload:
        g.user = SimpleNamespace(**payload)
    else:
        # Si estamos en modo prueba y no hay credenciales, inyectamos un usuario Mock
        # para que las plantillas renderizadas no fallen al buscar g.user.rol_nombre, etc.
        if is_test_mode:
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
    content_type = response.headers.get("Content-Type", "")
    if content_type.startswith("text/html"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response



@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', '0').lower() in ('1', 'true', 'yes', 'on')
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
