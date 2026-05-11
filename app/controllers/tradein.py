from flask import Blueprint, jsonify, render_template
from app.models.tradein import TradeIn
from app.utils.decorators import jwt_required

tradein_blueprint = Blueprint("tradein", __name__)


@tradein_blueprint.route("/trade-in", methods=["GET"])
@jwt_required
def pagina_tradein():
    return render_template(
        "tradein.html",
        show_navbar=True,
        show_notifications=True,
        active_page="tradein",
    )


@tradein_blueprint.route("/api/trade-in", methods=["GET"])
@jwt_required
def obtener_tradein_json():
    modelo = TradeIn()
    tradeins_db = modelo.obtener_tradeins() or []
    return jsonify({
        "success": True,
        "tradeins": tradeins_db,
    })
