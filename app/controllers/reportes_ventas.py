from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso, solo_roles
from app.models.reportes_ventas import ReportesVentasModel
from datetime import datetime
import traceback
from decimal import Decimal

reportes_ventas_blueprint = Blueprint("reportes_ventas", __name__)


@reportes_ventas_blueprint.route("/admin/reportes-ventas")
@jwt_required
@solo_roles(['admin', 'ventas'])
def pagina_reportes_ventas():
    """Página de reportes de ventas y ventas locales"""
    return render_template(
        "ventas/reportes.html",
        show_navbar=True,
        show_notifications=True,
        active_page="reportes_ventas"
    )


@reportes_ventas_blueprint.route("/api/reportes-ventas/listar", methods=["POST"])
@jwt_required
@tiene_permiso('Reportes Ventas', 'consultar')
def api_listar_reportes_ventas():
    """Obtiene ventas para reportes con filtros avanzados"""
    datos = request.get_json(silent=True) or {}
    
    filtros = {
        "q": datos.get("q", "").strip(),
        "estado": datos.get("estado"),
        "metodo_pago": datos.get("metodo_pago"),
        "moneda": datos.get("moneda"),
        "fecha_desde": datos.get("fecha_desde"),
        "fecha_hasta": datos.get("fecha_hasta"),
        "monto_min": datos.get("monto_min"),
        "monto_max": datos.get("monto_max"),
    }
    
    filtros = {k: v for k, v in filtros.items() if v not in (None, "", 0)}
    
    modelo = ReportesVentasModel()
    resultado = modelo.obtener_reportes_ventas(filtros)
    
    if resultado["success"]:
        resultado["fecha_reporte"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        resultado["filtros_aplicados"] = filtros
        return jsonify(resultado)
    else:
        return jsonify({"success": False, "error": resultado.get("error", "Error al generar reporte")}), 500


@reportes_ventas_blueprint.route("/api/reportes-ventas/detalle/<factura_id>", methods=["GET"])
@jwt_required
@tiene_permiso('Reportes Ventas', 'consultar')
def api_detalle_venta_reporte(factura_id):
    """Obtiene el detalle completo de una venta"""
    modelo = ReportesVentasModel(factura_id=factura_id)
    resultado = modelo.obtener_detalle_venta_completo()
    
    if resultado["success"]:
        return jsonify(resultado)
    else:
        return jsonify({"success": False, "error": resultado.get("error", "Error al obtener detalle")}), 500


# ==================== VENTAS LOCALES ====================

@reportes_ventas_blueprint.route("/api/reportes-ventas/ventas-locales", methods=["GET"])
@jwt_required
@tiene_permiso('Reportes Ventas', 'consultar')
def api_listar_ventas_locales():
    """Obtiene el historial de ventas locales"""
    try:
        busqueda = request.args.get("q", "").strip()
        fecha = request.args.get("fecha")
        
        modelo = ReportesVentasModel()
        ventas = modelo.obtener_ventas_locales(busqueda=busqueda, fecha=fecha)
        
        return jsonify({"success": True, "ventas": ventas})
    except Exception as e:
        print(f"Error en api_listar_ventas_locales: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@reportes_ventas_blueprint.route("/api/reportes-ventas/venta-local", methods=["POST"])
@jwt_required
@tiene_permiso('Reportes Ventas', 'crear')
def api_registrar_venta_local():
    """Registra una venta local (en tienda física)"""
    try:
        datos = request.get_json(silent=True) or {}
        
        cliente_id = datos.get("cliente_id")
        items = datos.get("items", [])
        metodo_pago = datos.get("metodo_pago")
        
        if not cliente_id:
            return jsonify({"success": False, "error": "Cliente no especificado"}), 400
        
        if not items:
            return jsonify({"success": False, "error": "Agrega al menos un producto"}), 400
        
        if not metodo_pago:
            return jsonify({"success": False, "error": "Método de pago no seleccionado"}), 400
        
        # Obtener usuario
        if isinstance(g.user, dict):
            usuario_id = g.user.get("id")
            empleado_id = g.user.get("cedula")
        else:
            usuario_id = getattr(g.user, "id", None)
            empleado_id = getattr(g.user, "cedula", None)
        
        modelo = ReportesVentasModel(
            cliente_id=str(cliente_id),
            items=items,
            metodo_pago=metodo_pago,
            empleado_id=str(empleado_id) if empleado_id else None,
            usuario_id=str(usuario_id) if usuario_id else None
        )
        
        factura_id = modelo.registrar_venta_local()
        
        return jsonify({
            "success": True,
            "factura_id": factura_id,
            "mensaje": "Venta local registrada exitosamente"
        })
        
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        print(f"Error en api_registrar_venta_local: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500