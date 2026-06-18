from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.ordenes_compra import OrdenCompra
from datetime import datetime

ordenes_compra_blueprint = Blueprint('ordenes_compra', __name__)


@ordenes_compra_blueprint.route('/ordenes_compra', methods=['GET'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'consultar')
def pagina_ordenes_compra():
    return render_template(
        "ordenes_compra.html",
        active_page="ordenes_compra",
        show_navbar=True,
        show_notifications=True,
    )


@ordenes_compra_blueprint.route('/api/ordenes_compra', methods=['GET'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'consultar')
def api_ordenes_compra():
    orden = OrdenCompra()
    ordenes = orden.listar_ordenes_pendientes()
    return jsonify(ordenes)


@ordenes_compra_blueprint.route('/api/ordenes_compra/entregadas', methods=['GET'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'consultar')
def api_ordenes_compra_entregadas():
    orden = OrdenCompra()
    ordenes = orden.listar_ordenes_entregadas()
    return jsonify(ordenes)


@ordenes_compra_blueprint.route('/api/empleados', methods=['GET'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'consultar')
def api_empleados():
    orden = OrdenCompra()
    empleados = orden.listar_empleados()
    return jsonify(empleados)


@ordenes_compra_blueprint.route('/api/proveedores', methods=['GET'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'consultar')
def api_proveedores():
    orden = OrdenCompra()
    proveedores = orden.listar_proveedores()
    return jsonify({"success": True, "proveedores": proveedores})


@ordenes_compra_blueprint.route('/api/productos_proveedor/<int:id_proveedor>', methods=['POST'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'consultar')
def api_productos_proveedor(id_proveedor):
    orden = OrdenCompra()
    productos = orden.obtener_productos_proveedor(id_proveedor)
    return jsonify({"success": True, "productos": productos})


@ordenes_compra_blueprint.route('/api/detalles_orden/<string:id_orden>', methods=['GET'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'consultar')
def api_detalles_orden(id_orden):
    orden = OrdenCompra()
    detalles = orden.obtener_detalles_orden(id_orden)
    
    if detalles and detalles.get("datos_orden"):
        return jsonify(detalles)
    
    return jsonify({"error": f"Orden {id_orden} no encontrada"}), 404


@ordenes_compra_blueprint.route('/api/ordenes_compra/agregar', methods=['POST'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'registrar')
def api_agregar_orden_compra():
    try:
        data = request.get_json()
        
        id_empleado = data.get('ID_empleado')
        if not id_empleado:
            return jsonify({"success": False, "error": "Debe seleccionar un empleado"}), 400
        
        try:
            id_emp = int(id_empleado)
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "ID de empleado inválido"}), 400
        
        id_proveedor = data.get('ID_proveedor')
        productos = data.get('productos', [])

        if not id_proveedor:
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
            normalized.append((str(mid), int(qty)))

        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", None)

        orden = OrdenCompra(
            id_empleado=id_emp,
            id_proveedor=id_proveedor,
            productos=normalized,
            usuario_id=usuario_id
        )
        success = orden.agregar_orden_compra()
        
        if success:
            return jsonify({"success": True, "message": "Orden de compra agregada exitosamente"}), 201
        else:
            return jsonify({"success": False, "error": "Error al agregar la orden de compra"}), 500
    except Exception as e:
        print(f"Error en api_agregar_orden_compra: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@ordenes_compra_blueprint.route('/api/ordenes_compra/anular', methods=['POST'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'eliminar')
def api_anular_orden_compra():
    data = request.get_json()
    id_orden = data.get('ID_orden_c')

    if not id_orden:
        return jsonify({"success": False, "error": "Falta el campo requerido: ID_orden_c"}), 400

    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", None)

    orden = OrdenCompra(
        id_orden=id_orden,
        usuario_id=usuario_id
    )
    success = orden.anular_orden_compra()
    
    if success:
        return jsonify({"success": True, "message": "Orden de compra anulada exitosamente"}), 200
    return jsonify({"success": False, "error": "No se pudo anular la orden. Verifique que esté pendiente."}), 500