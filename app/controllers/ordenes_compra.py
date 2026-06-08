from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso
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


def _obtener_id_empleado():
    user = getattr(g, 'user', None)
    if not user:
        return 1111111111
    if isinstance(user, dict):
        return user.get("usuario_id") or user.get("id") or user.get("ID_empleado") or 1111111111
    return getattr(user, "usuario_id", None) or getattr(user, "id", None) or 1111111111


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
    return jsonify({"success": True, "proveedores": proveedores})


@ordenes_compra.route('/api/productos_proveedor/<int:ID_proveedor>', methods=['POST'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'consultar')
def api_productos_proveedor(ID_proveedor):
    orden = OrdenCompra()
    productos = orden.obtener_productos_proveedor(ID_proveedor)
    return jsonify({"success": True, "productos": productos})


@ordenes_compra.route('/api/detalles_orden/<string:ID_orden_c>', methods=['GET', 'POST'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'consultar')
def api_detalles_orden(ID_orden_c):
    orden = OrdenCompra()
    detalles = orden.obtener_detalles_orden(ID_orden_c)
    if detalles and detalles.get("datos_orden"):
        return jsonify(detalles)
    return jsonify({"error": "Orden no encontrada"}), 404


@ordenes_compra.route('/api/ordenes_compra/agregar', methods=['POST'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'registrar')
def api_agregar_orden_compra():
    try:
        data = request.get_json()
        
        ID_em = _obtener_id_empleado()
        ID_proveedor = data.get('ID_proveedor')
        productos = data.get('productos', [])

        if not ID_proveedor:
            return jsonify({"success": False, "error": "Debe seleccionar un proveedor"}), 400

        if not productos or len(productos) == 0:
            return jsonify({"success": False, "error": "Debe agregar al menos un producto"}), 400

        # Normalizar productos
        normalized = []
        for p in productos:
            if isinstance(p, dict):
                mid = p.get('ID_modelo') or p.get('id_modelo')
                qty = p.get('Cantidad_p') or p.get('cantidad') or 1
            elif isinstance(p, (list, tuple)):
                mid, qty = p[0], p[1]
            else:
                continue
            normalized.append((int(mid), int(qty)))

        orden = OrdenCompra()
        success = orden.agregar_orden_compra(int(ID_em), int(ID_proveedor), normalized)
        
        if success:
            return jsonify({"success": True, "message": "Orden de compra agregada exitosamente"}), 201
        else:
            return jsonify({"success": False, "error": "Error al agregar la orden de compra"}), 500
    except Exception as e:
        print(f"Error en api_agregar_orden_compra: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ordenes_compra.route('/api/ordenes_compra/anular', methods=['POST'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'eliminar')
def api_anular_orden_compra():
    data = request.get_json()
    ID_orden_c = data.get('ID_orden_c')

    if not ID_orden_c:
        return jsonify({"success": False, "error": "Falta el campo requerido: ID_orden_c"}), 400

    orden = OrdenCompra()
    success = orden.anular_orden_compra(ID_orden_c)
    
    if success:
        return jsonify({"success": True, "message": "Orden de compra anulada exitosamente"}), 200
    return jsonify({"success": False, "error": "No se pudo anular la orden. Verifique que esté pendiente."}), 500


@ordenes_compra.route('/api/ordenes_compra/<string:ID_orden_c>/entrega', methods=['POST'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'modificar')
def api_registrar_entrega(ID_orden_c):
    try:
        data = request.get_json()
        recibido_por = data.get('recibido_por')
        fecha_entrega = data.get('fecha_entrega')
        
        print(f"=== Registrando entrega ===")
        print(f"ID_orden: {ID_orden_c}")
        print(f"Recibido por: {recibido_por}")
        print(f"Fecha entrega: {fecha_entrega}")
        
        if not recibido_por:
            return jsonify({"success": False, "error": "Debe especificar quién recibió la orden"}), 400
        
        if not fecha_entrega:
            fecha_entrega = datetime.now().strftime("%Y-%m-%d")
        
        orden = OrdenCompra()
        success = orden.registrar_entrega(ID_orden_c, recibido_por, fecha_entrega)
        
        print(f"Resultado: {success}")
        
        if success:
            return jsonify({"success": True, "message": "Entrega registrada exitosamente"}), 200
        else:
            return jsonify({"success": False, "error": "No se pudo registrar la entrega. Verifique que la orden exista y esté pendiente."}), 500
    except Exception as e:
        print(f"Error en api_registrar_entrega: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500