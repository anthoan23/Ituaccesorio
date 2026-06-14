from flask import Blueprint, jsonify, render_template, request, g
from app.models.tradein import TradeIn

tradein_blueprint = Blueprint("tradein", __name__)


def _obtener_usuario_actual():
    """Obtiene el ID del usuario actual (si está logueado) o None si no"""
    user = getattr(g, 'user', None)
    if not user:
        return None  # Usuario no autenticado
    if isinstance(user, dict):
        return str(user.get("usuario_id") or user.get("id"))
    return str(getattr(user, "usuario_id", None) or getattr(user, "id", None))


@tradein_blueprint.route("/trade-in", methods=["GET"])
# Sin decoradores - acceso completamente público
def pagina_tradein():
    modelo = TradeIn()
    return render_template(
        "tradein.html",
        show_navbar=True,
        show_notifications=True,
        active_page="tradein",
        equipos=modelo.consultar_equipos() or [],
        fallas=TradeIn.FALLAS_COTIZACION,
    )


@tradein_blueprint.route("/api/trade-in", methods=["GET"])
# Sin decoradores - acceso completamente público
def obtener_tradein_json():
    modelo = TradeIn()
    return jsonify({
        "success": True,
        "equipos": modelo.consultar_equipos() or [],
        "fallas": TradeIn.FALLAS_COTIZACION,
    })


@tradein_blueprint.route("/api/trade-in/cotizar", methods=["POST"])
# Sin decoradores - acceso completamente público
def cotizar_tradein():
    datos = request.get_json(silent=True) or {}
    
    # Obtener usuario actual (puede ser None para usuarios no autenticados)
    usuario_id = _obtener_usuario_actual()
    
    # Crear instancia del modelo con el usuario_id
    modelo = TradeIn(usuario_id=usuario_id)

    # Validar liberación del equipo
    liberado = str(datos.get("liberado", "")).strip().lower()
    if liberado not in ("si", "s", "sí", "1", "true", "on", "yes"):
        return jsonify({
            "success": False,
            "error": "Lo sentimos, el equipo debe estar liberado para calificar"
        }), 400

    id_producto = datos.get("id_producto")
    if id_producto in (None, ""):
        return jsonify({
            "success": False,
            "error": "Debes seleccionar un equipo para cotizar."
        }), 400

    try:
        resultado = modelo.calcular_cotizacion(
            int(id_producto), 
            datos.get("fallas") or []
        )
    except ValueError:
        return jsonify({
            "success": False,
            "error": "El equipo seleccionado no es válido.",
        }), 400

    estado = 200 if resultado.get("success") else 400
    return jsonify(resultado), estado