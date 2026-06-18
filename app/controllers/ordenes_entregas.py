from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.ordenes_entregas import OrdenEntregaModel
from app.models.ordenes_compra import OrdenCompra
from datetime import datetime

ordenes_entregas_blueprint = Blueprint('ordenes_entregas', __name__)


@ordenes_entregas_blueprint.route('/ordenes_entregas', methods=['GET'])
@jwt_required
@tiene_permiso('Entregas', 'consultar')
def pagina_ordenes_entregas():
    return render_template(
        "ordenes_entregas.html",
        active_page="ordenes_entregas",
        show_navbar=True,
        show_notifications=True,
    )


@ordenes_entregas_blueprint.route('/api/ordenes_entregas/pendientes', methods=['GET'])
@jwt_required
@tiene_permiso('Entregas', 'consultar')
def api_ordenes_entregas_pendientes():
    """Lista órdenes pendientes de entrega"""
    print("=== api_ordenes_entregas_pendientes llamada ===")
    orden = OrdenCompra()
    ordenes = orden.listar_ordenes_pendientes()
    print(f"Órdenes encontradas: {len(ordenes)}")
    for o in ordenes:
        print(f"  - {o.get('ID_orden_c')}: {o.get('Estado')}")
    return jsonify(ordenes)


@ordenes_entregas_blueprint.route('/api/ordenes_entregas/historial', methods=['GET'])
@jwt_required
@tiene_permiso('Entregas', 'consultar')
def api_ordenes_entregas_historial():
    """Lista entregas realizadas"""
    print("=== api_ordenes_entregas_historial llamada ===")
    entrega = OrdenEntregaModel()
    entregas = entrega.listar_entregas()
    print(f"Entregas encontradas: {len(entregas)}")
    for e in entregas:
        print(f"  - {e.get('ID_entrega')}: {e.get('ID_orden_c')} - {e.get('Recibido_por')}")
    return jsonify(entregas)


@ordenes_entregas_blueprint.route('/api/ordenes_entregas/<string:id_orden>/productos', methods=['GET'])
@jwt_required
@tiene_permiso('Entregas', 'consultar')
def api_ordenes_entregas_productos(id_orden):
    """Obtiene productos de una orden para entrega"""
    orden = OrdenCompra()
    productos = orden.obtener_productos_orden(id_orden)
    return jsonify({"success": True, "productos": productos})


@ordenes_entregas_blueprint.route('/api/ordenes_entregas/<string:id_orden>/registrar', methods=['POST'])
@jwt_required
@tiene_permiso('Entregas', 'modificar')
def api_registrar_entrega(id_orden):
    try:
        data = request.get_json()
        recibido_por = data.get('recibido_por')
        fecha_entrega = data.get('fecha_entrega')
        
        if not recibido_por:
            return jsonify({"success": False, "error": "Debe especificar quién recibió la orden"}), 400
        
        if not fecha_entrega:
            fecha_entrega = datetime.now().strftime("%Y-%m-%d")
        
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", None)
        
        id_empleado = None
        if usuario_id and str(usuario_id).isdigit():
            id_empleado = int(usuario_id)
        else:
            id_empleado = 30124556
            print(f"ID de empleado no numérico ('{usuario_id}'), usando valor por defecto: {id_empleado}")
        
        entrega = OrdenEntregaModel(
            id_orden=id_orden,
            recibido_por=recibido_por,
            fecha_entrega=fecha_entrega,
            id_empleado=id_empleado,
            usuario_id=usuario_id
        )
        
        success = entrega.registrar_entrega()
        
        if success:
            return jsonify({"success": True, "message": "Entrega registrada exitosamente. Stock actualizado."}), 200
        else:
            return jsonify({"success": False, "error": "No se pudo registrar la entrega"}), 500
    except Exception as e:
        print(f"Error en api_registrar_entrega: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500