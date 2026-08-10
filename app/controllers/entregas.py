from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso, solo_roles
from app.models.entrega import EntregaModel
from app.models.personal_delivery import PersonalDeliveryModel
from app.utils.validators import validar_numero, validar_texto, validar_texto_numero
import traceback

entregas_blueprint = Blueprint("entregas", __name__)


# ==================== PÁGINAS ====================

@entregas_blueprint.route("/entregas")
@jwt_required
@solo_roles(['admin', 'ventas'])
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
        
        # Validaciones
        error = validar_numero(cedula, 6, 9, "Cédula")
        if error:
            return jsonify({"success": False, "error": error}), 400
        
        error = validar_texto(nombre, 1, 50, "Nombre")
        if error:
            return jsonify({"success": False, "error": error}), 400
        
        error = validar_texto(apellido, 1, 50, "Apellido")
        if error:
            return jsonify({"success": False, "error": error}), 400
        
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
        
        modelo = PersonalDeliveryModel(
            cedula=cedula,
            nombre=nombre,
            apellido=apellido,
            usuario_id=usuario_id
        )
        mensaje = modelo.agregar_personal()
        
        if "exitosamente" in mensaje:
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
        
        # Validaciones
        error = validar_numero(cedula, 6, 9, "Cédula")
        if error:
            return jsonify({"success": False, "error": error}), 400
        
        error = validar_texto(nombre, 1, 50, "Nombre")
        if error:
            return jsonify({"success": False, "error": error}), 400
        
        error = validar_texto(apellido, 1, 50, "Apellido")
        if error:
            return jsonify({"success": False, "error": error}), 400
        
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
        
        modelo = PersonalDeliveryModel(
            cedula=cedula,
            nombre=nombre,
            apellido=apellido,
            usuario_id=usuario_id
        )
        mensaje = modelo.actualizar_personal()
        
        if "exitosamente" in mensaje:
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
        error = validar_numero(cedula, 6, 9, "Cédula")
        if error:
            return jsonify({"success": False, "error": error}), 400
        
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
        
        modelo = PersonalDeliveryModel(
            cedula=cedula,
            usuario_id=usuario_id
        )
        mensaje = modelo.eliminar_personal()
        
        if "exitosamente" in mensaje:
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
        
        # Validaciones
        error = validar_texto_numero(factura_id, 1, 50, "Factura")
        if error:
            return jsonify({"success": False, "error": error}), 400
        
        error = validar_numero(cedula_delivery, 6, 9, "Cédula del delivery")
        if error:
            return jsonify({"success": False, "error": error}), 400
        
        error = validar_texto_numero(direccion, 1, 255, "Dirección")
        if error:
            return jsonify({"success": False, "error": error}), 400
        
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
        
        modelo = EntregaModel(
            factura_id=factura_id,
            cedula_delivery=cedula_delivery,
            direccion=direccion,
            estado=estado,
            usuario_id=usuario_id
        )
        entrega_id = modelo.registrar_entrega()
        
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
        
        # Validaciones
        error = validar_texto_numero(entrega_id, 1, 50, "ID de entrega")
        if error:
            return jsonify({"success": False, "error": error}), 400
        
        error = validar_texto_numero(direccion, 1, 255, "Dirección")
        if error:
            return jsonify({"success": False, "error": error}), 400
        
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
        
        modelo = EntregaModel(
            entrega_id=entrega_id,
            direccion=direccion,
            estado=estado,
            usuario_id=usuario_id
        )
        mensaje = modelo.actualizar_entrega()
        
        if "exitosamente" in mensaje:
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
        error = validar_texto_numero(entrega_id, 1, 50, "ID de entrega")
        if error:
            return jsonify({"success": False, "error": error}), 400
        
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
        
        modelo = EntregaModel(
            entrega_id=entrega_id,
            usuario_id=usuario_id
        )
        mensaje = modelo.eliminar_entrega()
        
        if "exitosamente" in mensaje:
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