from flask import Blueprint, jsonify, render_template, request
from app.utils.decorators import jwt_required

from app.models.ordenes_compra import OrdenCompra

ordenes_compra = Blueprint('ordenes_compra', __name__)

@ordenes_compra.route('/ordenes_compra', methods=['GET'])
@jwt_required
def pagina_ordenes_compra():
    return render_template(
        "ordenes_compra.html",
        active_page="Órdenes de Compra",
        show_navbar=True,
        show_notifications=True,
        )   