from flask import Blueprint, render_template

home_blueprint = Blueprint('home', __name__)


@home_blueprint.route('/')
def home():
    # Aquí el controlador decide qué vista mostrar
    return render_template('index.html', mensaje="¡Hola desde MVC!")
