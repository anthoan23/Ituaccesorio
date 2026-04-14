from flask import Blueprint, render_template

main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/')
def home():
    # Aquí el controlador decide qué vista mostrar
    return render_template('index.html', mensaje="¡Hola desde MVC!")