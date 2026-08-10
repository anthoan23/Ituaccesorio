from flask import Blueprint, g, jsonify, render_template, request

from app.models.tradein import TradeIn
from app.utils.validators import validar_numero, validar_texto

tradein_blueprint = Blueprint("tradein", __name__)


def _obtener_usuario_actual():
    """Obtiene el ID del usuario actual (si está logueado) o None si no"""
    user = getattr(g, 'user', None)
    if not user:
        return None
    if isinstance(user, dict):
        return str(user.get("usuario_id") or user.get("id") or user.get("cedula"))
    return str(getattr(user, "usuario_id", None) or getattr(user, "id", None) or getattr(user, "cedula", None))


@tradein_blueprint.route("/trade-in", methods=["GET"])
def pagina_tradein():
    """Página principal de Trade-in - acceso público"""
    modelo = TradeIn()
    equipos = modelo.consultar_equipos() or []
    
    return render_template(
        "tradein.html",
        show_navbar=True,
        show_notifications=True,
        active_page="tradein",
        equipos=equipos,
        fallas=TradeIn.FALLAS_COTIZACION,
    )


@tradein_blueprint.route("/api/trade-in", methods=["GET"])
def obtener_tradein_json():
    """API para obtener datos de Trade-in - acceso público"""
    try:
        modelo = TradeIn()
        return jsonify({
            "success": True,
            "equipos": modelo.consultar_equipos() or [],
            "fallas": TradeIn.FALLAS_COTIZACION,
        })
    except Exception as e:
        print(f"Error en obtener_tradein_json: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@tradein_blueprint.route("/api/trade-in/cotizar", methods=["POST"])
def cotizar_tradein():
    """API para calcular cotización - acceso público"""
    try:
        datos = request.get_json(silent=True) or {}
        
        # Validar producto
        id_producto = datos.get("id_producto")
        if not id_producto:
            return jsonify({"success": False, "error": "Debes seleccionar un equipo para cotizar."}), 400
        
        error = validar_numero(id_producto, 1, 10, "ID del equipo")
        if error:
            return jsonify({"success": False, "error": error}), 400
        
        # Validar liberado
        liberado = str(datos.get("liberado", "")).strip().lower()
        valores_liberado = ("si", "s", "sí", "1", "true", "on", "yes")
        if liberado not in valores_liberado:
            return jsonify({"success": False, "error": "Lo sentimos, el equipo debe estar liberado para calificar."}), 400
        
        # Validar fallas
        fallas = datos.get("fallas") or []
        if not isinstance(fallas, list):
            return jsonify({"success": False, "error": "El formato de fallas no es válido."}), 400
        
        usuario_id = _obtener_usuario_actual()
        
        modelo = TradeIn(usuario_id=usuario_id)
        resultado = modelo.calcular_cotizacion(id_producto, fallas)
        estado = 200 if resultado.get("success") else 400
        return jsonify(resultado), estado
        
    except Exception as e:
        print(f"Error en cotizar_tradein: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@tradein_blueprint.route("/api/trade-in/equipos", methods=["GET"])
def obtener_equipos():
    """API para obtener solo la lista de equipos"""
    try:
        modelo = TradeIn()
        return jsonify({
            "success": True,
            "equipos": modelo.consultar_equipos() or []
        })
    except Exception as e:
        print(f"Error en obtener_equipos: {e}")
        return jsonify({"success": False, "error": str(e)}), 500