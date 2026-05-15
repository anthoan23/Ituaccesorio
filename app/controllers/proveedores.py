from flask import Blueprint, jsonify, render_template, request
from app.utils.decorators import jwt_required

from app.models.proveedores import Proveedores
from app.models.productos import Productos

proveedores_blueprint = Blueprint("proveedores", __name__)


@proveedores_blueprint.route("/proveedores", methods=["GET"])
@jwt_required
def pagina_proveedores():
    return render_template(
        "proveedores.html",
        show_navbar=True,
        show_notifications=True,
        active_page="proveedores",
    )


@proveedores_blueprint.route("/api/proveedores", methods=["GET"])
@jwt_required
def api_listar_proveedores():
    q = request.args.get("q", default=None, type=str)
    modelo = Proveedores()
    proveedores = modelo.listar_proveedores(q=q) or []
    return jsonify({"success": True, "proveedores": proveedores})


@proveedores_blueprint.route("/api/proveedores", methods=["POST"])
@jwt_required
def api_crear_proveedor():
    datos = request.get_json(silent=True) or {}
    id_proveedor = datos.get("id")
    nombre = str(datos.get("nombre", "")).strip()
    tipo = str(datos.get("tipo", "")).strip() or None
    celular = str(datos.get("celular", "")).strip() or None
    correo = str(datos.get("correo", "")).strip() or None
    direccion = str(datos.get("direccion", "")).strip() or None
    limite_credito = datos.get("limite_credito")
    productos = datos.get("productos")

    if nombre == "":
        return jsonify({"success": False, "error": "El nombre del proveedor es obligatorio."}), 400

    modelo = Proveedores()
    try:
        if id_proveedor in (None, ""):
            id_val = modelo.siguiente_id_proveedor()
        else:
            id_val = int(id_proveedor)
    except Exception:
        return jsonify({"success": False, "error": "El ID del proveedor debe ser numérico."}), 400

    try:
        if limite_credito in (None, ""):
            limite_val = None
        else:
            limite_val = int(limite_credito)
    except Exception:
        return jsonify({"success": False, "error": "El límite de crédito debe ser numérico."}), 400

    if productos not in (None, "") and not isinstance(productos, list):
        return jsonify({"success": False, "error": "Productos debe ser una lista."}), 400

    productos_norm: list[dict] = []
    for item in (productos or []):
        if not isinstance(item, dict):
            return jsonify({"success": False, "error": "Cada producto debe ser un objeto."}), 400
        if "id_modelo" not in item:
            return jsonify({"success": False, "error": "id_modelo es obligatorio en productos."}), 400
        try:
            id_modelo_val = int(item.get("id_modelo"))
        except Exception:
            return jsonify({"success": False, "error": "id_modelo debe ser numérico."}), 400
        costo = item.get("costo")
        try:
            if costo in (None, ""):
                costo_val = None
            else:
                costo_val = int(costo)
        except Exception:
            return jsonify({"success": False, "error": "El costo debe ser numérico."}), 400
        productos_norm.append({"id_modelo": id_modelo_val, "costo": costo_val})

    try:
        if productos_norm:
            new_id = modelo.crear_proveedor_con_productos(
                id_proveedor=id_val,
                nombre=nombre,
                tipo=tipo,
                celular=celular,
                correo=correo,
                direccion=direccion,
                limite_credito=limite_val,
                productos=productos_norm,
            )
        else:
            new_id = modelo.crear_proveedor(
                id_proveedor=id_val,
                nombre=nombre,
                tipo=tipo,
                celular=celular,
                correo=correo,
                direccion=direccion,
                limite_credito=limite_val,
            )
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@proveedores_blueprint.route("/api/proveedores/<int:id_proveedor>", methods=["GET"])
@jwt_required
def api_obtener_proveedor(id_proveedor: int):
    modelo = Proveedores()
    proveedor = modelo.obtener_proveedor(id_proveedor=id_proveedor)
    if not proveedor:
        return jsonify({"success": False, "error": "Proveedor no encontrado."}), 404

    productos = modelo.listar_productos_por_proveedor(id_proveedor=id_proveedor) or []
    return jsonify({"success": True, "proveedor": proveedor, "productos": productos})


@proveedores_blueprint.route("/api/proveedores/<int:id_proveedor>", methods=["PUT"])
@jwt_required
def api_actualizar_proveedor(id_proveedor: int):
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    tipo = str(datos.get("tipo", "")).strip() or None
    celular = str(datos.get("celular", "")).strip() or None
    correo = str(datos.get("correo", "")).strip() or None
    direccion = str(datos.get("direccion", "")).strip() or None
    limite_credito = datos.get("limite_credito")

    if nombre == "":
        return jsonify({"success": False, "error": "El nombre del proveedor es obligatorio."}), 400

    try:
        if limite_credito in (None, ""):
            limite_val = None
        else:
            limite_val = int(limite_credito)
    except Exception:
        return jsonify({"success": False, "error": "El límite de crédito debe ser numérico."}), 400

    modelo = Proveedores()
    try:
        ok = modelo.actualizar_proveedor(
            id_proveedor=id_proveedor,
            nombre=nombre,
            tipo=tipo,
            celular=celular,
            correo=correo,
            direccion=direccion,
            limite_credito=limite_val,
        )
        return jsonify({"success": True, "updated": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@proveedores_blueprint.route("/api/proveedores/<int:id_proveedor>", methods=["DELETE"])
@jwt_required
def api_eliminar_proveedor(id_proveedor: int):
    modelo = Proveedores()
    try:
        ok = modelo.eliminar_proveedor(id_proveedor=id_proveedor)
        return jsonify({"success": True, "deleted": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@proveedores_blueprint.route("/api/proveedores/<int:id_proveedor>/productos", methods=["GET"])
@jwt_required
def api_listar_productos_proveedor(id_proveedor: int):
    modelo = Proveedores()
    productos = modelo.listar_productos_por_proveedor(id_proveedor=id_proveedor) or []
    return jsonify({"success": True, "productos": productos})


@proveedores_blueprint.route("/api/proveedores/<int:id_proveedor>/productos", methods=["POST"])
@jwt_required
def api_upsert_producto_proveedor(id_proveedor: int):
    datos = request.get_json(silent=True) or {}
    id_modelo = datos.get("id_modelo")
    costo = datos.get("costo")

    try:
        id_modelo_val = int(id_modelo)
    except Exception:
        return jsonify({"success": False, "error": "El modelo es obligatorio."}), 400

    try:
        if costo in (None, ""):
            costo_val = None
        else:
            costo_val = int(costo)
    except Exception:
        return jsonify({"success": False, "error": "El costo debe ser numérico."}), 400

    modelo = Proveedores()
    try:
        ok = modelo.upsert_producto_proveedor(
            id_proveedor=id_proveedor,
            id_modelo=id_modelo_val,
            costo=costo_val,
        )
        return jsonify({"success": True, "updated": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@proveedores_blueprint.route(
    "/api/proveedores/<int:id_proveedor>/productos/<int:id_modelo>", methods=["DELETE"]
)
@jwt_required
def api_eliminar_producto_proveedor(id_proveedor: int, id_modelo: int):
    modelo = Proveedores()
    try:
        ok = modelo.eliminar_producto_proveedor(id_proveedor=id_proveedor, id_modelo=id_modelo)
        return jsonify({"success": True, "deleted": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@proveedores_blueprint.route("/api/proveedores/modelos", methods=["GET"])
@jwt_required
def api_listar_modelos_para_proveedores():
    q = request.args.get("q", default=None, type=str)
    modelo = Productos()
    modelos = modelo.listar_modelos(q=q) or []
    return jsonify({"success": True, "modelos": modelos})
