from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso, solo_roles
from app.models.bitacora import registrar_en_bitacora
from app.models.validacion_pagos import ValidacionPagosModel
from datetime import datetime
import traceback
from decimal import Decimal

validacion_pagos_blueprint = Blueprint("validacion_pagos", __name__)


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
        modelo = ValidacionPagosModel()
        detalle = modelo.obtener_detalle_venta(factura_id)
        
        for item in detalle:
            if 'Costo_venta' in item and isinstance(item['Costo_venta'], Decimal):
                item['Costo_venta'] = float(item['Costo_venta'])
        
        return jsonify({"success": True, "detalle": detalle})
    except Exception as e:
        print(f"Error en api_detalle_venta: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@validacion_pagos_blueprint.route("/api/validacion-pagos/aprobar/<factura_id>", methods=["POST"])
@jwt_required
@tiene_permiso('Validación Pagos', 'modificar')
def api_aprobar_pago(factura_id):
    try:
        # CORREGIDO: Usar 'cedula' en lugar de 'cedula_personal'
        if isinstance(g.user, dict):
            empleado_id = g.user.get("cedula")
            print(f"empleado_id desde dict: {empleado_id}")
        else:
            empleado_id = getattr(g.user, "cedula", None)
            print(f"empleado_id desde objeto: {empleado_id}")
        
        empleado_id = str(empleado_id) if empleado_id else None
        
        if not empleado_id:
            print("ERROR: No se encontró la cédula en el token")
            return jsonify({"success": False, "error": "Empleado no identificado - cédula no encontrada en token"}), 400
        
        modelo = ValidacionPagosModel()
        modelo.actualizar_fecha_pago(factura_id)
        resultado = modelo.aprobar_pago(factura_id, empleado_id)
        
        if resultado["success"]:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            
            registrar_en_bitacora(
                accion="Aprobar pago",
                descripcion=f"Se aprobó el pago de la factura ID: {factura_id}",
                usuario_id=usuario_id,
                modulo_nombre="Validación Pagos"
            )
            print(f"Pago {factura_id} aprobado por empleado {empleado_id}")
            print("=" * 50)
            return jsonify({"success": True, "mensaje": "Pago aprobado correctamente", "fecha_aprobacion": datetime.now().isoformat()})
        else:
            print(f"ERROR al aprobar: {resultado.get('error')}")
            print("=" * 50)
            return jsonify({"success": False, "error": resultado.get("error", "Error al aprobar")}), 500
    except Exception as e:
        print(f"Error en api_aprobar_pago: {e}")
        traceback.print_exc()
        print("=" * 50)
        return jsonify({"success": False, "error": str(e)}), 500


@validacion_pagos_blueprint.route("/api/validacion-pagos/rechazar/<factura_id>", methods=["POST"])
@jwt_required
@tiene_permiso('Validación Pagos', 'modificar')
def api_rechazar_pago(factura_id):
    try:
        datos = request.get_json(silent=True) or {}
        motivo = datos.get("motivo", "")
        
        if not motivo:
            return jsonify({"success": False, "error": "Debe especificar un motivo"}), 400
        
        # Debug
        print("=" * 50)
        print("DEBUG - Rechazando pago para factura:", factura_id)
        print("Motivo:", motivo)
        print("g.user:", g.user)
        
        # CORREGIDO: Usar 'cedula' en lugar de 'cedula_personal'
        if isinstance(g.user, dict):
            empleado_id = g.user.get("cedula")
            print(f"empleado_id desde dict: {empleado_id}")
        else:
            empleado_id = getattr(g.user, "cedula", None)
            print(f"empleado_id desde objeto: {empleado_id}")
        
        empleado_id = str(empleado_id) if empleado_id else None
        
        if not empleado_id:
            print("ERROR: No se encontró la cédula en el token")
            return jsonify({"success": False, "error": "Empleado no identificado - cédula no encontrada en token"}), 400
        
        modelo = ValidacionPagosModel()
        resultado = modelo.rechazar_pago(factura_id, empleado_id, motivo)
        
        if resultado["success"]:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            
            registrar_en_bitacora(
                accion="Rechazar pago",
                descripcion=f"Se rechazó el pago de la factura ID: {factura_id} - Motivo: {motivo}",
                usuario_id=usuario_id,
                modulo_nombre="Validación Pagos"
            )
            print(f"Pago {factura_id} rechazado por empleado {empleado_id}")
            print("=" * 50)
            return jsonify({"success": True, "mensaje": "Pago rechazado"})
        else:
            print(f"ERROR al rechazar: {resultado.get('error')}")
            print("=" * 50)
            return jsonify({"success": False, "error": resultado.get("error", "Error al rechazar")}), 500
    except Exception as e:
        print(f"Error en api_rechazar_pago: {e}")
        traceback.print_exc()
        print("=" * 50)
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== REPORTES ====================

@validacion_pagos_blueprint.route("/api/validacion-pagos/reportes", methods=["POST"])
@jwt_required
@tiene_permiso('Validación Pagos', 'consultar')
def api_reportes_pagos():
    """Obtiene pagos para reportes con filtros avanzados"""
    from datetime import datetime
    
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
    modelo = ValidacionPagosModel()
    resultado = modelo.obtener_reporte_detalle_ventas(factura_id)
    
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