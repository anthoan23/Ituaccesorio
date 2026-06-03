from flask import Blueprint, jsonify, render_template, request
from app.utils.decorators import jwt_required

from app.models.productos import Productos

productos_blueprint = Blueprint("productos", __name__)


@productos_blueprint.route("/productos", methods=["GET"])
@jwt_required
def pagina_productos():
    return render_template(
        "productos.html",
        show_navbar=True,
        show_notifications=True,
        active_page="productos",
    )


@productos_blueprint.route("/api/productos/clases", methods=["GET"])
@jwt_required
def api_listar_clases():
    modelo = Productos()
    clases = modelo.listar_clases() or []
    return jsonify({"success": True, "clases": clases})


@productos_blueprint.route("/api/productos/clases", methods=["POST"])
@jwt_required
def api_crear_clase():
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    num_i = datos.get("num_i")
    if nombre == "":
        return jsonify({"success": False, "error": "El nombre de la clase es obligatorio."}), 400

    try:
        num_i_val = int(num_i) if num_i not in (None, "") else None
    except Exception:
        return jsonify({"success": False, "error": "Num_i debe ser un número."}), 400

    modelo = Productos()
    try:
        new_id = modelo.crear_clase(nombre=nombre, num_i=num_i_val)
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/clases/<int:id_clase>", methods=["PUT"])
@jwt_required
def api_actualizar_clase(id_clase: int):
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    num_i = datos.get("num_i")
    if nombre == "":
        return jsonify({"success": False, "error": "El nombre de la clase es obligatorio."}), 400

    try:
        num_i_val = int(num_i) if num_i not in (None, "") else None
    except Exception:
        return jsonify({"success": False, "error": "Num_i debe ser un número."}), 400

    modelo = Productos()
    try:
        ok = modelo.actualizar_clase(id_clase=id_clase, nombre=nombre, num_i=num_i_val)
        return jsonify({"success": True, "updated": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/clases/<int:id_clase>", methods=["DELETE"])
@jwt_required
def api_eliminar_clase(id_clase: int):
    modelo = Productos()
    try:
        ok = modelo.eliminar_clase(id_clase=id_clase)
        return jsonify({"success": True, "deleted": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/marcas", methods=["GET"])
@jwt_required
def api_listar_marcas():
    id_clase = request.args.get("clase_id", default=None, type=int)
    modelo = Productos()
    marcas = modelo.listar_marcas(id_clase=id_clase) or []
    return jsonify({"success": True, "marcas": marcas})


@productos_blueprint.route("/api/productos/marcas", methods=["POST"])
@jwt_required
def api_crear_marca():
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    id_clase = datos.get("id_clase")

    if nombre == "":
        return jsonify({"success": False, "error": "El nombre de la marca es obligatorio."}), 400
    try:
        id_clase_val = int(id_clase)
    except Exception:
        return jsonify({"success": False, "error": "La clase es obligatoria."}), 400

    modelo = Productos()
    try:
        new_id = modelo.crear_marca(id_clase=id_clase_val, nombre=nombre)
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/marcas/<int:id_marca>", methods=["PUT"])
@jwt_required
def api_actualizar_marca(id_marca: int):
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    id_clase = datos.get("id_clase")

    if nombre == "":
        return jsonify({"success": False, "error": "El nombre de la marca es obligatorio."}), 400
    try:
        id_clase_val = int(id_clase)
    except Exception:
        return jsonify({"success": False, "error": "La clase es obligatoria."}), 400

    modelo = Productos()
    try:
        ok = modelo.actualizar_marca(id_marca=id_marca, id_clase=id_clase_val, nombre=nombre)
        return jsonify({"success": True, "updated": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/marcas/<int:id_marca>", methods=["DELETE"])
@jwt_required
def api_eliminar_marca(id_marca: int):
    modelo = Productos()
    try:
        ok = modelo.eliminar_marca(id_marca=id_marca)
        return jsonify({"success": True, "deleted": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/modelos", methods=["GET"])
@jwt_required
def api_listar_modelos():
    id_marca = request.args.get("marca_id", default=None, type=int)
    q = request.args.get("q", default=None, type=str)
    modelo = Productos()
    modelos = modelo.listar_modelos(id_marca=id_marca, q=q) or []
    return jsonify({"success": True, "modelos": modelos})


@productos_blueprint.route("/api/productos/modelos", methods=["POST"])
@jwt_required
def api_crear_modelo():
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    id_marca = datos.get("id_marca")

    if nombre == "":
        return jsonify({"success": False, "error": "El nombre del modelo es obligatorio."}), 400
    try:
        id_marca_val = int(id_marca)
    except Exception:
        return jsonify({"success": False, "error": "La marca es obligatoria."}), 400

    modelo = Productos()
    try:
        new_id = modelo.crear_modelo(id_marca=id_marca_val, nombre=nombre)
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/modelos/<int:id_modelo>", methods=["PUT"])
@jwt_required
def api_actualizar_modelo(id_modelo: int):
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    id_marca = datos.get("id_marca")

    if nombre == "":
        return jsonify({"success": False, "error": "El nombre del modelo es obligatorio."}), 400
    try:
        id_marca_val = int(id_marca)
    except Exception:
        return jsonify({"success": False, "error": "La marca es obligatoria."}), 400

    modelo = Productos()
    try:
        ok = modelo.actualizar_modelo(id_modelo=id_modelo, id_marca=id_marca_val, nombre=nombre)
        return jsonify({"success": True, "updated": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/modelos/<int:id_modelo>", methods=["DELETE"])
@jwt_required
def api_eliminar_modelo(id_modelo: int):
    modelo = Productos()
    try:
        ok = modelo.eliminar_modelo(id_modelo=id_modelo)
        return jsonify({"success": True, "deleted": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400
