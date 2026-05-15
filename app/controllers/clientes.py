from flask import Blueprint, jsonify, render_template, request

from app.models.clientes import GestionClientes
from app.utils.decorators import jwt_required

clientes_blueprint = Blueprint("clientes", __name__)


def _respuesta_error(mensaje, status=400):
    return jsonify({"success": False, "error": mensaje}), status


@clientes_blueprint.route("/clientes", methods=["GET"])
@jwt_required
def pagina_clientes():
    return render_template(
        "clientes.html",
        show_navbar=True,
        show_notifications=True,
        active_page="clientes",
    )


@clientes_blueprint.route("/api/clientes", methods=["GET"])
@jwt_required
def listar_clientes():
    modelo = GestionClientes()
    datos = modelo.listar_clientes() or []
    return jsonify({"success": True, "clientes": datos})


@clientes_blueprint.route("/api/clientes", methods=["POST"])
@jwt_required
def crear_cliente():
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    apellido = (datos.get("apellido") or "").strip()
    celular = (datos.get("celular") or "").strip()
    correo = (datos.get("correo") or "").strip()
    direccion = (datos.get("direccion") or "").strip()
    tipo = (datos.get("tipo") or "").strip()

    if not nombre or not apellido or not celular:
        return _respuesta_error("Nombre, apellido y celular son obligatorios.")

    modelo = GestionClientes()
    try:
        nuevo_id = modelo.crear_cliente(nombre, apellido, celular, correo, direccion, tipo)
        return jsonify({"success": True, "message": "Cliente creado.", "id": nuevo_id})
    except Exception as error:
        return _respuesta_error(str(error))


@clientes_blueprint.route("/api/clientes/<int:cliente_id>", methods=["PUT"])
@jwt_required
def actualizar_cliente(cliente_id):
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    apellido = (datos.get("apellido") or "").strip()
    celular = (datos.get("celular") or "").strip()
    correo = (datos.get("correo") or "").strip()
    direccion = (datos.get("direccion") or "").strip()
    tipo = (datos.get("tipo") or "").strip()

    if not nombre or not apellido or not celular:
        return _respuesta_error("Nombre, apellido y celular son obligatorios.")

    modelo = GestionClientes()
    try:
        modelo.actualizar_cliente(cliente_id, nombre, apellido, celular, correo, direccion, tipo)
        return jsonify({"success": True, "message": "Cliente actualizado."})
    except Exception as error:
        return _respuesta_error(str(error))


@clientes_blueprint.route("/api/clientes/<int:cliente_id>", methods=["DELETE"])
@jwt_required
def eliminar_cliente(cliente_id):
    modelo = GestionClientes()
    try:
        modelo.eliminar_cliente(cliente_id)
        return jsonify({"success": True, "message": "Cliente eliminado."})
    except Exception as error:
        return _respuesta_error(str(error))
