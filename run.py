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
from app.controllers.taller import taller_blueprint
from app.controllers.clientes import clientes_blueprint
from app.controllers.ordenes_servicio import ordenes_servicio_blueprint
from app.controllers.ventas import ventas_blueprint

from app.controllers.inventario import inventario_blueprint
from app.controllers.ordenes_compra import ordenes_compra
from app.controllers.cargos import cargos_blueprint
from app.controllers.especialidades import especialidades_blueprint
from app.utils.jwt_utils import decode_token
from types import SimpleNamespace


load_dotenv()



app = Flask(
    __name__,
    template_folder='views',
    static_folder='app/static',
    static_url_path='/static'
)

app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY"),
)

csp = {
    'default-src': ["'self'"],
    'style-src': ["'self'", 'https://fonts.googleapis.com'],
    'style-src-elem': ["'self'", 'https://fonts.googleapis.com', 'https://unpkg.com'],
    'script-src': ["'self'", 'https://unpkg.com', 'https://cdn.jsdelivr.net', 'https://www.google.com', 'https://www.gstatic.com', 'https://www.recaptcha.net'],
    'script-src-elem': ["'self'", 'https://unpkg.com', 'https://cdn.jsdelivr.net', 'https://www.google.com', 'https://www.gstatic.com', 'https://www.recaptcha.net'],
    'style-src': ["'self'", 'https://fonts.googleapis.com', 'https://unpkg.com'],
    'img-src': ["'self'", 'data:', 'blob:', 'https://www.google.com', 'https://www.gstatic.com', 'https://www.recaptcha.net'],
    'font-src': ["'self'", 'https://fonts.gstatic.com', 'data:'],
    'frame-src': ["'self'", 'https://www.google.com', 'https://www.recaptcha.net'],
    'child-src': ["'self'", 'https://www.google.com', 'https://www.recaptcha.net'],
    'connect-src': ["'self'", 'https://www.google.com', 'https://www.gstatic.com', 'https://www.recaptcha.net'],
}

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
app.register_blueprint(taller_blueprint)
app.register_blueprint(clientes_blueprint)
app.register_blueprint(ordenes_servicio_blueprint)
app.register_blueprint(ventas_blueprint)

app.register_blueprint(inventario_blueprint)
app.register_blueprint(ordenes_compra)
app.register_blueprint(cargos_blueprint)
app.register_blueprint(especialidades_blueprint)

@app.before_request
def load_user_from_jwt():
    token = request.cookies.get('access_token')
    if not token:
        auth = request.headers.get('Authorization', '')
        if auth.startswith('Bearer '):
            token = auth.split(' ', 1)[1].strip()

    payload = decode_token(token or "")
    if payload:
        # convert dict to object for template attribute access
        g.user = SimpleNamespace(**payload)
    else:
        g.user = None



@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', '0').lower() in ('1', 'true', 'yes', 'on')
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
