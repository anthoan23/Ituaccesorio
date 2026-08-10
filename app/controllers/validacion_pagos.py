from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso, solo_roles
from app.models.validacion_pagos import ValidacionPagosModel
from app.utils.validators import (
    validar_texto,
    validar_numero,
    validar_decimal,
    validar_sin_caracteres_especiales
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
        "ventas/validacion.html",
        show_navbar=True,
        show_notifications=True,
        active_page="validar_pagos"
    )


# ==================== LISTAR PAGOS ====================

@validacion_pagos_blueprint.route("/api/validacion-pagos/pendientes", methods=["GET"])
@jwt_required
@tiene_permiso('Validación Pagos', 'consultar')
def api_pagos_pendientes():
    try:
        modelo = ValidacionPagosModel()
        pagos = modelo.obtener_pagos_pendientes()
        print(f"[api] /pendientes -> registros devueltos: {len(pagos)}")
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
        print(f"[api] /aprobados -> registros devueltos: {len(pagos)}")
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
        print(f"[api] /rechazados -> registros devueltos: {len(pagos)}")
        return jsonify({"success": True, "pagos": pagos})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@validacion_pagos_blueprint.route("/api/validacion-pagos/venta/<factura_id>/detalle", methods=["GET"])
@jwt_required
@tiene_permiso('Validación Pagos', 'consultar')
def api_detalle_venta(factura_id):
    try:
        error = validar_texto_numero(factura_id, 1, 50, "Factura")
        if error:
            return jsonify({"success": False, "error": error}), 400
        
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
        error = validar_texto_numero(factura_id, 1, 50, "Factura")
        if error:
            return jsonify({"success": False, "error": error}), 400
        
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
        error = validar_texto_numero(factura_id, 1, 50, "Factura")
        if error:
            return jsonify({"success": False, "error": error}), 400
        
        datos = request.get_json(silent=True) or {}
        
        # Validar motivo
        motivo = datos.get("motivo", "").strip()
        if not motivo:
            return jsonify({"success": False, "error": "Debe especificar un motivo para el rechazo."}), 400
        
        error = validar_sin_caracteres_especiales(motivo, 3, 200, "Motivo del rechazo", permitir_espacios=True)
        if error:
            return jsonify({"success": False, "error": error}), 400
        
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
    
    # Validar búsqueda
    q = datos.get("q", "").strip()
    if q:
        error = validar_sin_caracteres_especiales(q, 1, 100, "Búsqueda", permitir_espacios=True)
        if error:
            return jsonify({"success": False, "error": error}), 400
    
    # Validar fechas
    fecha_desde = datos.get("fecha_desde")
    fecha_hasta = datos.get("fecha_hasta")
    
    if fecha_desde and fecha_hasta:
        try:
            desde = datetime.strptime(fecha_desde, "%Y-%m-%d")
            hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d")
            if desde > hasta:
                return jsonify({"success": False, "error": "La fecha 'desde' no puede ser mayor que la fecha 'hasta'."}), 400
        except ValueError:
            return jsonify({"success": False, "error": "Formato de fecha inválido. Use YYYY-MM-DD."}), 400
    
    # Validar montos
    monto_min = datos.get("monto_min")
    monto_max = datos.get("monto_max")
    
    if monto_min is not None:
        error = validar_decimal(monto_min, "Monto mínimo", max_decimales=2, min_valor=0)
        if error:
            return jsonify({"success": False, "error": error}), 400
    
    if monto_max is not None:
        error = validar_decimal(monto_max, "Monto máximo", max_decimales=2, min_valor=0)
        if error:
            return jsonify({"success": False, "error": error}), 400
    
    if monto_min is not None and monto_max is not None:
        try:
            if float(monto_min) > float(monto_max):
                return jsonify({"success": False, "error": "El monto mínimo no puede ser mayor que el monto máximo."}), 400
        except ValueError:
            pass
    
    filtros = {
        "q": q,
        "estado": datos.get("estado"),
        "metodo_pago": datos.get("metodo_pago"),
        "moneda": datos.get("moneda"),
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "monto_min": monto_min,
        "monto_max": monto_max,
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
    error = validar_texto_numero(factura_id, 1, 50, "Factura")
    if error:
        return jsonify({"success": False, "error": error}), 400
    
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