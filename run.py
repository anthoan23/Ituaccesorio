from flask import Flask
import os
from app.controllers.main_controller import main_blueprint

app = Flask(__name__, template_folder='app/views')

# Registramos el controlador
app.register_blueprint(main_blueprint)

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', '0').lower() in ('1', 'true', 'yes', 'on')
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)