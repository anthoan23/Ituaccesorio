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


# ==================== FOTOS DE INVENTARIO ====================

@inventario_blueprint.route("/api/inventario/fotos/<string:id_inventario>", methods=["GET"])
@jwt_required
@tiene_permiso('Inventario', 'consultar')
def api_listar_fotos_inventario(id_inventario: str):
    modelo = FotosInventario(id_inventario=id_inventario)
    lista = modelo.listar_fotos()
    return jsonify({"success": True, "fotos": lista})


# ==================== REPORTES ====================

@inventario_blueprint.route("/api/inventario/reportes", methods=["POST"])
@jwt_required
@tiene_permiso('Inventario', 'consultar')
def api_reportes_inventario():
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
    
    inventario_filtrado = []
    for item in inventario:
        if filtros["tipo"] and item.get("nombre_clase", "").lower() != filtros["tipo"].lower():
            continue
        
        if filtros["marca"] and item.get("nombre_marca", "").lower() != filtros["marca"].lower():
            continue
        
        if filtros["q"]:
            q_lower = filtros["q"].lower()
            nombre = item.get("nombre_producto", "").lower()
            marca = item.get("nombre_marca", "").lower()
            clase = item.get("nombre_clase", "").lower()
            if q_lower not in nombre and q_lower not in marca and q_lower not in clase:
                continue
        
        stock = item.get("existencia", 0)
        if filtros["stock_min"] is not None and stock < int(filtros["stock_min"]):
            continue
        if filtros["stock_max"] is not None and stock > int(filtros["stock_max"]):
            continue
        
        inventario_filtrado.append(item)
    
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