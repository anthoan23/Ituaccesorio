from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required

from app.models.bitacora import registrar_en_bitacora
from app.models.productos import ClaseProducto, MarcaProducto, Producto

productos_blueprint = Blueprint("productos", __name__)


def _resolver_usuario_actual():
    usuario = getattr(g, "user", None)
    if not usuario:
        return {"id": "SYSTEM", "nombre": "SISTEMA", "foto": None}
    
    if isinstance(usuario, dict):
        user_id = usuario.get("usuario_id") or usuario.get("id") or "SYSTEM"
        user_name = usuario.get("usuario_nombre") or usuario.get("nombre") or usuario.get("username") or "USUARIO"
        user_foto = usuario.get("foto_perfil") or None
    else:
        user_id = getattr(usuario, "usuario_id", None) or getattr(usuario, "id", None) or "SYSTEM"
        user_name = getattr(usuario, "usuario_nombre", None) or getattr(usuario, "nombre", None) or getattr(usuario, "username", None) or "USUARIO"
        user_foto = getattr(usuario, "foto_perfil", None) or None
    
    return {"id": user_id, "nombre": user_name, "foto": user_foto}


def _resolver_usuario_id_str():
    info = _resolver_usuario_actual()
    if info["nombre"] and info["id"] != "SYSTEM":
        return f"{info['nombre']} ({info['id']})"
    return info["id"] if info["id"] else "SISTEMA"


# ==================== PÁGINAS ====================

@productos_blueprint.route("/productos", methods=["GET"])
@jwt_required
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
def api_listar_clases():
    modelo = ClaseProducto()
    clases = modelo.listar()  # Cambiado de listar_clases() a listar()
    return jsonify({"success": True, "clases": clases})


@productos_blueprint.route("/api/productos/clases", methods=["POST"])
@jwt_required
def api_crear_clase():
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    
    if not nombre:
        return jsonify({"success": False, "error": "El nombre de la clase es obligatorio."}), 400

    modelo = ClaseProducto(nombre=nombre)
    try:
        new_id = modelo.crear()
        
        user_info = _resolver_usuario_actual()
        registrar_en_bitacora(
            "Crear clase",
            f"Clase creada: {nombre} (ID: {new_id})",
            usuario_id=user_info["id"],
            modulo_nombre="Productos",
            usuario_nombre=user_info["nombre"],
            usuario_foto=user_info["foto"]
        )
        
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/clases/<string:id_clase>", methods=["PUT"])
@jwt_required
def api_actualizar_clase(id_clase: str):
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    
    if not nombre:
        return jsonify({"success": False, "error": "El nombre de la clase es obligatorio."}), 400

    modelo = ClaseProducto(id_clase=id_clase, nombre=nombre)
    try:
        ok = modelo.actualizar()
        
        if ok:
            user_info = _resolver_usuario_actual()
            registrar_en_bitacora(
                "Actualizar clase",
                f"Clase actualizada: {nombre} (ID: {id_clase})",
                usuario_id=user_info["id"],
                modulo_nombre="Productos",
                usuario_nombre=user_info["nombre"],
                usuario_foto=user_info["foto"]
            )
        
        return jsonify({"success": True, "updated": ok})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/clases/<string:id_clase>", methods=["DELETE"])
@jwt_required
def api_eliminar_clase(id_clase: str):
    modelo = ClaseProducto(id_clase=id_clase)
    try:
        ok = modelo.eliminar()
        
        if ok:
            user_info = _resolver_usuario_actual()
            registrar_en_bitacora(
                "Eliminar clase",
                f"Clase eliminada (ID: {id_clase})",
                usuario_id=user_info["id"],
                modulo_nombre="Productos",
                usuario_nombre=user_info["nombre"],
                usuario_foto=user_info["foto"]
            )
        
        return jsonify({"success": True, "deleted": ok})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


# ==================== MARCAS ====================

@productos_blueprint.route("/api/productos/marcas", methods=["GET"])
@jwt_required
def api_listar_marcas():
    id_clase = request.args.get("clase_id", default=None, type=str)
    modelo = MarcaProducto()
    marcas = modelo.listar(id_clase=id_clase)  # Cambiado de listar_marcas() a listar()
    return jsonify({"success": True, "marcas": marcas})


@productos_blueprint.route("/api/productos/marcas", methods=["POST"])
@jwt_required
def api_crear_marca():
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    
    if not nombre:
        return jsonify({"success": False, "error": "El nombre de la marca es obligatorio."}), 400

    modelo = MarcaProducto(nombre=nombre)
    try:
        new_id = modelo.crear()
        
        user_info = _resolver_usuario_actual()
        registrar_en_bitacora(
            "Crear marca",
            f"Marca creada: {nombre} (ID: {new_id})",
            usuario_id=user_info["id"],
            modulo_nombre="Productos",
            usuario_nombre=user_info["nombre"],
            usuario_foto=user_info["foto"]
        )
        
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/marcas/<string:id_marca>", methods=["PUT"])
@jwt_required
def api_actualizar_marca(id_marca: str):
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    
    if not nombre:
        return jsonify({"success": False, "error": "El nombre de la marca es obligatorio."}), 400

    modelo = MarcaProducto(id_marca=id_marca, nombre=nombre)
    try:
        ok = modelo.actualizar()
        
        if ok:
            user_info = _resolver_usuario_actual()
            registrar_en_bitacora(
                "Actualizar marca",
                f"Marca actualizada: {nombre} (ID: {id_marca})",
                usuario_id=user_info["id"],
                modulo_nombre="Productos",
                usuario_nombre=user_info["nombre"],
                usuario_foto=user_info["foto"]
            )
        
        return jsonify({"success": True, "updated": ok})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/marcas/<string:id_marca>", methods=["DELETE"])
@jwt_required
def api_eliminar_marca(id_marca: str):
    modelo = MarcaProducto(id_marca=id_marca)
    try:
        ok = modelo.eliminar()
        
        if ok:
            user_info = _resolver_usuario_actual()
            registrar_en_bitacora(
                "Eliminar marca",
                f"Marca eliminada (ID: {id_marca})",
                usuario_id=user_info["id"],
                modulo_nombre="Productos",
                usuario_nombre=user_info["nombre"],
                usuario_foto=user_info["foto"]
            )
        
        return jsonify({"success": True, "deleted": ok})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


# ==================== PRODUCTOS (MODELOS) ====================

@productos_blueprint.route("/api/productos/modelos", methods=["GET"])
@jwt_required
def api_listar_modelos():
    id_marca = request.args.get("marca_id", default=None, type=str)
    id_clase = request.args.get("clase_id", default=None, type=str)
    q = request.args.get("q", default=None, type=str)
    
    modelo = Producto()
    productos = modelo.listar(id_marca=id_marca, id_clase=id_clase, q=q)
    return jsonify({"success": True, "modelos": productos})


@productos_blueprint.route("/api/productos/modelos", methods=["POST"])
@jwt_required
def api_crear_modelo():
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    id_marca = datos.get("id_marca")
    id_clase = datos.get("id_clase")
    descripcion = datos.get("descripcion")

    if not nombre:
        return jsonify({"success": False, "error": "El nombre del producto es obligatorio."}), 400
    if not id_marca:
        return jsonify({"success": False, "error": "La marca es obligatoria."}), 400
    if not id_clase:
        return jsonify({"success": False, "error": "La clase es obligatoria."}), 400

    modelo = Producto(id_clase=str(id_clase), id_marca=str(id_marca), nombre=nombre, descripcion=descripcion)
    try:
        new_id = modelo.crear()
        
        user_info = _resolver_usuario_actual()
        registrar_en_bitacora(
            "Crear producto",
            f"Producto creado: {nombre} (ID: {new_id})",
            usuario_id=user_info["id"],
            modulo_nombre="Productos",
            usuario_nombre=user_info["nombre"],
            usuario_foto=user_info["foto"]
        )
        
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

    if not nombre:
        return jsonify({"success": False, "error": "El nombre del producto es obligatorio."}), 400
    if not id_marca:
        return jsonify({"success": False, "error": "La marca es obligatoria."}), 400
    if not id_clase:
        return jsonify({"success": False, "error": "La clase es obligatoria."}), 400

    modelo = Producto(id_producto=id_modelo, id_clase=str(id_clase), id_marca=str(id_marca), 
                     nombre=nombre, descripcion=descripcion)
    try:
        ok = modelo.actualizar()
        
        if ok:
            user_info = _resolver_usuario_actual()
            registrar_en_bitacora(
                "Actualizar producto",
                f"Producto actualizado: {nombre} (ID: {id_modelo})",
                usuario_id=user_info["id"],
                modulo_nombre="Productos",
                usuario_nombre=user_info["nombre"],
                usuario_foto=user_info["foto"]
            )
        
        return jsonify({"success": True, "updated": ok})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@productos_blueprint.route("/api/productos/modelos/<string:id_modelo>", methods=["DELETE"])
@jwt_required
def api_eliminar_modelo(id_modelo: str):
    modelo = Producto(id_producto=id_modelo)
    try:
        ok = modelo.eliminar()
        
        if ok:
            user_info = _resolver_usuario_actual()
            registrar_en_bitacora(
                "Eliminar producto",
                f"Producto eliminado (ID: {id_modelo})",
                usuario_id=user_info["id"],
                modulo_nombre="Productos",
                usuario_nombre=user_info["nombre"],
                usuario_foto=user_info["foto"]
            )
        
        return jsonify({"success": True, "deleted": ok})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400