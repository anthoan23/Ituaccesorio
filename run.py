from flask import Flask, render_template
import os
from app.controllers.home_controller import home_blueprint
from app.controllers.prueba import prueba_blueprint
from app.controllers.telefonos import telefonos_blueprint



app = Flask(
    __name__,
    template_folder='views',
    static_folder='app/static',
    static_url_path='/static'
)

# Registramos el controlador
app.register_blueprint(home_blueprint)
app.register_blueprint(prueba_blueprint)
app.register_blueprint(telefonos_blueprint)



@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', '0').lower() in ('1', 'true', 'yes', 'on')
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)