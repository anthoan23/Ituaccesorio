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



    

@ordenes_compra.route('/api/detalles_orden/<int:ID_orden_c>', methods=['POST'])
@jwt_required
def api_detalles_orden(ID_orden_c):
    orden = OrdenCompra()
    detalles = orden.obtener_detalles_orden(ID_orden_c)
    if detalles and detalles.get("datos_orden"):
        return jsonify(detalles)
    else:
        return jsonify({"error": "Orden no encontrada"}), 404
    
@ordenes_compra.route('/api/ordenes_compra/agregar', methods=['POST'])
@jwt_required
def api_agregar_orden_compra():
    data = request.get_json()
    ID_em = 1004
    ID_proveedor = data.get('ID_proveedor')
    productos = data.get('productos')

    if not all([ID_em, ID_proveedor]):
        return jsonify({"error": "Faltan campos requeridos"}), 400

    # Validate productos is a non-empty list
    if productos is None or not isinstance(productos, list) or len(productos) == 0:
        return jsonify({"error": "El campo 'productos' debe ser una lista no vacía"}), 400

    # Normalize product entries to (ID_modelo, Cantidad_p) tuples
    normalized = []
    for idx, p in enumerate(productos, start=1):
        if isinstance(p, (list, tuple)):
            if len(p) < 2:
                return jsonify({"error": f"Producto #{idx} inválido: se requieren (ID_modelo, Cantidad_p)"}), 400
            mid, qty = p[0], p[1]
        elif isinstance(p, dict):
            mid = p.get('ID_modelo') or p.get('ID_modelo')
            qty = p.get('Cantidad_p') or p.get('Cantidad') or p.get('cantidad')
        else:
            return jsonify({"error": f"Producto #{idx} inválido: formato no reconocido"}), 400

        try:
            mid = int(mid)
            qty = int(qty)
        except Exception:
            return jsonify({"error": f"Producto #{idx} inválido: ID_modelo y Cantidad_p deben ser enteros"}), 400

        if qty <= 0:
            return jsonify({"error": f"Producto #{idx} inválido: Cantidad_p debe ser mayor que 0"}), 400

        normalized.append((mid, qty))

    orden = OrdenCompra()
    success = orden.agregar_orden_compra(ID_em, ID_proveedor, normalized)
    if success:
        return jsonify({"message": "Orden de compra agregada exitosamente"}), 201
    else:
        return jsonify({"error": "Error al agregar la orden de compra"}), 500
    

@ordenes_compra.route('/api/ordenes_compra/actualizar_productos', methods=['POST'])
@jwt_required
def api_actualizar_productos_orden():
    data = request.get_json()
    ID_orden_c = data.get('ID_orden_c')
    productos = data.get('productos')

    if not ID_orden_c:
        return jsonify({"error": "Falta el campo requerido: ID_orden_c"}), 400

    # Validate productos is a list if provided
    if productos is not None and (not isinstance(productos, list) or len(productos) == 0):
        return jsonify({"error": "El campo 'productos' debe ser una lista no vacía si se proporciona"}), 400

    # Normalize product entries to (ID_modelo, Cantidad_p) tuples
    normalized = []
    if productos:
        for idx, p in enumerate(productos, start=1):
            if isinstance(p, (list, tuple)):
                if len(p) < 2:
                    return jsonify({"error": f"Producto #{idx} inválido: se requieren (ID_modelo, Cantidad_p)"}), 400
                mid, qty = p[0], p[1]
            elif isinstance(p, dict):
                mid = p.get('ID_modelo') or p.get('ID_modelo')
                qty = p.get('Cantidad_p') or p.get('Cantidad') or p.get('cantidad')
            else:
                return jsonify({"error": f"Producto #{idx} inválido: formato no reconocido"}), 400

            try:
                mid = int(mid)
                qty = int(qty)
            except Exception:
                return jsonify({"error": f"Producto #{idx} inválido: ID_modelo y Cantidad_p deben ser enteros"}), 400

            if qty <= 0:
                return jsonify({"error": f"Producto #{idx} inválido: Cantidad_p debe ser mayor que 0"}), 400

            normalized.append((mid, qty))

    orden = OrdenCompra()
    success = orden.actualizar_productos_orden(ID_orden_c, normalized)
    if success:
        return jsonify({"message": "Productos de la orden actualizados exitosamente"})
    else:
        return jsonify({"error": "Error al actualizar los productos de la orden"}), 500
    
@ordenes_compra.route('/api/ordenes_compra/anular', methods=['POST'])
@jwt_required
def api_anular_orden_compra():
    data = request.get_json()
    ID_orden_c = data.get('ID_orden_c')

    if not ID_orden_c:
        return jsonify({"error": "Falta el campo requerido: ID_orden_c"}), 400

    orden = OrdenCompra()
    success = orden.anular_orden_compra(ID_orden_c)
    if success:
        return jsonify({"message": "Orden de compra anulada exitosamente"})
    else:
        return jsonify({"error": "Error al anular la orden de compra"}), 500