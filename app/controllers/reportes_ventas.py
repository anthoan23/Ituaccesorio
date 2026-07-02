from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso, solo_roles
from app.models.reportes_ventas import ReportesVentasModel
from app.utils.validators import (
    validar_sin_caracteres_especiales
)
from datetime import datetime
import traceback

reportes_ventas_blueprint = Blueprint("reportes_ventas", __name__)


# ==================== PÁGINAS ====================

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


# ==================== VALIDACIONES ====================

def _validar_filtros_reportes(data):
    """
    Valida los filtros de reportes de ventas.
    
    Args:
        data (dict): Filtros del reporte
    
    Returns:
        tuple: (error_mensaje, error_codigo) o (None, None) si es válido
    """
    # Validar búsqueda (sin caracteres especiales)
    q = data.get("q", "").strip()
    if q:
        error = validar_sin_caracteres_especiales(q, 1, 100, "Búsqueda", permitir_espacios=True)
        if error:
            return error, 400
    
    # Validar fechas
    fecha_desde = data.get("fecha_desde")
    fecha_hasta = data.get("fecha_hasta")
    
    if fecha_desde and fecha_hasta:
        try:
            desde = datetime.strptime(fecha_desde, "%Y-%m-%d")
            hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d")
            if desde > hasta:
                return "La fecha 'desde' no puede ser mayor que la fecha 'hasta'.", 400
        except ValueError:
            return "Formato de fecha inválido. Use YYYY-MM-DD.", 400
    
    # Validar montos
    monto_min = data.get("monto_min")
    monto_max = data.get("monto_max")
    
    if monto_min is not None:
        try:
            monto_min = float(monto_min)
            if monto_min < 0:
                return "El monto mínimo no puede ser negativo.", 400
        except (ValueError, TypeError):
            return "El monto mínimo debe ser un número válido.", 400
    
    if monto_max is not None:
        try:
            monto_max = float(monto_max)
            if monto_max < 0:
                return "El monto máximo no puede ser negativo.", 400
        except (ValueError, TypeError):
            return "El monto máximo debe ser un número válido.", 400
    
    if monto_min is not None and monto_max is not None:
        if monto_min > monto_max:
            return "El monto mínimo no puede ser mayor que el monto máximo.", 400
    
    return None, 200


def _validar_venta_local_data(data):
    """
    Valida los datos de una venta local.
    
    Args:
        data (dict): Datos de la venta local
    
    Returns:
        tuple: (error_mensaje, error_codigo) o (None, None) si es válido
    """
    # Validar cliente
    cliente_id = data.get("cliente_id")
    if not cliente_id:
        return "El campo Cliente es obligatorio.", 400
    
    # Validar items
    items = data.get("items", [])
    if not items:
        return "Agrega al menos un producto.", 400
    
    for i, item in enumerate(items):
        producto_id = item.get("producto_id")
        cantidad = item.get("cantidad", 0)
        
        if not producto_id:
            return f"El producto #{i+1} no tiene ID válido.", 400
        
        if cantidad is None:
            return f"La cantidad del producto #{i+1} es obligatoria.", 400
        
        try:
            cantidad = int(cantidad)
            if cantidad < 1:
                return f"La cantidad del producto #{i+1} debe ser al menos 1.", 400
        except (ValueError, TypeError):
            return f"La cantidad del producto #{i+1} debe ser un número válido.", 400
    
    # Validar método de pago
    metodo_pago = data.get("metodo_pago")
    if not metodo_pago:
        return "El campo Método de pago es obligatorio.", 400
    
    metodos_validos = ["pago_movil", "zelle", "binance", "efectivo_bs", "efectivo_usd"]
    if metodo_pago not in metodos_validos:
        return f"Método de pago '{metodo_pago}' no válido. Opciones: {', '.join(metodos_validos)}", 400
    
    return None, 200


# ==================== REPORTES DE VENTAS ====================

@reportes_ventas_blueprint.route("/api/reportes-ventas/listar", methods=["POST"])
@jwt_required
@tiene_permiso('Reportes Ventas', 'consultar')
def api_listar_reportes_ventas():
    """Obtiene ventas para reportes con filtros avanzados"""
    datos = request.get_json(silent=True) or {}
    
    # Validar filtros
    error, status = _validar_filtros_reportes(datos)
    if error:
        return jsonify({"success": False, "error": error}), status
    
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
        
        # Validar búsqueda
        if busqueda:
            error = validar_sin_caracteres_especiales(busqueda, 1, 100, "Búsqueda", permitir_espacios=True)
            if error:
                return jsonify({"success": False, "error": error}), 400
        
        fecha = request.args.get("fecha")
        if fecha:
            try:
                datetime.strptime(fecha, "%Y-%m-%d")
            except ValueError:
                return jsonify({"success": False, "error": "Formato de fecha inválido. Use YYYY-MM-DD."}), 400
        
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
        
        # Validar datos
        error, status = _validar_venta_local_data(datos)
        if error:
            return jsonify({"success": False, "error": error}), status
        
        cliente_id = datos.get("cliente_id")
        items = datos.get("items", [])
        metodo_pago = datos.get("metodo_pago")
        
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