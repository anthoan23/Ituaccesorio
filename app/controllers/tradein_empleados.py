from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso, solo_roles
from app.models.tradein_empleados import TradeInEmpleados
from app.models.bitacora import registrar_en_bitacora
import traceback

tradein_empleados_blueprint = Blueprint("tradein_empleados", __name__)


@tradein_empleados_blueprint.route("/empleados/tradein")
@jwt_required
@solo_roles(['admin', 'ventas', 'tecnico'])
def pagina_tradein_empleados():
    """Panel de gestión de Trade-In para empleados"""
    return render_template(
        "tradein_empleados.html",
        show_navbar=True,
        show_notifications=True,
        active_page="tradein_empleados"
    )


@tradein_empleados_blueprint.route("/api/tradein/pendientes", methods=["GET"])
@jwt_required
@tiene_permiso('Trade-in', 'consultar')
def api_tradein_pendientes():
    """Obtiene los trade-ins pendientes de evaluación"""
    try:
        modelo = TradeInEmpleados()
        resultados = modelo.obtener_trade_ins_pendientes()
        return jsonify({"success": True, "tradeins": resultados})
    except Exception as e:
        print(f"Error en api_tradein_pendientes: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@tradein_empleados_blueprint.route("/api/tradein/evaluados", methods=["GET"])
@jwt_required
@tiene_permiso('Trade-in', 'consultar')
def api_tradein_evaluados():
    """Obtiene los trade-ins ya evaluados"""
    try:
        modelo = TradeInEmpleados()
        resultados = modelo.obtener_trade_ins_evaluados()
        return jsonify({"success": True, "tradeins": resultados})
    except Exception as e:
        print(f"Error en api_tradein_evaluados: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@tradein_empleados_blueprint.route("/api/tradein/<tradein_id>/detalle", methods=["GET"])
@jwt_required
@tiene_permiso('Trade-in', 'consultar')
def api_tradein_detalle(tradein_id):
    """Obtiene el detalle completo de un trade-in"""
    try:
        modelo = TradeInEmpleados()
        detalle = modelo.obtener_detalle_trade_in(tradein_id)
        tests = modelo.obtener_tests_trade_in(tradein_id)
        fotos = modelo.obtener_fotos_trade_in(tradein_id)
        
        return jsonify({
            "success": True,
            "detalle": detalle,
            "tests": tests,
            "fotos": fotos
        })
    except Exception as e:
        print(f"Error en api_tradein_detalle: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@tradein_empleados_blueprint.route("/api/tradein/evaluar/<tradein_id>", methods=["POST"])
@jwt_required
@tiene_permiso('Trade-in', 'modificar')
def api_evaluar_tradein(tradein_id):
    """Evalúa un trade-in asignando un valor de cotización"""
    try:
        datos = request.get_json(silent=True) or {}
        
        valor = datos.get("valor")
        fallas = datos.get("fallas", [])
        observaciones = datos.get("observaciones", "")
        
        if valor is None:
            return jsonify({"success": False, "error": "El valor de cotización es obligatorio"}), 400
        
        # Obtener cédula del empleado desde el token
        empleado_id = g.user.get("cedula") if isinstance(g.user, dict) else getattr(g.user, "cedula", None)
        empleado_id = str(empleado_id) if empleado_id else None
        
        if not empleado_id:
            return jsonify({"success": False, "error": "Empleado no identificado"}), 400
        
        modelo = TradeInEmpleados()
        resultado = modelo.evaluar_trade_in(tradein_id, float(valor), empleado_id, fallas, observaciones)
        
        if resultado["success"]:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            
            registrar_en_bitacora(
                accion="Evaluar Trade-in",
                descripcion=f"Se evaluó el trade-in ID: {tradein_id} con valor: {valor}",
                usuario_id=usuario_id,
                modulo_nombre="Trade-in"
            )
            return jsonify({"success": True, "mensaje": resultado["message"]})
        else:
            return jsonify({"success": False, "error": resultado.get("error", "Error al evaluar")}), 500
    except Exception as e:
        print(f"Error en api_evaluar_tradein: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@tradein_empleados_blueprint.route("/api/tradein/estadisticas", methods=["GET"])
@jwt_required
@tiene_permiso('Trade-in', 'consultar')
def api_tradein_estadisticas():
    """Obtiene estadísticas de trade-ins"""
    try:
        modelo = TradeInEmpleados()
        estadisticas = modelo.obtener_estadisticas()
        return jsonify({"success": True, "estadisticas": estadisticas})
    except Exception as e:
        print(f"Error en api_tradein_estadisticas: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@tradein_empleados_blueprint.route("/api/tradein/equipos", methods=["GET"])
@jwt_required
@tiene_permiso('Trade-in', 'consultar')
def api_equipos_disponibles():
    """Obtiene equipos disponibles para trade-in"""
    try:
        modelo = TradeInEmpleados()
        equipos = modelo.obtener_equipos_disponibles()
        return jsonify({"success": True, "equipos": equipos})
    except Exception as e:
        print(f"Error en api_equipos_disponibles: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@tradein_empleados_blueprint.route("/api/tradein/catalogo-fallas", methods=["GET"])
@jwt_required
@tiene_permiso('Trade-in', 'consultar')
def api_catalogo_fallas():
    """Obtiene el catálogo de fallas para evaluación"""
    try:
        modelo = TradeInEmpleados()
        fallas = modelo.obtener_catalogo_fallas()
        return jsonify({"success": True, "fallas": fallas})
    except Exception as e:
        print(f"Error en api_catalogo_fallas: {e}")
        return jsonify({"success": False, "error": str(e)}), 500