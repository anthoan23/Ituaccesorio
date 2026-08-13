from flask import Blueprint, jsonify, render_template, request, g
from datetime import datetime

from app.utils.decorators import jwt_required, tiene_permiso
from app.models.bitacora import Bitacora
from app.models.productos import ClaseProducto, MarcaProducto, Producto, Categoria
from app.models.inventario import Inventario
from app.utils.helpers import guardar_foto_inventario
from app.utils.validators import validar_nombre_producto, validar_solo_letras, validar_solo_letras_numeros


productos_blueprint = Blueprint("productos", __name__)


# ==================== PÁGINAS ====================

@productos_blueprint.route("/productos", methods=["GET"])
@jwt_required
@tiene_permiso('Productos', 'consultar')
def pagina_productos():
    return render_template(
        "productos.html",
        show_navbar=True,
        show_notifications=True,
        active_page="productos",
    )


# ==================== CATEGORÍAS ====================

@productos_blueprint.route("/api/productos/categorias", methods=["GET"])
@jwt_required
@tiene_permiso('Productos', 'consultar')
def api_listar_categorias():
    modelo = Categoria()
    categorias = modelo.listar_categorias()
    return jsonify({"success": True, "categorias": categorias})


# ==================== CLASES ====================

@productos_blueprint.route("/api/productos/clases", methods=["GET"])
@jwt_required
@tiene_permiso('Productos', 'consultar')
def api_listar_clases():
    modelo = ClaseProducto()
    clases = modelo.listar_clases()
    return jsonify({"success": True, "clases": clases})


@productos_blueprint.route("/api/productos/clases", methods=["POST"])
@jwt_required
@tiene_permiso('Productos', 'registrar')
def api_crear_clase():
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()

    error_validacion = validar_solo_letras(nombre, 2, 30, "Nombre de la clase")
    if error_validacion:
        return jsonify({"success": False, "error": error_validacion}), 400

    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
    
    modelo = ClaseProducto(nombre=nombre, usuario_id=usuario_id)
    
    try:
        new_id = modelo.registrar_clase()
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


# ==================== MARCAS ====================

@productos_blueprint.route("/api/productos/marcas", methods=["GET"])
@jwt_required
@tiene_permiso('Productos', 'consultar')
def api_listar_marcas():
    id_clase = request.args.get("clase_id", default=None, type=str)
    modelo = MarcaProducto()
    marcas = modelo.listar_marcas(id_clase=id_clase)
    return jsonify({"success": True, "marcas": marcas})


@productos_blueprint.route("/api/productos/marcas", methods=["POST"])
@jwt_required
@tiene_permiso('Productos', 'registrar')
def api_crear_marca():
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()

    error_validacion = validar_solo_letras_numeros(nombre, 2, 30, "Nombre de la marca")
    if error_validacion:
        return jsonify({"success": False, "error": error_validacion}), 400

    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")

    modelo = MarcaProducto(nombre=nombre, usuario_id=usuario_id)
    
    try:
        new_id = modelo.registrar_marca()
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


# ==================== PRODUCTOS (MODELOS) ====================

@productos_blueprint.route("/api/productos/modelos", methods=["GET"])
@jwt_required
@tiene_permiso('Productos', 'consultar')
def api_listar_modelos():
    id_marca = request.args.get("marca_id", default=None, type=str)
    id_clase = request.args.get("clase_id", default=None, type=str)
    q = request.args.get("q", default=None, type=str)
    
    modelo = Producto()
    productos = modelo.listar_productos(id_marca=id_marca, id_clase=id_clase, q=q)
    return jsonify({"success": True, "modelos": productos})


@productos_blueprint.route("/api/productos/modelos", methods=["POST"])
@jwt_required
@tiene_permiso('Productos', 'registrar')
def api_crear_modelo():
    if request.files:
        datos = request.form.to_dict()
        archivo = request.files.get("foto_inventario")
    else:
        datos = request.get_json(silent=True) or {}
        archivo = None
    
    nombre = str(datos.get("modelo", "")).strip()
    id_marca = str(datos.get("id_marca", "")).strip()
    id_clase = str(datos.get("id_clase", "")).strip()
    descripcion = datos.get("descripcion", "")

    error_nombre = validar_nombre_producto(nombre, 2, 50, "Nombre del producto")
    if error_nombre:
        return jsonify({"success": False, "error": error_nombre}), 400

    if not id_marca:
        return jsonify({"success": False, "error": "La marca es obligatoria."}), 400
    if not id_clase:
        return jsonify({"success": False, "error": "La clase es obligatoria."}), 400

    try:
        int(id_marca)
        int(id_clase)
    except ValueError:
        return jsonify({"success": False, "error": "Los identificadores de clase y marca deben ser numéricos."}), 400

    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")

    modelo = Producto(
        id_clase=id_clase,
        id_marca=id_marca,
        nombre=nombre,
        descripcion=descripcion,
        usuario_id=usuario_id
    )
    
    try:
        new_id = modelo.registrar_producto()
        
        if archivo and archivo.filename:
            try:
                guardar_foto_inventario(archivo)
            except ValueError as e:
                print(f"Error al guardar foto: {e}")
        
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as error:
        print(f"Error al crear producto: {error}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/modelos/<string:id_modelo>", methods=["PUT"])
@jwt_required
@tiene_permiso('Productos', 'modificar')
def api_actualizar_modelo(id_modelo: str):
    datos = request.get_json(silent=True) or {}
    
    nombre = str(datos.get("nombre", "")).strip()
    id_marca = str(datos.get("id_marca", "")).strip()
    id_clase = str(datos.get("id_clase", "")).strip()
    descripcion = datos.get("descripcion")

    error_nombre = validar_nombre_producto(nombre, 2, 50, "Nombre del producto")
    if error_nombre:
        return jsonify({"success": False, "error": error_nombre}), 400

    if not id_marca:
        return jsonify({"success": False, "error": "La marca es obligatoria."}), 400
    if not id_clase:
        return jsonify({"success": False, "error": "La clase es obligatoria."}), 400

    try:
        int(id_marca)
        int(id_clase)
    except ValueError:
        return jsonify({"success": False, "error": "Los identificadores de clase y marca deben ser numéricos."}), 400

    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")

    modelo = Producto(
        id_producto=id_modelo,
        id_clase=id_clase,
        id_marca=id_marca,
        nombre=nombre,
        descripcion=descripcion,
        usuario_id=usuario_id
    )
    
    try:
        ok = modelo.actualizar_producto()
        return jsonify({"success": True, "updated": ok})
    except Exception as error:
        print(f"Error al actualizar producto: {error}")
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/modelos/<string:id_modelo>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Productos', 'eliminar')
def api_eliminar_modelo(id_modelo: str):
    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
    
    modelo = Producto(id_producto=id_modelo, usuario_id=usuario_id)
    
    try:
        if modelo.verificar_stock_asociado():
            stock = modelo.obtener_stock_producto()
            return jsonify({
                "success": False, 
                "error": f"No se puede eliminar el producto porque tiene {stock} unidades en inventario."
            }), 400
        
        ok = modelo.eliminar_producto()
        return jsonify({"success": True, "deleted": ok})
    except Exception as error:
        print(f"Error al eliminar producto: {error}")
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/modelos/<string:id_modelo>/verificar-stock", methods=["GET"])
@jwt_required
@tiene_permiso('Productos', 'consultar')
def api_verificar_stock_producto(id_modelo: str):
    modelo = Producto(id_producto=id_modelo)
    tiene_stock = modelo.verificar_stock_asociado()
    stock = modelo.obtener_stock_producto()
    return jsonify({
        "success": True,
        "tiene_stock": tiene_stock,
        "stock": stock
    })


# ==================== REPORTES ====================

@productos_blueprint.route("/api/productos/reportes", methods=["POST"])
@jwt_required
@tiene_permiso('Productos', 'consultar')
def api_reportes_productos():
    from app.models.inventario import Inventario
    from datetime import datetime
    
    datos = request.get_json(silent=True) or {}
    
    filtros = {
        "clase_id": datos.get("clase_id"),
        "marca_id": datos.get("marca_id"),
        "q": datos.get("q", "").strip(),
        "stock_min": datos.get("stock_min"),
        "stock_max": datos.get("stock_max"),
    }
    
    modelo = Producto()
    productos = modelo.listar_productos(
        id_marca=filtros["marca_id"],
        id_clase=filtros["clase_id"],
        q=filtros["q"]
    )
    
    inv_modelo = Inventario()
    inventario_lista = inv_modelo.listar_inventario() or []
    
    stock_dict = {}
    for item in inventario_lista:
        id_prod = str(item.get("id_producto", ""))
        if id_prod:
            stock_dict[id_prod] = item.get("existencia", 0)
    
    productos_filtrados = []
    for p in productos:
        stock = stock_dict.get(str(p.get("id", "")), 0)
        
        if filtros["stock_min"] is not None and stock < int(filtros["stock_min"]):
            continue
        if filtros["stock_max"] is not None and stock > int(filtros["stock_max"]):
            continue
        
        p["stock"] = stock
        productos_filtrados.append(p)
    
    return jsonify({
        "success": True,
        "productos": productos_filtrados,
        "total": len(productos_filtrados),
        "fecha_reporte": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })