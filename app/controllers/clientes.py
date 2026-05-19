from flask import Blueprint, jsonify, render_template, request
import mysql.connector

from app.models.clientes import GestionClientes
from app.utils.decorators import jwt_required

clientes_blueprint = Blueprint("clientes", __name__)


def _respuesta_error(mensaje, status=400):
    return jsonify({"success": False, "error": mensaje}), status


def _respuesta_por_excepcion(error):
    if isinstance(error, (ValueError, TypeError)):
        return _respuesta_error("Hay datos invalidos en la solicitud.", 400)

    if isinstance(error, mysql.connector.IntegrityError):
        errno = getattr(error, "errno", None)
        mensajes = {
            1062: "Ya existe un registro con esos datos.",
            1048: "Hay campos obligatorios sin completar.",
            1451: "No se puede eliminar porque el registro esta siendo usado.",
            1452: "La relacion indicada no existe o no es valida.",
        }
        return _respuesta_error(
            mensajes.get(errno, "No se pudo guardar la informacion por una restriccion de datos."),
            409,
        )

    if isinstance(error, mysql.connector.DataError):
        return _respuesta_error("El formato o tamaño de los datos no es valido.", 400)

    if isinstance(error, mysql.connector.ProgrammingError):
        return _respuesta_error("Ocurrio un error interno al procesar la solicitud.", 500)

    if isinstance(error, mysql.connector.OperationalError):
        return _respuesta_error("No fue posible conectar con la base de datos en este momento.", 503)

    if isinstance(error, mysql.connector.DatabaseError):
        return _respuesta_error("Se produjo un error al consultar la base de datos.", 500)

    return _respuesta_error("Ocurrio un error inesperado.", 500)


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
    cedula = (datos.get("cedula") or "").strip()
    nombre = (datos.get("nombre") or "").strip()
    apellido = (datos.get("apellido") or "").strip()
    celular = (datos.get("celular") or "").strip()
    correo = (datos.get("correo") or "").strip()
    direccion = (datos.get("direccion") or "").strip()
    tipo = (datos.get("tipo") or "").strip()

    if not cedula or not nombre or not apellido or not celular:
        return _respuesta_error("Cédula, nombre, apellido y celular son obligatorios.")

    if not cedula.isdigit():
        return _respuesta_error("La cédula debe contener solo números.")

    modelo = GestionClientes()
    try:
        nuevo_id = modelo.crear_cliente(int(cedula), nombre, apellido, celular, correo, direccion, tipo)
        return jsonify({"success": True, "message": "Cliente creado.", "id": nuevo_id})
    except Exception as error:
        return _respuesta_por_excepcion(error)


@clientes_blueprint.route("/api/clientes/<int:cliente_id>", methods=["PUT"])
@jwt_required
def actualizar_cliente(cliente_id):
    datos = request.get_json(silent=True) or {}
    cedula = (datos.get("cedula") or "").strip()
    nombre = (datos.get("nombre") or "").strip()
    apellido = (datos.get("apellido") or "").strip()
    celular = (datos.get("celular") or "").strip()
    correo = (datos.get("correo") or "").strip()
    direccion = (datos.get("direccion") or "").strip()
    tipo = (datos.get("tipo") or "").strip()

    if not cedula or not nombre or not apellido or not celular:
        return _respuesta_error("Cédula, nombre, apellido y celular son obligatorios.")

    if not cedula.isdigit():
        return _respuesta_error("La cédula debe contener solo números.")

    modelo = GestionClientes()
    cliente_existente = modelo.obtener_cliente_por_id(cliente_id)
    if not cliente_existente:
        return _respuesta_error("Cliente no encontrado.", 404)

    try:
        modelo.actualizar_cliente(
            cliente_id,
            int(cedula),
            nombre,
            apellido,
            celular,
            correo,
            direccion,
            tipo,
        )
        return jsonify({"success": True, "message": "Cliente actualizado."})
    except Exception as error:
        return _respuesta_por_excepcion(error)


@clientes_blueprint.route("/api/clientes/<int:cliente_id>", methods=["DELETE"])
@jwt_required
def eliminar_cliente(cliente_id):
    modelo = GestionClientes()
    cliente_existente = modelo.obtener_cliente_por_id(cliente_id)
    if not cliente_existente:
        return _respuesta_error("Cliente no encontrado.", 404)

    try:
        modelo.eliminar_cliente(cliente_id)
        return jsonify({"success": True, "message": "Cliente eliminado."})
    except Exception as error:
        return _respuesta_por_excepcion(error)
