from flask import Blueprint, jsonify, render_template, request
from app.utils.decorators import jwt_required

from app.models.ordenes_compra import OrdenCompra

ordenes_compra = Blueprint('ordenes_compra', __name__)

@ordenes_compra.route('/ordenes_compra', methods=['GET'])
@jwt_required
def pagina_ordenes_compra():
    return render_template(
        "ordenes_compra.html",
        active_page="ordenes_compra",
        show_navbar=True,
        show_notifications=True,
        )   


@ordenes_compra.route('/api/ordenes_compra', methods=['GET'])
@jwt_required
def api_ordenes_compra():
    orden = OrdenCompra()
    ordenes = orden.enlistar_ordenes_compra()
    return jsonify(ordenes)

@ordenes_compra.route('/api/proveedores', methods=['GET'])
@jwt_required
def api_proveedores():
    orden = OrdenCompra()
    proveedores = orden.enlistar_proveedores()
    return jsonify(proveedores)



@ordenes_compra.route('/api/productos_proveedor/<int:ID_proveedor>', methods=['POST'])
@jwt_required
def api_productos_proveedor(ID_proveedor):
    orden = OrdenCompra()
    productos = orden.obtener_productos_proveedor(ID_proveedor)
    return jsonify(productos)


@ordenes_compra.route('/api/ordenes_compra', methods=['POST'])
@jwt_required
def api_agregar_orden_compra():
    data = request.get_json()
    ID_em = 1004
    ID_proveedor = data.get('ID_proveedor')
    Costo_venta = data.get('Costo_venta')

    if not all([ID_em, ID_proveedor, Costo_venta]):
        return jsonify({"error": "Faltan campos requeridos"}), 400

    orden = OrdenCompra()
    success = orden.agregar_orden_compra(ID_em, ID_proveedor, Costo_venta)
    if success:
        return jsonify({"message": "Orden de compra agregada exitosamente"}), 201
    else:
        return jsonify({"error": "Error al agregar la orden de compra"}), 500