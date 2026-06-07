from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.bitacora import registrar_en_bitacora
from app.models.ordenes_compra import OrdenCompra
from datetime import datetime

ordenes_compra = Blueprint('ordenes_compra', __name__)


def _usuario_actual():
    user = getattr(g, 'user', None)
    if not user:
        return "SYSTEM"
    if isinstance(user, dict):
        return str(user.get("usuario_id") or user.get("id") or "SYSTEM")
    return str(getattr(user, "usuario_id", None) or getattr(user, "id", None) or "SYSTEM")


def _obtener_nombre_proveedor(proveedor_id):
    orden = OrdenCompra()
    proveedores = orden.enlistar_proveedores()
    for p in proveedores:
        if str(p.get("ID_proveedor")) == str(proveedor_id):
            return p.get("N_proveedor", str(proveedor_id))
    return str(proveedor_id)


@ordenes_compra.route('/ordenes_compra', methods=['GET'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'consultar')
def pagina_ordenes_compra():
    return render_template(
        "ordenes_compra.html",
        active_page="ordenes_compra",
        show_navbar=True,
        show_notifications=True,
    )


@ordenes_compra.route('/api/ordenes_compra', methods=['GET'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'consultar')
def api_ordenes_compra():
    orden = OrdenCompra()
    ordenes = orden.enlistar_ordenes_compra()
    return jsonify(ordenes)


@ordenes_compra.route('/api/ordenes_compra/todas', methods=['GET'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'consultar')
def api_ordenes_compra_todas():
    orden = OrdenCompra()
    ordenes = orden.enlistar_ordenes_compra_todas()
    return jsonify(ordenes)


@ordenes_compra.route('/api/ordenes_compra/entregadas', methods=['GET'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'consultar')
def api_ordenes_compra_entregadas():
    orden = OrdenCompra()
    ordenes = orden.enlistar_ordenes_entregadas()
    return jsonify(ordenes)


@ordenes_compra.route('/api/proveedores', methods=['GET'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'consultar')
def api_proveedores():
    orden = OrdenCompra()
    proveedores = orden.enlistar_proveedores()
    return jsonify(proveedores)


@ordenes_compra.route('/api/productos_proveedor/<int:ID_proveedor>', methods=['POST'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'consultar')
def api_productos_proveedor(ID_proveedor):
    orden = OrdenCompra()
    productos = orden.obtener_productos_proveedor(ID_proveedor)
    return jsonify(productos)


@ordenes_compra.route('/api/detalles_orden/<string:ID_orden_c>', methods=['POST'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'consultar')
def api_detalles_orden(ID_orden_c):
    orden = OrdenCompra()
    detalles = orden.obtener_detalles_orden(ID_orden_c)
    if detalles and detalles.get("datos_orden"):
        return jsonify(detalles)
    else:
        return jsonify({"error": "Orden no encontrada"}), 404


@ordenes_compra.route('/api/ordenes_compra/agregar', methods=['POST'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'registrar')
def api_agregar_orden_compra():
    data = request.get_json()
    
    # Usar un empleado que existe en la BD (32014004 es Eduin Meneses)
    ID_em = 32014004
    ID_proveedor = data.get('ID_proveedor')
    productos = data.get('productos')

    if not ID_proveedor:
        return jsonify({"error": "Debe seleccionar un proveedor"}), 400

    if not productos or len(productos) == 0:
        return jsonify({"error": "Debe agregar al menos un producto"}), 400

    normalized = []
    for p in productos:
        if isinstance(p, dict):
            mid = p.get('ID_modelo') or p.get('id_modelo')
            qty = p.get('Cantidad_p') or p.get('cantidad') or 1
        elif isinstance(p, (list, tuple)):
            mid, qty = p[0], p[1]
        else:
            continue
        
        normalized.append((str(mid), int(qty)))

    orden = OrdenCompra()
    success = orden.agregar_orden_compra(ID_em, ID_proveedor, normalized)
    
    if success:
        return jsonify({"message": "Orden de compra agregada exitosamente"}), 201
    else:
        return jsonify({"error": "Error al agregar la orden de compra"}), 500


@ordenes_compra.route('/api/ordenes_compra/actualizar_productos', methods=['POST'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'modificar')
def api_actualizar_productos_orden():
    data = request.get_json()
    ID_orden_c = data.get('ID_orden_c')
    productos = data.get('productos')

    if not ID_orden_c:
        return jsonify({"error": "Falta el campo requerido: ID_orden_c"}), 400

    normalized = []
    if productos:
        for p in productos:
            if isinstance(p, dict):
                mid = p.get('ID_modelo') or p.get('id_modelo')
                qty = p.get('Cantidad_p') or p.get('cantidad') or 1
            elif isinstance(p, (list, tuple)):
                mid, qty = p[0], p[1]
            else:
                continue
            normalized.append((str(mid), int(qty)))

    orden = OrdenCompra()
    success = orden.actualizar_productos_orden(ID_orden_c, normalized)
    
    if success:
        return jsonify({"message": "Productos de la orden actualizados exitosamente"}), 200
    else:
        return jsonify({"error": "Error al actualizar los productos de la orden"}), 500


@ordenes_compra.route('/api/ordenes_compra/anular', methods=['POST'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'eliminar')
def api_anular_orden_compra():
    data = request.get_json()
    ID_orden_c = data.get('ID_orden_c')

    if not ID_orden_c:
        return jsonify({"error": "Falta el campo requerido: ID_orden_c"}), 400

    orden = OrdenCompra()
    success = orden.anular_orden_compra(ID_orden_c)
    
    if success:
        return jsonify({"message": "Orden de compra anulada exitosamente"}), 200
    else:
        return jsonify({"error": "Error al anular la orden de compra"}), 500


@ordenes_compra.route('/api/ordenes_compra/<string:ID_orden_c>/entrega', methods=['POST'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'modificar')
def api_registrar_entrega(ID_orden_c):
    data = request.get_json()
    recibido_por = data.get('recibido_por')
    fecha_entrega = data.get('fecha_entrega')
    
    if not recibido_por:
        return jsonify({"error": "Debe especificar quién recibió la orden"}), 400
    
    if not fecha_entrega:
        fecha_entrega = datetime.now().strftime("%Y-%m-%d")
    
    orden = OrdenCompra()
    success = orden.registrar_entrega(ID_orden_c, recibido_por, fecha_entrega)
    
    if success:
        return jsonify({"message": "Entrega registrada exitosamente"}), 200
    else:
        return jsonify({"error": "Error al registrar la entrega"}), 500


@ordenes_compra.route('/api/ordenes_compra/reportes', methods=['POST'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'consultar')
def api_reportes_ordenes_compra():
    datos = request.get_json(silent=True) or {}
    
    filtros = {
        "proveedor_id": datos.get("proveedor_id"),
        "estado": datos.get("estado"),
        "fecha_desde": datos.get("fecha_desde"),
        "fecha_hasta": datos.get("fecha_hasta"),
        "costo_min": datos.get("costo_min"),
        "costo_max": datos.get("costo_max"),
    }
    
    orden = OrdenCompra()
    ordenes = orden.enlistar_ordenes_compra_todas() or []
    
    ordenes_filtradas = []
    for o in ordenes:
        if filtros["proveedor_id"] and str(o.get("ID_proveedor")) != str(filtros["proveedor_id"]):
            continue
        if filtros["estado"] and o.get("Estado", "").lower() != filtros["estado"].lower():
            continue
        if filtros["fecha_desde"] and o.get("Fecha_o", "") < filtros["fecha_desde"]:
            continue
        if filtros["fecha_hasta"] and o.get("Fecha_o", "") > filtros["fecha_hasta"]:
            continue
        ordenes_filtradas.append(o)
    
    proveedores = orden.enlistar_proveedores() or []
    
    return jsonify({
        "success": True,
        "ordenes": ordenes_filtradas,
        "total": len(ordenes_filtradas),
        "proveedores": proveedores,
        "fecha_reporte": datetime.now().strftime("%Y-%d-%m %H:%M:%S")
    })