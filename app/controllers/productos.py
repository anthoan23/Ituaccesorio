from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso
from datetime import datetime

from app.models.bitacora import registrar_en_bitacora
from app.models.productos import ClaseProducto, MarcaProducto, Producto
from app.models.inventario import Inventario

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
    
    if not nombre:
        return jsonify({"success": False, "error": "El nombre de la clase es obligatorio."}), 400

    # Instanciar el modelo con los atributos
    modelo = ClaseProducto(nombre=nombre)
    
    try:
        new_id = modelo.registrar_clase()
        
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        usuario_nombre = g.user.get("usuario_nombre") if isinstance(g.user, dict) else getattr(g.user, "usuario_nombre", "SISTEMA")
        usuario_foto = g.user.get("foto_perfil") if isinstance(g.user, dict) else getattr(g.user, "foto_perfil", None)
        
        registrar_en_bitacora(
            "Crear clase",
            f"Clase creada: {nombre} (ID: {new_id})",
            usuario_id=usuario_id,
            modulo_nombre="Productos",
            usuario_nombre=usuario_nombre,
            usuario_foto=usuario_foto
        )
        
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/clases/<string:id_clase>", methods=["PUT"])
@jwt_required
@tiene_permiso('Productos', 'modificar')
def api_actualizar_clase(id_clase: str):
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    
    if not nombre:
        return jsonify({"success": False, "error": "El nombre de la clase es obligatorio."}), 400

    # Instanciar el modelo con los atributos
    modelo = ClaseProducto(id_clase=id_clase, nombre=nombre)
    
    try:
        ok = modelo.actualizar_clase()
        
        if ok:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            usuario_nombre = g.user.get("usuario_nombre") if isinstance(g.user, dict) else getattr(g.user, "usuario_nombre", "SISTEMA")
            usuario_foto = g.user.get("foto_perfil") if isinstance(g.user, dict) else getattr(g.user, "foto_perfil", None)
            
            registrar_en_bitacora(
                "Actualizar clase",
                f"Clase actualizada: {nombre} (ID: {id_clase})",
                usuario_id=usuario_id,
                modulo_nombre="Productos",
                usuario_nombre=usuario_nombre,
                usuario_foto=usuario_foto
            )
        
        return jsonify({"success": True, "updated": ok})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/clases/<string:id_clase>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Productos', 'eliminar')
def api_eliminar_clase(id_clase: str):
    # Instanciar el modelo con los atributos
    modelo = ClaseProducto(id_clase=id_clase)
    
    try:
        ok = modelo.eliminar_clase()
        
        if ok:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            usuario_nombre = g.user.get("usuario_nombre") if isinstance(g.user, dict) else getattr(g.user, "usuario_nombre", "SISTEMA")
            usuario_foto = g.user.get("foto_perfil") if isinstance(g.user, dict) else getattr(g.user, "foto_perfil", None)
            
            registrar_en_bitacora(
                "Eliminar clase",
                f"Clase eliminada (ID: {id_clase})",
                usuario_id=usuario_id,
                modulo_nombre="Productos",
                usuario_nombre=usuario_nombre,
                usuario_foto=usuario_foto
            )
        
        return jsonify({"success": True, "deleted": ok})
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
    
    if not nombre:
        return jsonify({"success": False, "error": "El nombre de la marca es obligatorio."}), 400

    # Instanciar el modelo con los atributos
    modelo = MarcaProducto(nombre=nombre)
    
    try:
        new_id = modelo.registrar_marca()
        
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        usuario_nombre = g.user.get("usuario_nombre") if isinstance(g.user, dict) else getattr(g.user, "usuario_nombre", "SISTEMA")
        usuario_foto = g.user.get("foto_perfil") if isinstance(g.user, dict) else getattr(g.user, "foto_perfil", None)
        
        registrar_en_bitacora(
            "Crear marca",
            f"Marca creada: {nombre} (ID: {new_id})",
            usuario_id=usuario_id,
            modulo_nombre="Productos",
            usuario_nombre=usuario_nombre,
            usuario_foto=usuario_foto
        )
        
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/marcas/<string:id_marca>", methods=["PUT"])
@jwt_required
@tiene_permiso('Productos', 'modificar')
def api_actualizar_marca(id_marca: str):
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    
    if not nombre:
        return jsonify({"success": False, "error": "El nombre de la marca es obligatorio."}), 400

    # Instanciar el modelo con los atributos
    modelo = MarcaProducto(id_marca=id_marca, nombre=nombre)
    
    try:
        ok = modelo.actualizar_marca()
        
        if ok:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            usuario_nombre = g.user.get("usuario_nombre") if isinstance(g.user, dict) else getattr(g.user, "usuario_nombre", "SISTEMA")
            usuario_foto = g.user.get("foto_perfil") if isinstance(g.user, dict) else getattr(g.user, "foto_perfil", None)
            
            registrar_en_bitacora(
                "Actualizar marca",
                f"Marca actualizada: {nombre} (ID: {id_marca})",
                usuario_id=usuario_id,
                modulo_nombre="Productos",
                usuario_nombre=usuario_nombre,
                usuario_foto=usuario_foto
            )
        
        return jsonify({"success": True, "updated": ok})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/marcas/<string:id_marca>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Productos', 'eliminar')
def api_eliminar_marca(id_marca: str):
    # Instanciar el modelo con los atributos
    modelo = MarcaProducto(id_marca=id_marca)
    
    try:
        ok = modelo.eliminar_marca()
        
        if ok:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            usuario_nombre = g.user.get("usuario_nombre") if isinstance(g.user, dict) else getattr(g.user, "usuario_nombre", "SISTEMA")
            usuario_foto = g.user.get("foto_perfil") if isinstance(g.user, dict) else getattr(g.user, "foto_perfil", None)
            
            registrar_en_bitacora(
                "Eliminar marca",
                f"Marca eliminada (ID: {id_marca})",
                usuario_id=usuario_id,
                modulo_nombre="Productos",
                usuario_nombre=usuario_nombre,
                usuario_foto=usuario_foto
            )
        
        return jsonify({"success": True, "deleted": ok})
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
    datos = request.get_json(silent=True) or {}
    
    nombre = str(datos.get("nombre", "")).strip()
    id_marca = str(datos.get("id_marca", "")).strip()
    id_clase = str(datos.get("id_clase", "")).strip()
    descripcion = datos.get("descripcion")

    if not nombre:
        return jsonify({"success": False, "error": "El nombre del producto es obligatorio."}), 400
    if not id_marca:
        return jsonify({"success": False, "error": "La marca es obligatoria."}), 400
    if not id_clase:
        return jsonify({"success": False, "error": "La clase es obligatoria."}), 400

    # Instanciar el modelo con los atributos
    modelo = Producto(
        id_clase=id_clase,
        id_marca=id_marca,
        nombre=nombre,
        descripcion=descripcion
    )
    
    try:
        new_id = modelo.registrar_producto()
        
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        usuario_nombre = g.user.get("usuario_nombre") if isinstance(g.user, dict) else getattr(g.user, "usuario_nombre", "SISTEMA")
        usuario_foto = g.user.get("foto_perfil") if isinstance(g.user, dict) else getattr(g.user, "foto_perfil", None)
        
        registrar_en_bitacora(
            "Crear producto",
            f"Producto creado: {nombre} (ID: {new_id})",
            usuario_id=usuario_id,
            modulo_nombre="Productos",
            usuario_nombre=usuario_nombre,
            usuario_foto=usuario_foto
        )
        
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as error:
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

    if not nombre:
        return jsonify({"success": False, "error": "El nombre del producto es obligatorio."}), 400
    if not id_marca:
        return jsonify({"success": False, "error": "La marca es obligatoria."}), 400
    if not id_clase:
        return jsonify({"success": False, "error": "La clase es obligatoria."}), 400

    # Instanciar el modelo con los atributos
    modelo = Producto(
        id_producto=id_modelo,
        id_clase=id_clase,
        id_marca=id_marca,
        nombre=nombre,
        descripcion=descripcion
    )
    
    try:
        ok = modelo.actualizar_producto()
        
        if ok:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            usuario_nombre = g.user.get("usuario_nombre") if isinstance(g.user, dict) else getattr(g.user, "usuario_nombre", "SISTEMA")
            usuario_foto = g.user.get("foto_perfil") if isinstance(g.user, dict) else getattr(g.user, "foto_perfil", None)
            
            registrar_en_bitacora(
                "Actualizar producto",
                f"Producto actualizado: {nombre} (ID: {id_modelo})",
                usuario_id=usuario_id,
                modulo_nombre="Productos",
                usuario_nombre=usuario_nombre,
                usuario_foto=usuario_foto
            )
        
        return jsonify({"success": True, "updated": ok})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/modelos/<string:id_modelo>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Productos', 'eliminar')
def api_eliminar_modelo(id_modelo: str):
    # Instanciar el modelo con los atributos
    modelo = Producto(id_producto=id_modelo)
    
    try:
        # Verificar si el producto tiene stock
        if modelo.verificar_stock_asociado():
            stock = modelo.obtener_stock_producto()
            return jsonify({
                "success": False, 
                "error": f"No se puede eliminar el producto porque tiene {stock} unidades en inventario. Primero debe eliminar o reducir el stock."
            }), 400
        
        ok = modelo.eliminar_producto()
        
        if ok:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            usuario_nombre = g.user.get("usuario_nombre") if isinstance(g.user, dict) else getattr(g.user, "usuario_nombre", "SISTEMA")
            usuario_foto = g.user.get("foto_perfil") if isinstance(g.user, dict) else getattr(g.user, "foto_perfil", None)
            
            registrar_en_bitacora(
                "Eliminar producto",
                f"Producto eliminado (ID: {id_modelo})",
                usuario_id=usuario_id,
                modulo_nombre="Productos",
                usuario_nombre=usuario_nombre,
                usuario_foto=usuario_foto
            )
        
        return jsonify({"success": True, "deleted": ok})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/modelos/<string:id_modelo>/verificar-stock", methods=["GET"])
@jwt_required
@tiene_permiso('Productos', 'consultar')
def api_verificar_stock_producto(id_modelo: str):
    """Verifica si un producto tiene stock asociado"""
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
    """Obtiene productos para reportes con filtros avanzados"""
    from app.models.inventario import Inventario
    
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
    
    # Obtener stock de cada producto
    inv_modelo = Inventario()
    inventario_lista = inv_modelo.listar_inventario() or []
    
    # Crear diccionario de stock por id_producto
    stock_dict = {}
    for item in inventario_lista:
        id_prod = str(item.get("id_producto", ""))
        if id_prod:
            stock_dict[id_prod] = item.get("existencia", 0)
    
    # Filtrar por stock y agregar stock a cada producto
    productos_filtrados = []
    for p in productos:
        stock = stock_dict.get(str(p.get("id", "")), 0)
        
        # Aplicar filtros de stock
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