import os
from app import create_app
from werkzeug.serving import WSGIRequestHandler

app = create_app()


class ServidorSinVersion(WSGIRequestHandler):
    """Oculta la versión de Werkzeug/Python en el header `Server`.

    Evita la filtración de versión detectada por ZAP (alerta 10036):
    el servidor responde `Server: iTuaAccesorio` sin números de versión.
    """

    def version_string(self):
        return "iTuaAccesorio"


if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', '0').lower() in ('1', 'true', 'yes', 'on')
    # 0.0.0.0 es necesario dentro del contenedor Docker; en producción se usa gunicorn
    app.run(host='0.0.0.0', port=5000, debug=debug_mode,  # nosec B104
            request_handler=ServidorSinVersion)