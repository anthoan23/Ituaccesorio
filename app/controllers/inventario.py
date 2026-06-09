import os
import uuid

from flask import Blueprint, jsonify, request, current_app, g
from werkzeug.utils import secure_filename

from decimal import Decimal, InvalidOperation

from app.models.inventario import Inventario, FotosInventario
from app.models.productos import Producto
from app.models.bitacora import registrar_en_bitacora
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


@inventario_blueprint.route("/api/inventario", methods=["GET"])
@jwt_required
@tiene_permiso('Inventario', 'consultar')
def api_listar_inventario():
    """Listado de inventario (stock + modelo + marca + clase)"""
    modelo = request.args.get("modelo")
    
    if modelo is not None:
        modelo = str(modelo).strip()
        if modelo == "":
            modelo = None

    inv = Inventario()
    
    if modelo:
        inventario = inv.listar_inventario_general_modelo(modelo) or []
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


@inventario_blueprint.route("/api/inventario/stock", methods=["POST"])
@jwt_required
@tiene_permiso('Inventario', 'registrar')
def api_registrar_stock():
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
    
    # Guardar foto
    foto_inventario = None
    if archivo:
        try:
            foto_inventario = _guardar_foto_inventario(archivo)
            print(f"Foto guardada en: {foto_inventario}")
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 400
    else:
        print("No se recibió archivo de foto")

    id_producto_val = str(id_producto).strip() if id_producto not in (None, "") else ""
    print(f"ID Producto: {id_producto_val}")
    
    if not id_producto_val:
        print("Error: id_producto vacío")
        return jsonify({"success": False, "error": "id_producto es obligatorio."}), 400

    if not foto_inventario:
        print("Error: foto_inventario vacía")
        return jsonify({"success": False, "error": "foto_inventario es obligatoria."}), 400

    try:
        existencia_val = int(existencia)
        print(f"Existencia: {existencia_val}")
    except Exception as e:
        print(f"Error parsing existencia: {e}")
        return jsonify({"success": False, "error": "existencia debe ser un número."}), 400

    try:
        costo_raw = str(costo_venta).strip().replace(",", ".")
        costo_val = Decimal(costo_raw)
        print(f"Costo venta: {costo_val}")
    except (InvalidOperation, Exception) as e:
        print(f"Error parsing costo: {e}")
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
            foto_inventario=foto_inventario,
        )
        
        print(f"ID inventario retornado: {id_inventario}")
        
        if not id_inventario:
            return jsonify({"success": False, "error": "No se pudo registrar el stock."}), 500
        
        # Obtener ID del usuario desde g.user
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        # Registrar en bitácora
        registrar_en_bitacora(
            accion="Registrar stock",
            descripcion=f"Se registró stock para producto ID: {id_producto_val} - Cantidad: {existencia_val} - Costo: {costo_val}",
            usuario_id=usuario_id,
            modulo_nombre="Inventario"
        )
        
        return jsonify({"success": True, "id_inventario": id_inventario})
    except Exception as error:
        print(f"Error en api_registrar_stock: {error}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(error)}), 500


@inventario_blueprint.route("/api/inventario/fotos/<string:id_inventario>", methods=["GET"])
@jwt_required
@tiene_permiso('Inventario', 'consultar')
def api_listar_fotos_inventario(id_inventario: str):
    """Lista todas las fotos de un inventario"""
    fotos = FotosInventario()
    lista = fotos.listar_fotos(id_inventario)
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
    
    fotos = FotosInventario()
    try:
        new_id = fotos.insertar_foto(id_inventario, foto_url)
        
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
    fotos = FotosInventario()
    try:
        ok = fotos.eliminar_foto(id_foto)
        if ok:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            
            registrar_en_bitacora(
                accion="Eliminar foto inventario",
                descripcion=f"Se eliminó la foto ID: {id_foto} del inventario",
                usuario_id=usuario_id,
                modulo_nombre="Inventario"
            )
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