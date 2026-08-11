from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.clientes import Clientes, Persona_natural, Cliente_juridico
import re

clientes_blueprint = Blueprint("clientes", __name__)


@clientes_blueprint.route("/clientes", methods=["GET"])
@jwt_required
@tiene_permiso('Clientes', 'consultar')
def pagina_clientes():
    return render_template(
        "clientes.html",
        show_navbar=True,
        show_notifications=True,
        active_page="clientes",
    )


@clientes_blueprint.route("/api/clientes", methods=["GET"])
@jwt_required
@tiene_permiso('Clientes', 'consultar')
def api_listar_clientes():
    cliente_model = Clientes()
    clientes = cliente_model.listar_clientes() or []
    return jsonify({"success": True, "clientes": clientes})


@clientes_blueprint.route("/api/clientes/<string:id_cliente>", methods=["GET"])
@jwt_required
@tiene_permiso('Clientes', 'consultar')
def api_obtener_cliente(id_cliente):
    id_cliente = (id_cliente or "").strip()
    if not id_cliente:
        return jsonify({"success": False, "message": "La cédula del cliente es obligatoria."}), 400

    cliente_model = Clientes(ID_cliente=id_cliente)
    cliente = cliente_model.obtener_datos_cliente_completo(cliente_id=id_cliente)
    if not cliente:
        return jsonify({"success": False, "message": "Cliente no encontrado."}), 404
    return jsonify({"success": True, "cliente": cliente})


@clientes_blueprint.route("/api/clientes", methods=["POST"])
@jwt_required
@tiene_permiso('Clientes', 'registrar')
def api_registrar_cliente():
    data = request.get_json(silent=True) or request.form
    Id_cliente = data.get("cedula", "").strip()
    nombre_cliente = data.get("nombre", "").strip()
    apellido_cliente = data.get("apellido", "").strip()
    direccion_cliente = data.get("direccion", "").strip()
    telefono_cliente = data.get("celular", "").strip()
    correo_cliente = data.get("correo", "").strip()
    
    if not Id_cliente or not nombre_cliente or not apellido_cliente or not telefono_cliente:
        return jsonify({"success": False, "message": "Cédula, nombre, apellido y celular son obligatorios."}), 400

    # Validar cédula: 8 dígitos, solo números
    if not re.match(r"^\d{8}$", Id_cliente):
        return jsonify({"success": False, "message": "La cédula debe tener exactamente 8 dígitos numéricos."}), 400

    # Validar celular: 11 dígitos, solo números
    if not re.match(r"^\d{11}$", telefono_cliente):
        return jsonify({"success": False, "message": "El celular debe tener exactamente 11 dígitos numéricos."}), 400

    # Validar correo si se proporciona
    if correo_cliente and not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", correo_cliente):
        return jsonify({"success": False, "message": "El correo electrónico no es válido."}), 400

    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
    cliente_model = Persona_natural(
        Cedula_cliente=Id_cliente,
        Nombre_cliente=nombre_cliente,
        Apellido_cliente=apellido_cliente,
        Direccion_cliente=direccion_cliente,
        Telefono_cliente=telefono_cliente,
        Correo_cliente=correo_cliente,
        usuario_id=usuario_actual_id
    )
    mensaje = cliente_model.registrar_persona_natural()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje, "id": Id_cliente}), 201
    else:
        return jsonify({"success": False, "message": mensaje}), 400


@clientes_blueprint.route("/api/clientes/natural", methods=["POST"])
@jwt_required
@tiene_permiso('Clientes', 'registrar')
def api_registrar_persona_natural():
    data = request.get_json(silent=True) or request.form
    Id_cliente = data.get("Id_cliente", "").strip()
    nombre_cliente = data.get("nombre_cliente", "").strip()
    apellido_cliente = data.get("apellido_cliente", "").strip()
    direccion_cliente = data.get("direccion_cliente", "").strip()
    telefono_cliente = data.get("telefono_cliente", "").strip()
    correo_cliente = data.get("correo_cliente", "").strip()
    
    # Obtener usuario actual para bitácora
    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
    
    cliente_model = Persona_natural(
        Cedula_cliente=Id_cliente,
        Nombre_cliente=nombre_cliente,
        Apellido_cliente=apellido_cliente,
        Direccion_cliente=direccion_cliente,
        Telefono_cliente=telefono_cliente,
        Correo_cliente=correo_cliente,
        usuario_id=usuario_actual_id
    )
    mensaje = cliente_model.registrar_persona_natural()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 201
    else:
        return jsonify({"success": False, "message": mensaje}), 400


@clientes_blueprint.route("/api/clientes/natural/<string:cedula>", methods=["PUT"])
@jwt_required
@tiene_permiso('Clientes', 'modificar')
def api_actualizar_persona_natural(cedula):
    data = request.get_json(silent=True) or request.form
    nombre_cliente = data.get("nombre_cliente", "").strip()
    apellido_cliente = data.get("apellido_cliente", "").strip()
    direccion_cliente = data.get("direccion_cliente", "").strip()
    telefono_cliente = data.get("telefono_cliente", "").strip()
    correo_cliente = data.get("correo_cliente", "").strip()
    
    if not cedula:
        return jsonify({"success": False, "message": "La cédula del cliente es obligatoria."}), 400
    if not nombre_cliente:
        return jsonify({"success": False, "message": "El nombre del cliente es obligatorio."}), 400
    
    # Obtener usuario actual para bitácora
    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
    
    cliente_model = Persona_natural(
        Cedula_cliente=cedula,
        Nombre_cliente=nombre_cliente,
        Apellido_cliente=apellido_cliente,
        Direccion_cliente=direccion_cliente,
        Telefono_cliente=telefono_cliente,
        Correo_cliente=correo_cliente,
        usuario_id=usuario_actual_id
    )
    mensaje = cliente_model.actualizar_persona_natural()
    
    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200
    else:
        return jsonify({"success": False, "message": mensaje}), 400


@clientes_blueprint.route("/api/clientes/juridico", methods=["POST"])
@jwt_required
@tiene_permiso('Clientes', 'registrar')
def api_registrar_cliente_juridico():
    data = request.get_json(silent=True) or request.form
    Id_cliente = data.get("Id_cliente", "").strip()
    razon_social = data.get("razon_social", "").strip()
    rif = data.get("rif", "").strip()
    direccion_cliente = data.get("direccion_cliente", "").strip()
    telefono_cliente = data.get("telefono_cliente", "").strip()
    correo_cliente = data.get("correo_cliente", "").strip()
    
    # Validación de RIF en el endpoint
    patron_rif = r'^[JE]-\d{8}-\d$'
    if not re.match(patron_rif, rif):
        return jsonify({
            "success": False, 
            "message": "El RIF debe tener el formato: J-12345678-9 o E-12345678-9"
        }), 400
    
    # Validar que la razón social no esté vacía
    if not razon_social:
        return jsonify({
            "success": False,
            "message": "La razón social es obligatoria."
        }), 400
    
    # Validar teléfono: 11 dígitos, solo números
    if not re.match(r"^\d{11}$", telefono_cliente):
        return jsonify({
            "success": False,
            "message": "El teléfono debe tener exactamente 11 dígitos numéricos."
        }), 400
    
    # Validar correo si se proporciona
    if correo_cliente and not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", correo_cliente):
        return jsonify({
            "success": False,
            "message": "El correo electrónico no es válido."
        }), 400
    
    # Obtener usuario actual para bitácora
    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
    
    cliente_model = Cliente_juridico(
        Id_cliente=Id_cliente,
        Razon_social=razon_social,
        RIF=rif,
        Direccion_cliente=direccion_cliente,
        Telefono_cliente=telefono_cliente,
        Correo_cliente=correo_cliente,
        usuario_id=usuario_actual_id
    )
    mensaje = cliente_model.registrar_cliente_juridico()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 201
    else:
        return jsonify({"success": False, "message": mensaje}), 400


@clientes_blueprint.route("/api/clientes/juridico/<string:id_cliente>", methods=["PUT"])
@jwt_required
@tiene_permiso('Clientes', 'modificar')
def api_actualizar_cliente_juridico(id_cliente):
    data = request.get_json(silent=True) or request.form
    razon_social = data.get("razon_social", "").strip()
    rif = data.get("rif", "").strip()
    direccion_cliente = data.get("direccion_cliente", "").strip()
    telefono_cliente = data.get("telefono_cliente", "").strip()
    correo_cliente = data.get("correo_cliente", "").strip()
    
    if not id_cliente:
        return jsonify({"success": False, "message": "El ID del cliente es obligatorio."}), 400
    if not razon_social:
        return jsonify({"success": False, "message": "La razón social del cliente es obligatoria."}), 400
    
    # Validación de RIF en el endpoint
    patron_rif = r'^[JE]-\d{8}-\d$'
    if not re.match(patron_rif, rif):
        return jsonify({
            "success": False, 
            "message": "El RIF debe tener el formato: J-12345678-9 o E-12345678-9"
        }), 400
    
    # Validar teléfono: 11 dígitos, solo números
    if telefono_cliente and not re.match(r"^\d{11}$", telefono_cliente):
        return jsonify({
            "success": False,
            "message": "El teléfono debe tener exactamente 11 dígitos numéricos."
        }), 400
    
    # Validar correo si se proporciona
    if correo_cliente and not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", correo_cliente):
        return jsonify({
            "success": False,
            "message": "El correo electrónico no es válido."
        }), 400
    
    # Obtener usuario actual para bitácora
    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
    
    cliente_model = Cliente_juridico(
        Id_cliente=id_cliente,
        Razon_social=razon_social,
        RIF=rif,
        Direccion_cliente=direccion_cliente,
        Telefono_cliente=telefono_cliente,
        Correo_cliente=correo_cliente,
        usuario_id=usuario_actual_id
    )
    mensaje = cliente_model.actualizar_cliente_juridico()
    
    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200
    else:
        return jsonify({"success": False, "message": mensaje}), 400


@clientes_blueprint.route("/api/clientes/<string:id_cliente>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Clientes', 'eliminar')
def api_eliminar_cliente(id_cliente):
    id_cliente = (id_cliente or "").strip()
    if not id_cliente:
        return jsonify({"success": False, "message": "El ID del cliente es obligatorio."}), 400

    # Obtener usuario actual para bitácora
    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    cliente_model = Clientes(
        ID_cliente=id_cliente,
        usuario_id=usuario_actual_id
    )
    mensaje = cliente_model.eliminar_cliente()
    
    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200
    else:
        return jsonify({"success": False, "message": mensaje}), 400