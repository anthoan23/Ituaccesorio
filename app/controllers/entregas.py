from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso, solo_roles
from app.models.entrega import EntregaModel
from app.models.personal_delivery import PersonalDeliveryModel
import traceback

entregas_blueprint = Blueprint("entregas", __name__)


def _obtener_usuario_id():
    return g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", None)


# ==================== PÁGINAS ====================

@entregas_blueprint.route("/entregas")
@jwt_required
@solo_roles(['admin', 'ventas'])
def pagina_entregas():
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
    try:
        data = request.get_json(silent=True) or request.form
        usuario_id = _obtener_usuario_id()

        modelo = PersonalDeliveryModel(
            cedula=data.get("cedula", "").strip() if isinstance(data.get("cedula"), str) else data.get("cedula"),
            nombre=data.get("nombre", "").strip() if isinstance(data.get("nombre"), str) else data.get("nombre"),
            apellido=data.get("apellido", "").strip() if isinstance(data.get("apellido"), str) else data.get("apellido"),
            usuario_id=usuario_id
        )
        mensaje = modelo.agregar_personal()

        if "exitosamente" in mensaje:
            return jsonify({"success": True, "message": mensaje}), 201

        status = 500 if mensaje.startswith("Error") else 400
        return jsonify({"success": False, "error": mensaje}), status
    except Exception as e:
        print(f"Error en api_crear_personal: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@entregas_blueprint.route("/api/personal-delivery/<cedula>", methods=["PUT"])
@jwt_required
@tiene_permiso('Entregas', 'modificar')
def api_actualizar_personal(cedula):
    try:
        data = request.get_json(silent=True) or request.form
        usuario_id = _obtener_usuario_id()

        modelo = PersonalDeliveryModel(
            cedula=cedula,
            nombre=data.get("nombre", "").strip() if isinstance(data.get("nombre"), str) else data.get("nombre"),
            apellido=data.get("apellido", "").strip() if isinstance(data.get("apellido"), str) else data.get("apellido"),
            usuario_id=usuario_id
        )
        mensaje = modelo.actualizar_personal()

        if "exitosamente" in mensaje:
            return jsonify({"success": True, "message": mensaje}), 200

        status = 500 if mensaje.startswith("Error") else 400
        return jsonify({"success": False, "error": mensaje}), status
    except Exception as e:
        print(f"Error en api_actualizar_personal: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@entregas_blueprint.route("/api/personal-delivery/<cedula>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Entregas', 'eliminar')
def api_eliminar_personal(cedula):
    try:
        usuario_id = _obtener_usuario_id()

        modelo = PersonalDeliveryModel(cedula=cedula, usuario_id=usuario_id)
        mensaje = modelo.eliminar_personal()

        if "exitosamente" in mensaje:
            return jsonify({"success": True, "message": mensaje}), 200

        status = 500 if mensaje.startswith("Error") else 400
        return jsonify({"success": False, "error": mensaje}), status
    except Exception as e:
        print(f"Error en api_eliminar_personal: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== API ENTREGAS ====================

@entregas_blueprint.route("/api/entregas", methods=["GET"])
@jwt_required
@tiene_permiso('Entregas', 'consultar')
def api_listar_entregas():
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
    try:
        data = request.get_json(silent=True) or request.form
        usuario_id = _obtener_usuario_id()

        # Validaciones (factura, delivery, dirección, estado) en EntregaModel
        modelo = EntregaModel(
            factura_id=data.get("factura_id", "").strip() if isinstance(data.get("factura_id"), str) else data.get("factura_id"),
            cedula_delivery=data.get("cedula_delivery", "").strip() if isinstance(data.get("cedula_delivery"), str) else data.get("cedula_delivery"),
            direccion=data.get("direccion", "").strip() if isinstance(data.get("direccion"), str) else data.get("direccion"),
            estado=data.get("estado", 0),
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
    try:
        data = request.get_json(silent=True) or request.form
        usuario_id = _obtener_usuario_id()

        modelo = EntregaModel(
            entrega_id=entrega_id,
            direccion=data.get("direccion", "").strip() if isinstance(data.get("direccion"), str) else data.get("direccion"),
            estado=data.get("estado", 0),
            usuario_id=usuario_id
        )
        mensaje = modelo.actualizar_entrega()

        if "exitosamente" in mensaje:
            return jsonify({"success": True, "message": mensaje}), 200

        status = 500 if mensaje.startswith("Error") else 400
        return jsonify({"success": False, "error": mensaje}), status
    except Exception as e:
        print(f"Error en api_actualizar_entrega: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@entregas_blueprint.route("/api/entregas/<string:entrega_id>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Entregas', 'eliminar')
def api_eliminar_entrega(entrega_id):
    try:
        usuario_id = _obtener_usuario_id()

        modelo = EntregaModel(entrega_id=entrega_id, usuario_id=usuario_id)
        mensaje = modelo.eliminar_entrega()

        if "exitosamente" in mensaje:
            return jsonify({"success": True, "message": mensaje}), 200

        status = 500 if mensaje.startswith("Error") else 400
        return jsonify({"success": False, "error": mensaje}), status
    except Exception as e:
        print(f"Error en api_eliminar_entrega: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@entregas_blueprint.route("/api/facturas-pendientes", methods=["GET"])
@jwt_required
@tiene_permiso('Entregas', 'consultar')
def api_facturas_pendientes():
    try:
        modelo = EntregaModel()
        facturas = modelo.obtener_facturas_pendientes()
        return jsonify({"success": True, "facturas": facturas})
    except Exception as e:
        print(f"Error en api_facturas_pendientes: {e}")
        return jsonify({"success": False, "error": str(e)}), 500