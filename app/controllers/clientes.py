from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.clientes import Clientes, Persona_natural, Cliente_juridico
from app.models.bitacora import registrar_en_bitacora

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
    
    cliente_model = Persona_natural(
        Cedula_cliente=Id_cliente,
        Nombre_cliente=nombre_cliente,
        Apellido_cliente=apellido_cliente,
        Direccion_cliente=direccion_cliente,
        Telefono_cliente=telefono_cliente,
        Correo_cliente=correo_cliente
    )
    mensaje = cliente_model.registrar_persona_natural()

    if "exitosamente" in mensaje:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        registrar_en_bitacora(
            accion="Registrar cliente natural",
            descripcion=f"Se registró el cliente natural: {Id_cliente} - {nombre_cliente} {apellido_cliente}",
            usuario_id=usuario_id,
            modulo_nombre="Clientes"
        )
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
    
    cliente_model = Persona_natural(
        Cedula_cliente=cedula,
        Nombre_cliente=nombre_cliente,
        Apellido_cliente=apellido_cliente,
        Direccion_cliente=direccion_cliente,
        Telefono_cliente=telefono_cliente,
        Correo_cliente=correo_cliente
    )
    mensaje = cliente_model.actualizar_persona_natural()
    
    if "exitosamente" in mensaje:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        registrar_en_bitacora(
            accion="Actualizar cliente natural",
            descripcion=f"Se actualizó el cliente natural: {cedula} - {nombre_cliente} {apellido_cliente}",
            usuario_id=usuario_id,
            modulo_nombre="Clientes"
        )
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
    
    cliente_model = Cliente_juridico(
        Id_cliente=Id_cliente,
        Razon_social=razon_social,
        RIF=rif,
        Direccion_cliente=direccion_cliente,
        Telefono_cliente=telefono_cliente,
        Correo_cliente=correo_cliente
    )
    mensaje = cliente_model.registrar_cliente_juridico()

    if "exitosamente" in mensaje:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        registrar_en_bitacora(
            accion="Registrar cliente jurídico",
            descripcion=f"Se registró el cliente jurídico: {Id_cliente} - {razon_social}",
            usuario_id=usuario_id,
            modulo_nombre="Clientes"
        )
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
    
    cliente_model = Cliente_juridico(
        Id_cliente=id_cliente,
        Razon_social=razon_social,
        RIF=rif,
        Direccion_cliente=direccion_cliente,
        Telefono_cliente=telefono_cliente,
        Correo_cliente=correo_cliente
    )
    mensaje = cliente_model.actualizar_cliente_juridico()
    
    if "exitosamente" in mensaje:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        registrar_en_bitacora(
            accion="Actualizar cliente jurídico",
            descripcion=f"Se actualizó el cliente jurídico: {id_cliente} - {razon_social}",
            usuario_id=usuario_id,
            modulo_nombre="Clientes"
        )
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

    cliente_model_temp = Clientes()
    cliente_existente = cliente_model_temp.obtener_cliente_por_id(id_cliente)
    nombre_cliente = cliente_existente.get("nombre_cliente") if cliente_existente else id_cliente

    cliente_model = Clientes(ID_cliente=id_cliente)
    mensaje = cliente_model.eliminar_cliente()
    
    if "exitosamente" in mensaje:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        registrar_en_bitacora(
            accion="Eliminar cliente",
            descripcion=f"Se eliminó el cliente ID: {id_cliente} - Nombre: {nombre_cliente}",
            usuario_id=usuario_id,
            modulo_nombre="Clientes"
        )
        return jsonify({"success": True, "message": mensaje}), 200
    else:
        return jsonify({"success": False, "message": mensaje}), 400