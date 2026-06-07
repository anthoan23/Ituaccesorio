import os
import uuid

from flask import Blueprint, jsonify, request, current_app, g
from werkzeug.utils import secure_filename

from decimal import Decimal, InvalidOperation

from app.models.inventario import Inventario
from app.models.bitacora import registrar_en_bitacora
from app.utils.decorators import jwt_required, tiene_permiso

inventario_blueprint = Blueprint("inventario", __name__)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def _usuario_actual():
    """Obtiene el ID del usuario actual"""
    user = getattr(g, 'user', None)
    if not user:
        return "SYSTEM"
    if isinstance(user, dict):
        return str(user.get("usuario_id") or user.get("id") or "SYSTEM")
    return str(getattr(user, "usuario_id", None) or getattr(user, "id", None) or "SYSTEM")


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
@tiene_permiso('Inventario', 'consultar')
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
@tiene_permiso('Inventario', 'registrar')
def api_registrar_stock():
    datos = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})
    id_producto = datos.get("id_producto")
    existencia = datos.get("existencia")
    costo_venta = datos.get("costo_venta")
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
        # Obtener información del producto para la bitácora
        producto_info = inv.obtener_producto_por_id(id_producto_val)
        nombre_producto = producto_info.get("nombre_producto", id_producto_val) if producto_info else id_producto_val
        
        id_inventario = inv.registrar_stock(
            id_producto=id_producto_val,
            existencia=existencia_val,
            costo_venta=costo_val,
            foto_inventario=foto_inventario,
        )
        
        if not id_inventario:
            return jsonify({"success": False, "error": "No se pudo conectar a la base de datos."}), 500
        
        # Registrar en bitácora
        registrar_en_bitacora(
            accion="Registrar stock",
            descripcion=f"Se registró stock para producto: {nombre_producto} (ID: {id_producto_val}) - Cantidad: {existencia_val} - Costo: {costo_val}",
            usuario_id=_usuario_actual(),
            modulo_nombre="Inventario"
        )
        
        return jsonify({"success": True, "id_inventario": id_inventario})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@inventario_blueprint.route("/api/inventario/stock/<string:id_inventario>", methods=["PUT"])
@jwt_required
@tiene_permiso('Inventario', 'modificar')
def api_actualizar_stock(id_inventario: str):
    """Actualiza el stock de un producto en inventario"""
    datos = request.get_json(silent=True) or {}
    existencia = datos.get("existencia")
    costo_venta = datos.get("costo_venta")

    if existencia is None and costo_venta is None:
        return jsonify({"success": False, "error": "Debe proporcionar existencia o costo_venta para actualizar."}), 400

    inv = Inventario()
    try:
        # Obtener información actual antes de actualizar
        stock_actual = inv.obtener_stock_por_id(id_inventario)
        if not stock_actual:
            return jsonify({"success": False, "error": "Stock no encontrado."}), 404
        
        nombre_producto = stock_actual.get("nombre_producto", id_inventario)
        existencia_actual = stock_actual.get("existencia", 0)
        costo_actual = stock_actual.get("costo_venta", 0)
        
        if existencia is not None:
            existencia_val = int(existencia)
            if existencia_val < 0:
                return jsonify({"success": False, "error": "existencia no puede ser negativa."}), 400
        else:
            existencia_val = None
        
        if costo_venta is not None:
            costo_raw = str(costo_venta).strip().replace(",", ".")
            costo_val = Decimal(costo_raw)
            if costo_val < 0:
                return jsonify({"success": False, "error": "costo_venta no puede ser negativo."}), 400
        else:
            costo_val = None
        
        ok = inv.actualizar_stock(
            id_inventario=id_inventario,
            existencia=existencia_val,
            costo_venta=costo_val,
        )
        
        if not ok:
            return jsonify({"success": False, "error": "No se pudo actualizar el stock."}), 500
        
        # Registrar en bitácora
        cambios = []
        if existencia_val is not None and existencia_val != existencia_actual:
            cambios.append(f"cantidad: {existencia_actual} → {existencia_val}")
        if costo_val is not None and costo_val != costo_actual:
            cambios.append(f"costo: {costo_actual} → {costo_val}")
        
        if cambios:
            registrar_en_bitacora(
                accion="Actualizar stock",
                descripcion=f"Se actualizó stock para producto: {nombre_producto} (ID Inventario: {id_inventario}) - Cambios: {', '.join(cambios)}",
                usuario_id=_usuario_actual(),
                modulo_nombre="Inventario"
            )
        
        return jsonify({"success": True, "message": "Stock actualizado correctamente."})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@inventario_blueprint.route("/api/inventario/stock/<string:id_inventario>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Inventario', 'eliminar')
def api_eliminar_stock(id_inventario: str):
    """Elimina un registro de stock del inventario"""
    inv = Inventario()
    try:
        # Obtener información antes de eliminar
        stock_actual = inv.obtener_stock_por_id(id_inventario)
        if not stock_actual:
            return jsonify({"success": False, "error": "Stock no encontrado."}), 404
        
        nombre_producto = stock_actual.get("nombre_producto", id_inventario)
        existencia = stock_actual.get("existencia", 0)
        costo = stock_actual.get("costo_venta", 0)
        
        ok = inv.eliminar_stock(id_inventario=id_inventario)
        
        if not ok:
            return jsonify({"success": False, "error": "No se pudo eliminar el stock."}), 500
        
        # Registrar en bitácora
        registrar_en_bitacora(
            accion="Eliminar stock",
            descripcion=f"Se eliminó stock del producto: {nombre_producto} (ID Inventario: {id_inventario}) - Cantidad: {existencia} - Costo: {costo}",
            usuario_id=_usuario_actual(),
            modulo_nombre="Inventario"
        )
        
        return jsonify({"success": True, "message": "Stock eliminado correctamente."})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@inventario_blueprint.route("/api/inventario/productos", methods=["GET"])
@jwt_required
@tiene_permiso('Inventario', 'consultar')
def api_listar_productos_para_inventario():
    """Lista productos disponibles para agregar a inventario"""
    inv = Inventario()
    productos = inv.listar_productos_sin_inventario() or []
    return jsonify({"success": True, "productos": productos})


@inventario_blueprint.route("/api/inventario/stock/<string:id_inventario>", methods=["GET"])
@jwt_required
@tiene_permiso('Inventario', 'consultar')
def api_obtener_stock(id_inventario: str):
    """Obtiene un registro de stock específico"""
    inv = Inventario()
    stock = inv.obtener_stock_por_id(id_inventario)
    if not stock:
        return jsonify({"success": False, "error": "Stock no encontrado."}), 404
    return jsonify({"success": True, "stock": stock})