import os
import uuid

from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename

from decimal import Decimal, InvalidOperation

from app.models.inventario import Inventario
from app.utils.decorators import jwt_required

inventario_blueprint = Blueprint("inventario", __name__)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def _es_imagen_permitida(nombre_archivo: str) -> bool:
    return "." in nombre_archivo and nombre_archivo.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def _guardar_foto_inventario(archivo):
    if not archivo or not getattr(archivo, "filename", ""):
        return None

    if not _es_imagen_permitida(archivo.filename):
        raise ValueError("La foto del inventario debe ser una imagen válida.")

    nombre_seguro = secure_filename(archivo.filename)
    _, extension = os.path.splitext(nombre_seguro)
    extension = extension.lower()[:10] or ".jpg"
    nombre_final = f"{uuid.uuid4().hex}{extension}"

    carpeta_destino = os.path.join(current_app.static_folder, "img", "evidencias", "inventario")
    os.makedirs(carpeta_destino, exist_ok=True)

    ruta_fisica = os.path.join(carpeta_destino, nombre_final)
    archivo.save(ruta_fisica)
    return f"/static/img/evidencias/inventario/{nombre_final}"


@inventario_blueprint.route("/api/inventario", methods=["GET"])
@jwt_required
def api_listar_inventario():
    """Listado de inventario (stock + modelo + marca + clase + caracteristica).

    Query params opcionales:
    - modelo: filtra por Producto.Nombre_producto (match exacto)
    """

    modelo = request.args.get("modelo")

    if modelo is not None:
        modelo = str(modelo).strip()
        if modelo == "":
            modelo = None

    inv = Inventario()
    inventario = inv.listar_inventario_filtrado(N_modelo=modelo) or []
    return jsonify({"success": True, "inventario": inventario})


@inventario_blueprint.route("/api/inventario/stock", methods=["POST"])
@jwt_required
def api_registrar_stock():
    datos = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})
    id_producto = datos.get("id_producto")
    existencia = datos.get("existencia")
    costo_venta = datos.get("costo_venta")
    capacidad = datos.get("capacidad")
    color = datos.get("color")
    foto_inventario = _guardar_foto_inventario(request.files.get("foto_inventario"))

    id_producto_val = str(id_producto).strip() if id_producto not in (None, "") else ""
    if not id_producto_val:
        return jsonify({"success": False, "error": "id_producto es obligatorio."}), 400

    if not foto_inventario:
        return jsonify({"success": False, "error": "foto_inventario es obligatoria."}), 400

    try:
        existencia_val = int(existencia)
    except Exception:
        return jsonify({"success": False, "error": "existencia debe ser un número."}), 400

    try:
        costo_raw = str(costo_venta).strip().replace(",", ".")
        costo_val = Decimal(costo_raw)
    except (InvalidOperation, Exception):
        return jsonify({"success": False, "error": "costo_venta debe ser un número (ej. 12.50)."}), 400

    if existencia_val < 0:
        return jsonify({"success": False, "error": "existencia no puede ser negativa."}), 400
    if costo_val < 0:
        return jsonify({"success": False, "error": "costo_venta no puede ser negativo."}), 400

    inv = Inventario()
    try:
        id_inventario = inv.registrar_stock(
            id_producto=id_producto_val,
            existencia=existencia_val,
            costo_venta=costo_val,
            capacidad=capacidad,
            color=color,
            foto_inventario=foto_inventario,
        )
        if not id_inventario:
            return jsonify({"success": False, "error": "No se pudo conectar a la base de datos."}), 500
        return jsonify({"success": True, "id_inventario": id_inventario})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400
