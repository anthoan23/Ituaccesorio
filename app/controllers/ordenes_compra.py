from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.ordenes_compra import OrdenCompra
from datetime import datetime

ordenes_compra = Blueprint('ordenes_compra', __name__)


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


@ordenes_compra.route('/api/detalles_orden/<string:ID_orden_c>', methods=['GET'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'consultar')
def api_detalles_orden(ID_orden_c):
    print(f"=== API DETALLES ORDEN ===")
    print(f"ID recibido: {ID_orden_c}")
    
    orden = OrdenCompra()
    detalles = orden.obtener_detalles_orden(ID_orden_c)
    
    if detalles and detalles.get("datos_orden"):
        print(f"✅ Orden encontrada: {detalles['datos_orden']['ID_orden_c']}")
        return jsonify(detalles)
    
    print(f"❌ Orden no encontrada: {ID_orden_c}")
    return jsonify({"error": f"Orden {ID_orden_c} no encontrada"}), 404


@ordenes_compra.route('/api/ordenes_compra/agregar', methods=['POST'])
@jwt_required
@tiene_permiso('Órdenes de compra', 'registrar')
def api_agregar_orden_compra():
    try:
        data = request.get_json()
        
        # Obtener ID del empleado desde g.user
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", None)
        if not usuario_id:
            return jsonify({"success": False, "error": "Usuario no identificado"}), 400
        
        try:
            ID_em = int(usuario_id)
        except (ValueError, TypeError):
            ID_em = 1
        
        ID_proveedor = data.get('ID_proveedor')
        productos = data.get('productos', [])

        if not ID_proveedor:
            return jsonify({"success": False, "error": "Debe seleccionar un proveedor"}), 400

        if not productos or len(productos) == 0:
            return jsonify({"success": False, "error": "Debe agregar al menos un producto"}), 400

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
        success = orden.agregar_orden_compra(ID_em, ID_proveedor, normalized)
        
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
        
        if not recibido_por:
            return jsonify({"success": False, "error": "Debe especificar quién recibió la orden"}), 400
        
        if not fecha_entrega:
            fecha_entrega = datetime.now().strftime("%Y-%m-%d")
        
        orden = OrdenCompra()
        success = orden.registrar_entrega(ID_orden_c, recibido_por, fecha_entrega)
        
        if success:
            return jsonify({"success": True, "message": "Entrega registrada exitosamente"}), 200
        else:
            return jsonify({"success": False, "error": "No se pudo registrar la entrega"}), 500
    except Exception as e:
        print(f"Error en api_registrar_entrega: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# Endpoint de depuración
@ordenes_compra.route('/api/ordenes_compra/debug/listar', methods=['GET'])
@jwt_required
def api_debug_listar_ordenes():
    """Endpoint temporal para depurar"""
    orden = OrdenCompra()
    db = orden.conexion1()
    
    if not db:
        return jsonify({"error": "No se pudo conectar"}), 500
    
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT ID_orden_compra FROM Orden_compra ORDER BY ID_orden_compra")
        todas = cursor.fetchall()
        
        cursor.execute("SELECT ID_orden_compra FROM Orden_compra WHERE Estado_orden_compra = 'Pendiente'")
        pendientes = cursor.fetchall()
        
        return jsonify({
            "todas": [o["ID_orden_compra"] for o in todas],
            "pendientes": [o["ID_orden_compra"] for o in pendientes],
            "total": len(todas)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()