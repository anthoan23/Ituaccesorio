from flask import Blueprint, jsonify, request

from app.models.inventario import Inventario
from app.utils.decorators import jwt_required

inventario_blueprint = Blueprint("inventario", __name__)


@inventario_blueprint.route("/api/inventario", methods=["GET"])
@jwt_required
def api_listar_inventario():
    """Listado de inventario (stock + modelo + marca + clase + caracteristica).

    Query params opcionales:
    - num_i: filtra por clase_producto.Num_i (ej. 2 = repuestos/herramientas)
    - modelo: filtra por modelo_producto.N_modelo (match exacto)
    """

    num_i_raw = request.args.get("num_i")
    modelo = request.args.get("modelo")

    num_i = None
    if num_i_raw not in (None, ""):
        try:
            num_i = int(num_i_raw)
        except Exception:
            return jsonify({"success": False, "error": "num_i debe ser un número."}), 400

    if modelo is not None:
        modelo = str(modelo).strip()
        if modelo == "":
            modelo = None

    inv = Inventario()
    inventario = inv.listar_inventario_filtrado(num_i=num_i, N_modelo=modelo) or []
    return jsonify({"success": True, "inventario": inventario})


@inventario_blueprint.route("/api/inventario/stock", methods=["POST"])
@jwt_required
def api_registrar_stock():
    datos = request.get_json(silent=True) or {}
    id_modelo = datos.get("id_modelo")
    existencia = datos.get("existencia")
    costo_venta = datos.get("costo_venta")
    capacidad = datos.get("capacidad")
    color = datos.get("color")

    try:
        id_modelo_val = int(id_modelo)
    except Exception:
        return jsonify({"success": False, "error": "id_modelo es obligatorio."}), 400

    try:
        existencia_val = int(existencia)
    except Exception:
        return jsonify({"success": False, "error": "existencia debe ser un número."}), 400

    try:
        costo_val = int(costo_venta)
    except Exception:
        return jsonify({"success": False, "error": "costo_venta debe ser un número."}), 400

    if existencia_val < 0:
        return jsonify({"success": False, "error": "existencia no puede ser negativa."}), 400
    if costo_val < 0:
        return jsonify({"success": False, "error": "costo_venta no puede ser negativo."}), 400

    inv = Inventario()
    try:
        id_producto = inv.registrar_stock(
            id_modelo=id_modelo_val,
            existencia=existencia_val,
            costo_venta=costo_val,
            capacidad=capacidad,
            color=color,
        )
        if not id_producto:
            return jsonify({"success": False, "error": "No se pudo conectar a la base de datos."}), 500
        return jsonify({"success": True, "id_producto": int(id_producto)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400
