from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso, solo_roles
from app.models.validacion_pagos import ValidacionPagosModel
from app.utils.validators import (
    validar_sin_caracteres_especiales,
    validar_campo_comun
)
from datetime import datetime
import traceback
from decimal import Decimal

validacion_pagos_blueprint = Blueprint("validacion_pagos", __name__)


# ==================== PÁGINAS ====================

@validacion_pagos_blueprint.route("/admin/validar-pagos")
@jwt_required
@solo_roles(['admin', 'ventas'])
def pagina_validar_pagos():
    """Panel de validación de pagos para empleados"""
    return render_template(
        "validacion_pagos.html",
        show_navbar=True,
        show_notifications=True,
        active_page="validar_pagos"
    )


# ==================== VALIDACIONES ====================

def _validar_rechazo_data(data):
    """
    Función auxiliar para validar los datos de rechazo de pago.
    
    Args:
        data (dict): Datos del rechazo
    
    Returns:
        tuple: (error_mensaje, error_codigo) o (None, None) si es válido
    """
    motivo = data.get("motivo", "").strip()
    
    if not motivo:
        return "Debe especificar un motivo para el rechazo.", 400
    
    # Validar que el motivo no tenga caracteres especiales
    error = validar_sin_caracteres_especiales(motivo, 3, 200, "Motivo del rechazo", permitir_espacios=True)
    if error:
        return error, 400
    
    return None, 200


def _validar_filtros_reportes(data):
    """
    Valida los filtros de reportes de pagos.
    
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


# ==================== LISTAR PAGOS ====================

@validacion_pagos_blueprint.route("/api/validacion-pagos/pendientes", methods=["GET"])
@jwt_required
@tiene_permiso('Validación Pagos', 'consultar')
def api_pagos_pendientes():
    try:
        modelo = ValidacionPagosModel()
        pagos = modelo.obtener_pagos_pendientes()
        return jsonify({"success": True, "pagos": pagos})
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@validacion_pagos_blueprint.route("/api/validacion-pagos/aprobados", methods=["GET"])
@jwt_required
@tiene_permiso('Validación Pagos', 'consultar')
def api_pagos_aprobados():
    try:
        modelo = ValidacionPagosModel()
        pagos = modelo.obtener_pagos_aprobados()
        return jsonify({"success": True, "pagos": pagos})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@validacion_pagos_blueprint.route("/api/validacion-pagos/rechazados", methods=["GET"])
@jwt_required
@tiene_permiso('Validación Pagos', 'consultar')
def api_pagos_rechazados():
    try:
        modelo = ValidacionPagosModel()
        pagos = modelo.obtener_pagos_rechazados()
        return jsonify({"success": True, "pagos": pagos})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@validacion_pagos_blueprint.route("/api/validacion-pagos/venta/<factura_id>/detalle", methods=["GET"])
@jwt_required
@tiene_permiso('Validación Pagos', 'consultar')
def api_detalle_venta(factura_id):
    try:
        modelo = ValidacionPagosModel(factura_id=factura_id)
        detalle = modelo.obtener_detalle_venta()
        
        for item in detalle:
            if 'Costo_venta' in item and isinstance(item['Costo_venta'], Decimal):
                item['Costo_venta'] = float(item['Costo_venta'])
        
        return jsonify({"success": True, "detalle": detalle})
    except Exception as e:
        print(f"Error en api_detalle_venta: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== APROBAR Y RECHAZAR ====================

@validacion_pagos_blueprint.route("/api/validacion-pagos/aprobar/<factura_id>", methods=["POST"])
@jwt_required
@tiene_permiso('Validación Pagos', 'modificar')
def api_aprobar_pago(factura_id):
    try:
        # Obtener cédula del empleado desde g.user
        if isinstance(g.user, dict):
            empleado_id = g.user.get("cedula")
            usuario_id = g.user.get("id")
        else:
            empleado_id = getattr(g.user, "cedula", None)
            usuario_id = getattr(g.user, "id", None)
        
        empleado_id = str(empleado_id) if empleado_id else None
        usuario_id = str(usuario_id) if usuario_id else None
        
        if not empleado_id:
            return jsonify({"success": False, "error": "Empleado no identificado - cédula no encontrada en token"}), 400
        
        modelo = ValidacionPagosModel(
            factura_id=factura_id,
            empleado_id=empleado_id,
            usuario_id=usuario_id
        )
        
        # Actualizar fecha de pago
        modelo.actualizar_fecha_pago()
        
        # Aprobar pago
        resultado = modelo.aprobar_pago()
        
        if resultado["success"]:
            return jsonify({"success": True, "mensaje": "Pago aprobado correctamente", "fecha_aprobacion": datetime.now().isoformat()})
        else:
            return jsonify({"success": False, "error": resultado.get("error", "Error al aprobar")}), 500
    except Exception as e:
        print(f"Error en api_aprobar_pago: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@validacion_pagos_blueprint.route("/api/validacion-pagos/rechazar/<factura_id>", methods=["POST"])
@jwt_required
@tiene_permiso('Validación Pagos', 'modificar')
def api_rechazar_pago(factura_id):
    try:
        datos = request.get_json(silent=True) or {}
        
        # Validar datos
        error, status = _validar_rechazo_data(datos)
        if error:
            return jsonify({"success": False, "error": error}), status
        
        motivo = datos.get("motivo", "").strip()
        
        # Obtener cédula del empleado desde g.user
        if isinstance(g.user, dict):
            empleado_id = g.user.get("cedula")
            usuario_id = g.user.get("id")
        else:
            empleado_id = getattr(g.user, "cedula", None)
            usuario_id = getattr(g.user, "id", None)
        
        empleado_id = str(empleado_id) if empleado_id else None
        usuario_id = str(usuario_id) if usuario_id else None
        
        if not empleado_id:
            return jsonify({"success": False, "error": "Empleado no identificado - cédula no encontrada en token"}), 400
        
        modelo = ValidacionPagosModel(
            factura_id=factura_id,
            empleado_id=empleado_id,
            usuario_id=usuario_id
        )
        
        resultado = modelo.rechazar_pago(motivo=motivo)
        
        if resultado["success"]:
            return jsonify({"success": True, "mensaje": "Pago rechazado"})
        else:
            return jsonify({"success": False, "error": resultado.get("error", "Error al rechazar")}), 500
    except Exception as e:
        print(f"Error en api_rechazar_pago: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== REPORTES ====================

@validacion_pagos_blueprint.route("/api/validacion-pagos/reportes", methods=["POST"])
@jwt_required
@tiene_permiso('Validación Pagos', 'consultar')
def api_reportes_pagos():
    """Obtiene pagos para reportes con filtros avanzados"""
    from datetime import datetime
    
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
    
    modelo = ValidacionPagosModel()
    resultado = modelo.obtener_reportes_pagos(filtros)
    
    if resultado["success"]:
        resultado["fecha_reporte"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        resultado["filtros_aplicados"] = filtros
        return jsonify(resultado)
    else:
        return jsonify({"success": False, "error": resultado.get("error", "Error al generar reporte")}), 500


@validacion_pagos_blueprint.route("/api/validacion-pagos/detalle-venta/<factura_id>", methods=["GET"])
@jwt_required
@tiene_permiso('Validación Pagos', 'consultar')
def api_detalle_venta_reporte(factura_id):
    """Obtiene el detalle completo de una venta para reportes"""
    modelo = ValidacionPagosModel(factura_id=factura_id)
    resultado = modelo.obtener_reporte_detalle_ventas()
    
    if resultado["success"]:
        return jsonify(resultado)
    else:
        return jsonify({"success": False, "error": resultado.get("error", "Error al obtener detalle")}), 500


@validacion_pagos_blueprint.route("/api/validacion-pagos/metodos-pago", methods=["GET"])
@jwt_required
@tiene_permiso('Validación Pagos', 'consultar')
def api_listar_metodos_pago():
    """Lista los métodos de pago disponibles para filtros"""
    modelo = ValidacionPagosModel()
    return jsonify({
        "success": True,
        "metodos": modelo.obtener_metodos_pago_disponibles()
    })


@validacion_pagos_blueprint.route("/api/validacion-pagos/monedas", methods=["GET"])
@jwt_required
@tiene_permiso('Validación Pagos', 'consultar')
def api_listar_monedas():
    """Lista las monedas disponibles para filtros"""
    modelo = ValidacionPagosModel()
    return jsonify({
        "success": True,
        "monedas": modelo.obtener_monedas_disponibles()
    })