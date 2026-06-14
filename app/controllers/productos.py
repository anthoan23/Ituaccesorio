from flask import Blueprint, jsonify, render_template, request, g, current_app
from app.utils.decorators import jwt_required, tiene_permiso
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename

from app.models.bitacora import registrar_en_bitacora
from app.models.productos import ClaseProducto, MarcaProducto, Producto, Categoria
from app.models.inventario import Inventario, FotosInventario

productos_blueprint = Blueprint("productos", __name__)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def _es_imagen_permitida(nombre_archivo: str) -> bool:
    return "." in nombre_archivo and nombre_archivo.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def _guardar_foto_inventario(archivo):
    if not archivo or not getattr(archivo, "filename", ""):
        return None

    if not _es_imagen_permitida(archivo.filename):
        raise ValueError("La foto debe ser una imagen válida.")

    nombre_seguro = secure_filename(archivo.filename)
    _, extension = os.path.splitext(nombre_seguro)
    extension = extension.lower()[:10] or ".jpg"
    nombre_final = f"{uuid.uuid4().hex}{extension}"

    carpeta_destino = os.path.join(current_app.static_folder, "img", "evidencias", "inventario")
    os.makedirs(carpeta_destino, exist_ok=True)

    ruta_fisica = os.path.join(carpeta_destino, nombre_final)
    archivo.save(ruta_fisica)
    return f"/static/img/evidencias/inventario/{nombre_final}"


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
    
    if not nombre:
        return jsonify({"success": False, "error": "El nombre de la clase es obligatorio."}), 400

    modelo = ClaseProducto(nombre=nombre)
    
    modelo = ClaseProducto(nombre=nombre, usuario_id=usuario_id)
    try:
        new_id = modelo.crear()
        
        # Obtener usuario desde g.user
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

    modelo = MarcaProducto(nombre=nombre)
    
    try:
        new_id = modelo.crear()
        
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
    # Verificar si es FormData (con foto) o JSON
    if request.files:
        datos = request.form.to_dict()
        archivo = request.files.get("foto_inventario")
        print("=== DATOS RECIBIDOS (FormData) ===")
        print(datos)
        print(f"Archivo: {archivo.filename if archivo else 'No'}")
    else:
        datos = request.get_json(silent=True) or {}
        archivo = None
        print("=== DATOS RECIBIDOS (JSON) ===")
        print(datos)
    
    # Extraer campos
    nombre = str(datos.get("modelo", "")).strip()
    id_marca = str(datos.get("id_marca", "")).strip()
    id_clase = str(datos.get("id_clase", "")).strip()
    id_categoria = datos.get("id_categoria", 0)
    descripcion = datos.get("descripcion", "")

    print(f"Nombre extraído: '{nombre}'")
    print(f"ID Marca: '{id_marca}'")
    print(f"ID Clase: '{id_clase}'")

    if not nombre:
        return jsonify({"success": False, "error": "El nombre del producto es obligatorio."}), 400
    if not id_marca:
        return jsonify({"success": False, "error": "La marca es obligatoria."}), 400
    if not id_clase:
        return jsonify({"success": False, "error": "La clase es obligatoria."}), 400

    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
    
    # Instanciar el modelo con los atributos
    modelo = Producto(
        
        id_clase=id_clase,
        
        id_marca=id_marca,
        
        nombre=nombre, 
       
        descripcion=descripcion,
        usuario_id=usuario_id
    
    )
    
    try:
        new_id = modelo.crear()
        
        # Guardar foto si se proporcionó (solo guardar, no asociar a inventario aún)
        foto_path = None
        if archivo and archivo.filename:
            try:
                foto_path = _guardar_foto_inventario(archivo)
                print(f"Foto guardada: {foto_path}")
                # TODO: Guardar la foto asociada al producto (si agregas una tabla Producto_fotos)
            except ValueError as e:
                print(f"Error al guardar foto: {e}")
        
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

    if not nombre:
        return jsonify({"success": False, "error": "El nombre del producto es obligatorio."}), 400
    if not id_marca:
        return jsonify({"success": False, "error": "La marca es obligatoria."}), 400
    if not id_clase:
        return jsonify({"success": False, "error": "La clase es obligatoria."}), 400

    modelo = Producto(
        id_producto=id_modelo,
        id_clase=id_clase,
        id_marca=id_marca,
        nombre=nombre,
        descripcion=descripcion
    )
    
    modelo = Producto(
        id_producto=id_modelo, 
        id_clase=str(id_clase), 
        id_marca=str(id_marca), 
        nombre=nombre, 
        descripcion=descripcion,
        usuario_id=usuario_id
    )
    try:
        ok = modelo.actualizar()
        
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
    modelo = Producto(id_producto=id_modelo)
    
    modelo = Producto(id_producto=id_modelo, usuario_id=usuario_id)
    try:
        if modelo.verificar_stock_asociado():
            stock = modelo.obtener_stock_producto()
            return jsonify({
                "success": False, 
                "error": f"No se puede eliminar el producto porque tiene {stock} unidades en inventario. Primero debe eliminar o reducir el stock."
            }), 400
        
        ok = modelo.eliminar()
        
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