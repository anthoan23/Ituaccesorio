from flask import Blueprint, jsonify, request

from decimal import Decimal, InvalidOperation

from app.models.inventario import Inventario
from app.utils.decorators import jwt_required

inventario_blueprint = Blueprint("inventario", __name__)


@inventario_blueprint.route("/api/inventario", methods=["GET"])
@jwt_required
def api_listar_inventario():
    """Listado de inventario (stock + modelo + marca + clase + caracteristica).

    Query params opcionales:
    - modelo: filtra por Producto.Nombre_producto (match exacto)
    """

    modelo = request.args.get("modelo")

    if modelo is not None:
        modelo = str(modelo).strip()
        if modelo == "":
            modelo = None

    inv = Inventario()
    inventario = inv.listar_inventario_filtrado(N_modelo=modelo) or []
    return jsonify({"success": True, "inventario": inventario})


@inventario_blueprint.route("/api/inventario/stock", methods=["POST"])
@jwt_required
def api_registrar_stock():
    datos = request.get_json(silent=True) or {}
    id_producto = datos.get("id_producto")
    existencia = datos.get("existencia")
    costo_venta = datos.get("costo_venta")
    capacidad = datos.get("capacidad")
    color = datos.get("color")

    try:
        id_producto_val = int(id_producto)
    except Exception:
        return jsonify({"success": False, "error": "id_producto es obligatorio."}), 400

    try:
        existencia_val = int(existencia)
    except Exception:
        return jsonify({"success": False, "error": "existencia debe ser un número."}), 400

    try:
        costo_raw = str(costo_venta).strip().replace(",", ".")
        costo_val = Decimal(costo_raw)
    except (InvalidOperation, Exception):
        return jsonify({"success": False, "error": "costo_venta debe ser un número (ej. 12.50)."}), 400

    if existencia_val < 0:
        return jsonify({"success": False, "error": "existencia no puede ser negativa."}), 400
    if costo_val < 0:
        return jsonify({"success": False, "error": "costo_venta no puede ser negativo."}), 400

    inv = Inventario()
    try:
        id_inventario = inv.registrar_stock(
            id_producto=id_producto_val,
            existencia=existencia_val,
            costo_venta=costo_val,
            capacidad=capacidad,
            color=color,
        )
        if not id_inventario:
            return jsonify({"success": False, "error": "No se pudo conectar a la base de datos."}), 500
        return jsonify({"success": True, "id_inventario": int(id_inventario)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400
