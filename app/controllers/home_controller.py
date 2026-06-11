from flask import Blueprint, render_template, redirect, url_for, g, jsonify
from app.models.inventario import Inventario

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


@home_blueprint.route('/api/dashboard/bajo-stock', methods=['GET'])
def api_bajo_stock():
    """API para obtener productos con bajo stock (<=10)"""
    try:
        inventario = Inventario()
        productos = inventario.obtener_productos_bajo_stock(limite=10)
        return jsonify({"success": True, "productos": productos})
    except Exception as e:
        print(f"Error en api_bajo_stock: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@home_blueprint.route('/api/dashboard/sin-stock', methods=['GET'])
def api_sin_stock():
    """API para obtener productos sin stock (=0)"""
    try:
        inventario = Inventario()
        productos = inventario.obtener_productos_sin_stock()
        return jsonify({"success": True, "productos": productos})
    except Exception as e:
        print(f"Error en api_sin_stock: {e}")
        return jsonify({"success": False, "error": str(e)}), 500