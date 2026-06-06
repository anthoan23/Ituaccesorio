from flask import Blueprint, jsonify, render_template, request
from app.utils.decorators import jwt_required

from app.models.productos import Productos

productos_blueprint = Blueprint("productos", __name__)
productos_modelo = Productos()


def _validate_len(nombre_campo: str, valor: str, max_len: int):
    valor = str(valor or "")
    if len(valor) > max_len:
        raise ValueError(f"{nombre_campo} no puede exceder {max_len} caracteres.")


def _parse_int_field(nombre_campo: str, valor, required: bool = True) -> int | None:
    if valor in (None, ""):
        if required:
            raise ValueError(f"{nombre_campo} es obligatorio.")
        return None
    try:
        num = int(valor)
    except Exception:
        raise ValueError(f"{nombre_campo} debe ser un número.")
    if required and num <= 0:
        raise ValueError(f"{nombre_campo} debe ser mayor a 0.")
    return num


def _parse_id_field(nombre_campo: str, valor, required: bool = True) -> str | None:
    if valor in (None, ""):
        if required:
            raise ValueError(f"{nombre_campo} es obligatorio.")
        return None
    texto = str(valor).strip()
    if not texto:
        if required:
            raise ValueError(f"{nombre_campo} es obligatorio.")
        return None
    if len(texto) > 10:
        raise ValueError(f"{nombre_campo} no puede exceder 10 caracteres.")
    return texto


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
        _validate_len("Clase", nombre, 30)
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400

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


@productos_blueprint.route("/api/productos/clases/<string:id_clase>", methods=["PUT"])
@jwt_required
def api_actualizar_clase(id_clase: str):
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    num_i = datos.get("num_i")
    if nombre == "":
        return jsonify({"success": False, "error": "El nombre de la clase es obligatorio."}), 400

    try:
        _validate_len("Clase", nombre, 30)
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400

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


@productos_blueprint.route("/api/productos/clases/<string:id_clase>", methods=["DELETE"])
@jwt_required
def api_eliminar_clase(id_clase: str):
    modelo = Productos()
    try:
        ok = modelo.eliminar_clase(id_clase=id_clase)
        return jsonify({"success": True, "deleted": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/marcas", methods=["GET"])
@jwt_required
def api_listar_marcas():
    id_clase = request.args.get("clase_id", default=None, type=str)
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
        _validate_len("Marca", nombre, 30)
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400

    try:
        id_clase_val = _parse_id_field("La clase", id_clase, required=False)
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400

    modelo = Productos()
    try:
        new_id = modelo.crear_marca(id_clase=id_clase_val, nombre=nombre)
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/marcas/<string:id_marca>", methods=["PUT"])
@jwt_required
def api_actualizar_marca(id_marca: str):
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    id_clase = datos.get("id_clase")

    if nombre == "":
        return jsonify({"success": False, "error": "El nombre de la marca es obligatorio."}), 400

    try:
        _validate_len("Marca", nombre, 30)
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400

    try:
        id_clase_val = _parse_id_field("La clase", id_clase, required=False)
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400

    modelo = Productos()
    try:
        ok = modelo.actualizar_marca(id_marca=id_marca, id_clase=id_clase_val, nombre=nombre)
        return jsonify({"success": True, "updated": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/marcas/<string:id_marca>", methods=["DELETE"])
@jwt_required
def api_eliminar_marca(id_marca: str):
    modelo = Productos()
    try:
        ok = modelo.eliminar_marca(id_marca=id_marca)
        return jsonify({"success": True, "deleted": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/modelos", methods=["GET"])
@jwt_required
def api_listar_modelos():
    id_marca = request.args.get("marca_id", default=None, type=str)
    id_clase = request.args.get("clase_id", default=None, type=str)
    q = request.args.get("q", default=None, type=str)
    modelo = Productos()
    modelos = modelo.listar_modelos(id_marca=id_marca, id_clase=id_clase, q=q) or []
    return jsonify({"success": True, "modelos": modelos})


@productos_blueprint.route("/api/productos/modelos", methods=["POST"])
@jwt_required
def api_crear_modelo():
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    id_marca = datos.get("id_marca")
    id_clase = datos.get("id_clase")
    descripcion = datos.get("descripcion")

    if nombre == "":
        return jsonify({"success": False, "error": "El nombre del producto es obligatorio."}), 400

    try:
        _validate_len("Producto", nombre, 30)
        id_marca_val = _parse_id_field("La marca", id_marca, required=True)
        id_clase_val = _parse_id_field("La clase", id_clase, required=True)
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400

    desc_val = None
    if descripcion not in (None, ""):
        desc_val = str(descripcion).strip()
        try:
            _validate_len("Descripción", desc_val, 300)
        except Exception as error:
            return jsonify({"success": False, "error": str(error)}), 400

    modelo = Productos()
    try:
        new_id = modelo.crear_modelo(id_clase=id_clase_val, id_marca=id_marca_val, nombre=nombre, descripcion=desc_val)
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/modelos/<string:id_modelo>", methods=["PUT"])
@jwt_required
def api_actualizar_modelo(id_modelo: str):
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    id_marca = datos.get("id_marca")
    id_clase = datos.get("id_clase")
    descripcion = datos.get("descripcion")

    if nombre == "":
        return jsonify({"success": False, "error": "El nombre del producto es obligatorio."}), 400

    try:
        _validate_len("Producto", nombre, 30)
        id_marca_val = _parse_id_field("La marca", id_marca, required=True)
        id_clase_val = _parse_id_field("La clase", id_clase, required=True)
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400

    desc_val = None
    if descripcion not in (None, ""):
        desc_val = str(descripcion).strip()
        try:
            _validate_len("Descripción", desc_val, 300)
        except Exception as error:
            return jsonify({"success": False, "error": str(error)}), 400

    modelo = Productos()
    try:
        ok = modelo.actualizar_modelo(
            id_modelo=id_modelo,
            id_clase=id_clase_val,
            id_marca=id_marca_val,
            nombre=nombre,
            descripcion=desc_val,
        )
        return jsonify({"success": True, "updated": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/modelos/<string:id_modelo>", methods=["DELETE"])
@jwt_required
def api_eliminar_modelo(id_modelo: str):
    modelo = Productos()
    try:
        ok = modelo.eliminar_modelo(id_modelo=id_modelo)
        return jsonify({"success": True, "deleted": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400
