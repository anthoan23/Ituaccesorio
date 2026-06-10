from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso, solo_roles
from app.models.bitacora import registrar_en_bitacora
from app.models.entrega import EntregaModel
from app.models.personal_delivery import PersonalDeliveryModel
import traceback

entregas_blueprint = Blueprint("entregas", __name__)


# ==================== PÁGINAS ====================

@entregas_blueprint.route("/entregas")
@jwt_required
@solo_roles(['admin', 'Ventas'])
def pagina_entregas():
    """Panel de gestión de entregas"""
    return render_template(
        "entregas.html",
        show_navbar=True,
        show_notifications=True,
        active_page="entregas"
    )


# ==================== API PERSONAL DELIVERY ====================

@entregas_blueprint.route("/api/personal-delivery", methods=["GET"])
@jwt_required
@tiene_permiso('Entregas', 'consultar')
def api_listar_personal():
    """Listar todo el personal de delivery"""
    try:
        modelo = PersonalDeliveryModel()
        personal = modelo.listar_personal()
        return jsonify({"success": True, "personal": personal})
    except Exception as e:
        print(f"Error en api_listar_personal: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@entregas_blueprint.route("/api/personal-delivery", methods=["POST"])
@jwt_required
@tiene_permiso('Entregas', 'registrar')
def api_crear_personal():
    """Registrar nuevo delivery"""
    try:
        data = request.get_json(silent=True) or request.form
        cedula = data.get("cedula", "").strip()
        nombre = data.get("nombre", "").strip()
        apellido = data.get("apellido", "").strip()
        
        if not cedula or not nombre or not apellido:
            return jsonify({"success": False, "error": "Cédula, nombre y apellido son obligatorios"}), 400
        
        modelo = PersonalDeliveryModel()
        mensaje = modelo.agregar_personal(cedula, nombre, apellido)
        
        if "exitosamente" in mensaje:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            
            registrar_en_bitacora(
                accion="Registrar delivery",
                descripcion=f"Se registró al delivery: {nombre} {apellido} - Cédula: {cedula}",
                usuario_id=usuario_id,
                modulo_nombre="Entregas"
            )
            return jsonify({"success": True, "message": mensaje}), 201
        else:
            return jsonify({"success": False, "error": mensaje}), 400
    except Exception as e:
        print(f"Error en api_crear_personal: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@entregas_blueprint.route("/api/personal-delivery/<cedula>", methods=["PUT"])
@jwt_required
@tiene_permiso('Entregas', 'modificar')
def api_actualizar_personal(cedula):
    """Actualizar delivery existente"""
    try:
        data = request.get_json(silent=True) or request.form
        nombre = data.get("nombre", "").strip()
        apellido = data.get("apellido", "").strip()
        
        if not nombre or not apellido:
            return jsonify({"success": False, "error": "Nombre y apellido son obligatorios"}), 400
        
        modelo = PersonalDeliveryModel()
        mensaje = modelo.actualizar_personal(cedula, nombre, apellido)
        
        if "exitosamente" in mensaje:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            
            registrar_en_bitacora(
                accion="Actualizar delivery",
                descripcion=f"Se actualizó al delivery con cédula: {cedula}",
                usuario_id=usuario_id,
                modulo_nombre="Entregas"
            )
            return jsonify({"success": True, "message": mensaje}), 200
        else:
            return jsonify({"success": False, "error": mensaje}), 400
    except Exception as e:
        print(f"Error en api_actualizar_personal: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@entregas_blueprint.route("/api/personal-delivery/<cedula>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Entregas', 'eliminar')
def api_eliminar_personal(cedula):
    """Eliminar delivery"""
    try:
        modelo = PersonalDeliveryModel()
        mensaje = modelo.eliminar_personal(cedula)
        
        if "exitosamente" in mensaje:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            
            registrar_en_bitacora(
                accion="Eliminar delivery",
                descripcion=f"Se eliminó al delivery con cédula: {cedula}",
                usuario_id=usuario_id,
                modulo_nombre="Entregas"
            )
            return jsonify({"success": True, "message": mensaje}), 200
        else:
            return jsonify({"success": False, "error": mensaje}), 400
    except Exception as e:
        print(f"Error en api_eliminar_personal: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== API ENTREGAS ====================

@entregas_blueprint.route("/api/entregas", methods=["GET"])
@jwt_required
@tiene_permiso('Entregas', 'consultar')
def api_listar_entregas():
    """Listar todas las entregas"""
    try:
        modelo = EntregaModel()
        entregas = modelo.listar_entregas()
        return jsonify({"success": True, "entregas": entregas})
    except Exception as e:
        print(f"Error en api_listar_entregas: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@entregas_blueprint.route("/api/entregas", methods=["POST"])
@jwt_required
@tiene_permiso('Entregas', 'registrar')
def api_registrar_entrega():
    """Registrar nueva entrega"""
    try:
        data = request.get_json(silent=True) or request.form
        factura_id = data.get("factura_id", "").strip()
        cedula_delivery = data.get("cedula_delivery", "").strip()
        direccion = data.get("direccion", "").strip()
        estado = int(data.get("estado", 0))
        
        if not factura_id:
            return jsonify({"success": False, "error": "La factura es obligatoria"}), 400
        if not cedula_delivery:
            return jsonify({"success": False, "error": "El delivery es obligatorio"}), 400
        if not direccion:
            return jsonify({"success": False, "error": "La dirección es obligatoria"}), 400
        
        modelo = EntregaModel()
        entrega_id = modelo.registrar_entrega(factura_id, cedula_delivery, direccion, estado)
        
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Registrar entrega",
            descripcion=f"Se registró la entrega ID: {entrega_id} para factura: {factura_id}",
            usuario_id=usuario_id,
            modulo_nombre="Entregas"
        )
        
        return jsonify({"success": True, "message": "Entrega registrada exitosamente", "id": entrega_id}), 201
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        print(f"Error en api_registrar_entrega: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@entregas_blueprint.route("/api/entregas/<string:entrega_id>", methods=["PUT"])
@jwt_required
@tiene_permiso('Entregas', 'modificar')
def api_actualizar_entrega(entrega_id):
    """Actualizar entrega existente"""
    try:
        data = request.get_json(silent=True) or request.form
        direccion = data.get("direccion", "").strip()
        estado = int(data.get("estado", 0))
        
        if not direccion:
            return jsonify({"success": False, "error": "La dirección es obligatoria"}), 400
        
        modelo = EntregaModel()
        mensaje = modelo.actualizar_entrega(entrega_id, direccion, estado)
        
        if "exitosamente" in mensaje:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            
            registrar_en_bitacora(
                accion="Actualizar entrega",
                descripcion=f"Se actualizó la entrega ID: {entrega_id}",
                usuario_id=usuario_id,
                modulo_nombre="Entregas"
            )
            return jsonify({"success": True, "message": mensaje}), 200
        else:
            return jsonify({"success": False, "error": mensaje}), 400
    except Exception as e:
        print(f"Error en api_actualizar_entrega: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@entregas_blueprint.route("/api/entregas/<string:entrega_id>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Entregas', 'eliminar')
def api_eliminar_entrega(entrega_id):
    """Eliminar entrega"""
    try:
        modelo = EntregaModel()
        mensaje = modelo.eliminar_entrega(entrega_id)
        
        if "exitosamente" in mensaje:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            
            registrar_en_bitacora(
                accion="Eliminar entrega",
                descripcion=f"Se eliminó la entrega ID: {entrega_id}",
                usuario_id=usuario_id,
                modulo_nombre="Entregas"
            )
            return jsonify({"success": True, "message": mensaje}), 200
        else:
            return jsonify({"success": False, "error": mensaje}), 400
    except Exception as e:
        print(f"Error en api_eliminar_entrega: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@entregas_blueprint.route("/api/facturas-pendientes", methods=["GET"])
@jwt_required
@tiene_permiso('Entregas', 'consultar')
def api_facturas_pendientes():
    """Obtener facturas que necesitan entrega"""
    try:
        modelo = EntregaModel()
        facturas = modelo.obtener_facturas_pendientes()
        return jsonify({"success": True, "facturas": facturas})
    except Exception as e:
        print(f"Error en api_facturas_pendientes: {e}")
        return jsonify({"success": False, "error": str(e)}), 500