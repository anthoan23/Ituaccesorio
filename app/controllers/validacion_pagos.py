from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso, solo_roles
from app.models.validacion_pagos import ValidacionPagosModel
from datetime import datetime
import traceback

validacion_pagos_blueprint = Blueprint("validacion_pagos", __name__)


def _obtener_empleado_y_usuario():
    if isinstance(g.user, dict):
        empleado_id = g.user.get("cedula")
        usuario_id = g.user.get("id")
    else:
        empleado_id = getattr(g.user, "cedula", None)
        usuario_id = getattr(g.user, "id", None)
    return (
        str(empleado_id) if empleado_id else None,
        str(usuario_id) if usuario_id else None
    )


# ==================== PÁGINAS ====================

@validacion_pagos_blueprint.route("/admin/validar-pagos")
@jwt_required
@solo_roles(['admin', 'ventas'])
def pagina_validar_pagos():
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
        modelo = ValidacionPagosModel(factura_id=factura_id)
        detalle = modelo.obtener_detalle_venta()
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
        empleado_id, usuario_id = _obtener_empleado_y_usuario()

        if not empleado_id:
            return jsonify({"success": False, "error": "Empleado no identificado - cédula no encontrada en token"}), 400

        modelo = ValidacionPagosModel(
            factura_id=factura_id,
            empleado_id=empleado_id,
            usuario_id=usuario_id
        )

        modelo.actualizar_fecha_pago()
        resultado = modelo.aprobar_pago()

        if resultado["success"]:
            return jsonify({"success": True, "mensaje": "Pago aprobado correctamente", "fecha_aprobacion": datetime.now().isoformat()})

        error_msg = resultado.get("error", "Error al aprobar")
        status = 500 if error_msg.startswith("Error") else 400
        return jsonify({"success": False, "error": error_msg}), status
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
        motivo = datos.get("motivo", "").strip() if isinstance(datos.get("motivo"), str) else datos.get("motivo", "")

        empleado_id, usuario_id = _obtener_empleado_y_usuario()

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

        error_msg = resultado.get("error", "Error al rechazar")
        status = 500 if error_msg.startswith("Error") else 400
        return jsonify({"success": False, "error": error_msg}), status
    except Exception as e:
        print(f"Error en api_rechazar_pago: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== REPORTES ====================

@validacion_pagos_blueprint.route("/api/validacion-pagos/reportes", methods=["POST"])
@jwt_required
@tiene_permiso('Validación Pagos', 'consultar')
def api_reportes_pagos():
    datos = request.get_json(silent=True) or {}

    filtros = {
        "q": datos.get("q", "").strip() if isinstance(datos.get("q"), str) else datos.get("q"),
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

    error_msg = resultado.get("error", "Error al generar reporte")
    status = 500 if error_msg.startswith("Error") else 400
    return jsonify({"success": False, "error": error_msg}), status


@validacion_pagos_blueprint.route("/api/validacion-pagos/detalle-venta/<factura_id>", methods=["GET"])
@jwt_required
@tiene_permiso('Validación Pagos', 'consultar')
def api_detalle_venta_reporte(factura_id):
    modelo = ValidacionPagosModel(factura_id=factura_id)
    resultado = modelo.obtener_reporte_detalle_ventas()

    if resultado["success"]:
        return jsonify(resultado)

    error_msg = resultado.get("error", "Error al obtener detalle")
    status = 500 if error_msg.startswith("Error") else 400
    return jsonify({"success": False, "error": error_msg}), status


@validacion_pagos_blueprint.route("/api/validacion-pagos/metodos-pago", methods=["GET"])
@jwt_required
@tiene_permiso('Validación Pagos', 'consultar')
def api_listar_metodos_pago():
    modelo = ValidacionPagosModel()
    return jsonify({
        "success": True,
        "metodos": modelo.obtener_metodos_pago_disponibles()
    })


@validacion_pagos_blueprint.route("/api/validacion-pagos/monedas", methods=["GET"])
@jwt_required
@tiene_permiso('Validación Pagos', 'consultar')
def api_listar_monedas():
    modelo = ValidacionPagosModel()
    return jsonify({
        "success": True,
        "monedas": modelo.obtener_monedas_disponibles()
    })