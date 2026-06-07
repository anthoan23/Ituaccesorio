from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso, solo_roles
from app.models.bitacora import registrar_en_bitacora
from app.models.validacion_pagos import ValidacionPagosModel
from datetime import datetime
import traceback
from decimal import Decimal

validacion_pagos_blueprint = Blueprint("validacion_pagos", __name__)


def _usuario_actual() -> str:
    """Obtiene el ID del usuario actual"""
    user = getattr(g, 'user', None)
    if not user:
        return "SYSTEM"
    if isinstance(user, dict):
        return str(user.get("usuario_id") or user.get("id") or "SYSTEM")
    return str(getattr(user, "usuario_id", None) or getattr(user, "id", None) or "SYSTEM")


def _obtener_id_empleado() -> str:
    """Obtiene el ID del empleado actual (cédula como string)"""
    user = getattr(g, 'user', None)
    if not user:
        return None
    
    if isinstance(user, dict):
        cedula = user.get("cedula_personal") or user.get("cedula")
    else:
        cedula = getattr(user, "cedula_personal", None) or getattr(user, "cedula", None)
    
    return str(cedula) if cedula else None


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
@tiene_permiso('Ventas', 'consultar')
def api_pagos_pendientes():
    try:
        modelo = ValidacionPagosModel()
        pagos = modelo.obtener_pagos_pendientes()
        print(f"API pendientes: {len(pagos)} pagos")
        return jsonify({"success": True, "pagos": pagos})
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@validacion_pagos_blueprint.route("/api/validacion-pagos/aprobados", methods=["GET"])
@jwt_required
@tiene_permiso('Ventas', 'consultar')
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
@tiene_permiso('Ventas', 'consultar')
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
@tiene_permiso('Ventas', 'consultar')
def api_detalle_venta(factura_id):
    try:
        modelo = ValidacionPagosModel()
        detalle = modelo.obtener_detalle_venta(factura_id)
        
        print(f"API detalle venta {factura_id}: {len(detalle)} items")
        
        # Convertir Decimal a float para JSON
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
@tiene_permiso('Ventas', 'modificar')
def api_aprobar_pago(factura_id):
    try:
        empleado_id = _obtener_id_empleado()
        if not empleado_id:
            return jsonify({"success": False, "error": "Empleado no identificado"}), 400
        
        modelo = ValidacionPagosModel()
        
        # Actualizar la fecha de pago primero
        modelo.actualizar_fecha_pago(factura_id)
        
        # Luego aprobar el pago
        resultado = modelo.aprobar_pago(factura_id, empleado_id)
        
        if resultado["success"]:
            registrar_en_bitacora(
                accion="Aprobar pago",
                descripcion=f"Se aprobó el pago de la factura ID: {factura_id}",
                usuario_id=_usuario_actual(),
                modulo_nombre="Ventas"
            )
            return jsonify({"success": True, "mensaje": "Pago aprobado correctamente", "fecha_aprobacion": datetime.now().isoformat()})
        else:
            return jsonify({"success": False, "error": resultado.get("error", "Error al aprobar")}), 500
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@validacion_pagos_blueprint.route("/api/validacion-pagos/rechazar/<factura_id>", methods=["POST"])
@jwt_required
@tiene_permiso('Ventas', 'modificar')
def api_rechazar_pago(factura_id):
    try:
        datos = request.get_json(silent=True) or {}
        motivo = datos.get("motivo", "")
        
        if not motivo:
            return jsonify({"success": False, "error": "Debe especificar un motivo"}), 400
        
        empleado_id = _obtener_id_empleado()
        if not empleado_id:
            return jsonify({"success": False, "error": "Empleado no identificado"}), 400
        
        modelo = ValidacionPagosModel()
        resultado = modelo.rechazar_pago(factura_id, empleado_id, motivo)
        
        if resultado["success"]:
            registrar_en_bitacora(
                accion="Rechazar pago",
                descripcion=f"Se rechazó el pago de la factura ID: {factura_id} - Motivo: {motivo}",
                usuario_id=_usuario_actual(),
                modulo_nombre="Ventas"
            )
            return jsonify({"success": True, "mensaje": "Pago rechazado"})
        else:
            return jsonify({"success": False, "error": resultado.get("error", "Error al rechazar")}), 500
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500