import os
import uuid

from flask import Blueprint, jsonify, request, current_app, g
from werkzeug.utils import secure_filename

from decimal import Decimal, InvalidOperation

from app.models.inventario import Inventario, FotosInventario
from app.models.productos import Producto
from app.utils.decorators import jwt_required, tiene_permiso

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


# ==================== LISTADOS ====================

@inventario_blueprint.route("/api/inventario", methods=["GET"])
@jwt_required
@tiene_permiso('Inventario', 'consultar')
def api_listar_inventario():
    """Listado de inventario (stock + modelo + marca + clase)"""
    modelo_buscar = request.args.get("modelo")
    
    if modelo_buscar is not None:
        modelo_buscar = str(modelo_buscar).strip()
        if modelo_buscar == "":
            modelo_buscar = None

    inv = Inventario()
    
    if modelo_buscar:
        inventario = inv.listar_inventario_por_modelo(nombre_modelo=modelo_buscar) or []
    else:
        inventario = inv.listar_inventario_general() or []
    
    # Transformar keys para el frontend
    for item in inventario:
        item["tipo"] = item.get("nombre_clase", "")
        item["N_marca"] = item.get("nombre_marca", "")
        item["N_modelo"] = item.get("nombre_producto", "")
        item["Existencia"] = item.get("existencia", 0)
        item["Costo_venta"] = item.get("costo_venta", 0)
        item["Foto_inventario"] = item.get("foto_inventario", "")
    
    return jsonify({"success": True, "inventario": inventario})


@inventario_blueprint.route("/api/inventario/productos/bajo-stock", methods=["GET"])
@jwt_required
@tiene_permiso('Inventario', 'consultar')
def api_productos_bajo_stock():
    """Obtiene productos con stock bajo"""
    limite = request.args.get("limite", 10, type=int)
    inv = Inventario()
    productos = inv.listar_productos_bajo_stock(limite=limite)
    return jsonify({"success": True, "productos": productos})


@inventario_blueprint.route("/api/inventario/productos/sin-stock", methods=["GET"])
@jwt_required
@tiene_permiso('Inventario', 'consultar')
def api_productos_sin_stock():
    """Obtiene productos sin stock"""
    inv = Inventario()
    productos = inv.listar_productos_sin_stock()
    return jsonify({"success": True, "productos": productos})


# ==================== REGISTRO DE STOCK ====================

@inventario_blueprint.route("/api/inventario/stock", methods=["POST"])
@jwt_required
@tiene_permiso('Inventario', 'registrar')
def api_registrar_stock():
    """Registra o actualiza stock de un producto"""
    print("=== DEBUG: Iniciando registro de stock ===")
    
    # Verificar si es FormData o JSON
    if request.files:
        datos = request.form.to_dict()
        archivo = request.files.get("foto_inventario")
        print(f"Datos recibidos (FormData): {datos}")
        print(f"Archivo recibido: {archivo.filename if archivo else 'No'}")
    else:
        datos = request.get_json(silent=True) or {}
        archivo = None
        print(f"Datos recibidos (JSON): {datos}")
    
    id_producto = datos.get("id_producto")
    existencia = datos.get("existencia")
    costo_venta = datos.get("costo_venta")
    
    # Validar ID del producto
    if not id_producto:
        return jsonify({"success": False, "error": "id_producto es obligatorio."}), 400
    
    # Validar existencia
    try:
        existencia_val = int(existencia)
        if existencia_val < 0:
            return jsonify({"success": False, "error": "existencia no puede ser negativa."}), 400
    except Exception as e:
        return jsonify({"success": False, "error": "existencia debe ser un número."}), 400

    # Validar costo
    try:
        costo_raw = str(costo_venta).strip().replace(",", ".")
        costo_val = Decimal(costo_raw)
        if costo_val < 0:
            return jsonify({"success": False, "error": "costo_venta no puede ser negativo."}), 400
    except (InvalidOperation, Exception):
        return jsonify({"success": False, "error": "costo_venta debe ser un número (ej. 12.50)."}), 400

    # Guardar foto
    foto_path = None
    if archivo:
        try:
            foto_path = _guardar_foto_inventario(archivo)
            print(f"Foto guardada en: {foto_path}")
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 400

    # Instanciar modelo con los datos
    modelo = Inventario(
        id_producto=id_producto,
        existencia=existencia_val,
        costo_venta=costo_val
    )
    
    try:
        id_inventario = modelo.registrar_stock()
        print(f"ID inventario retornado: {id_inventario}")
        
        # Guardar foto si se proporcionó
        if foto_path and id_inventario:
            foto_model = FotosInventario(
                id_inventario=id_inventario,
                foto_inventario=foto_path
            )
            foto_model.registrar_foto()
        
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Registrar stock",
            descripcion=f"Se registró stock para producto ID: {id_producto} - Cantidad: {existencia_val} - Costo: {costo_val}",
            usuario_id=usuario_id,
            modulo_nombre="Inventario"
        )
        
        return jsonify({"success": True, "id_inventario": id_inventario})
    except Exception as error:
        print(f"Error en api_registrar_stock: {error}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(error)}), 500


# ==================== FOTOS DE INVENTARIO ====================

@inventario_blueprint.route("/api/inventario/fotos/<string:id_inventario>", methods=["GET"])
@jwt_required
@tiene_permiso('Inventario', 'consultar')
def api_listar_fotos_inventario(id_inventario: str):
    """Lista todas las fotos de un inventario"""
    modelo = FotosInventario(id_inventario=id_inventario)
    lista = modelo.listar_fotos()
    return jsonify({"success": True, "fotos": lista})


@inventario_blueprint.route("/api/inventario/fotos", methods=["POST"])
@jwt_required
@tiene_permiso('Inventario', 'registrar')
def api_agregar_foto_inventario():
    """Agrega una nueva foto a un inventario"""
    datos = request.get_json(silent=True) or {}
    id_inventario = datos.get("id_inventario")
    foto_url = datos.get("foto_url")
    
    if not id_inventario or not foto_url:
        return jsonify({"success": False, "error": "id_inventario y foto_url son requeridos."}), 400
    
    modelo = FotosInventario(
        id_inventario=id_inventario,
        foto_inventario=foto_url
    )
    
    try:
        new_id = modelo.registrar_foto()
        
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Agregar foto inventario",
            descripcion=f"Se agregó foto al inventario ID: {id_inventario}",
            usuario_id=usuario_id,
            modulo_nombre="Inventario"
        )
        
        return jsonify({"success": True, "id": new_id})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@inventario_blueprint.route("/api/inventario/fotos/<string:id_foto>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Inventario', 'eliminar')
def api_eliminar_foto_inventario(id_foto: str):
    """Elimina una foto de inventario"""
    modelo = FotosInventario(id_foto_inventario=id_foto)
    
    try:
        ok = modelo.eliminar_foto()
        if ok:
            return jsonify({"success": True, "message": "Foto eliminada."})
        return jsonify({"success": False, "error": "Foto no encontrada."}), 404
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


# ==================== REPORTES ====================

@inventario_blueprint.route("/api/inventario/reportes", methods=["POST"])
@jwt_required
@tiene_permiso('Inventario', 'consultar')
def api_reportes_inventario():
    """Obtiene inventario para reportes con filtros avanzados"""
    from datetime import datetime
    
    datos = request.get_json(silent=True) or {}
    
    filtros = {
        "tipo": datos.get("tipo"),
        "marca": datos.get("marca"),
        "stock_min": datos.get("stock_min"),
        "stock_max": datos.get("stock_max"),
        "q": datos.get("q", "").strip(),
    }
    
    inv = Inventario()
    inventario = inv.listar_inventario_general() or []
    
    # Aplicar filtros
    inventario_filtrado = []
    for item in inventario:
        # Filtrar por tipo (clase)
        if filtros["tipo"] and item.get("nombre_clase", "").lower() != filtros["tipo"].lower():
            continue
        
        # Filtrar por marca
        if filtros["marca"] and item.get("nombre_marca", "").lower() != filtros["marca"].lower():
            continue
        
        # Filtrar por búsqueda
        if filtros["q"]:
            q_lower = filtros["q"].lower()
            nombre = item.get("nombre_producto", "").lower()
            marca = item.get("nombre_marca", "").lower()
            clase = item.get("nombre_clase", "").lower()
            if q_lower not in nombre and q_lower not in marca and q_lower not in clase:
                continue
        
        # Filtrar por stock
        stock = item.get("existencia", 0)
        if filtros["stock_min"] is not None and stock < int(filtros["stock_min"]):
            continue
        if filtros["stock_max"] is not None and stock > int(filtros["stock_max"]):
            continue
        
        inventario_filtrado.append(item)
    
    # Obtener clases y marcas únicas para los filtros
    clases_unicas = sorted(set(item.get("nombre_clase", "") for item in inventario if item.get("nombre_clase")))
    marcas_unicas = sorted(set(item.get("nombre_marca", "") for item in inventario if item.get("nombre_marca")))
    
    return jsonify({
        "success": True,
        "inventario": inventario_filtrado,
        "total": len(inventario_filtrado),
        "clases": clases_unicas,
        "marcas": marcas_unicas,
        "fecha_reporte": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })