from flask import Blueprint, render_template, redirect, url_for, g

home_blueprint = Blueprint('home', __name__)


@home_blueprint.route('/')
def home():
    usuario = getattr(g, "user", None)
    nombre_rol = getattr(usuario, "nombre_rol", "") if usuario else ""
    if str(nombre_rol or "").strip().lower() != "cliente" and usuario:
        return render_template('index.html', show_navbar=True, show_notifications=True, active_page='dashboard')
    return redirect(url_for("ventas.pagina_catalogo"))


@home_blueprint.route('/inventario')
def inventario():
    return render_template('inventario.html', show_navbar=True, show_notifications=True, active_page='inventario')
