from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.proveedores import Proveedores
from app.models.productos import Producto
from app.models.bitacora import Bitacora

proveedores_blueprint = Blueprint("proveedores", __name__)


@proveedores_blueprint.route("/proveedores", methods=["GET"])
@jwt_required
@tiene_permiso('Proveedores', 'consultar')
def pagina_proveedores():
    return render_template(
        "proveedores.html",
        show_navbar=True,
        show_notifications=True,
        active_page="proveedores",
    )


@proveedores_blueprint.route("/api/proveedores", methods=["GET"])
@jwt_required
@tiene_permiso('Proveedores', 'consultar')
def api_listar_proveedores():
    q = request.args.get("q", default=None, type=str)
    modelo = Proveedores()
    proveedores = modelo.listar_proveedores(q=q) or []
    return jsonify({"success": True, "proveedores": proveedores})


@proveedores_blueprint.route("/api/proveedores", methods=["POST"])
@jwt_required
@tiene_permiso('Proveedores', 'registrar')
def api_crear_proveedor():
    datos = request.get_json(silent=True) or {}
    
    rif = str(datos.get("rif", "")).strip() or None
    nombre = str(datos.get("nombre", "")).strip()
    tipo = str(datos.get("tipo", "")).strip() or None
    celular = str(datos.get("celular", "")).strip() or None
    correo = str(datos.get("correo", "")).strip() or None
    direccion = str(datos.get("direccion", "")).strip() or None
    limite_credito = datos.get("limite_credito")
    productos = datos.get("productos")

    try:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")

        modelo = Proveedores(
            id_proveedor=0,
            rif=rif,
            nombre=nombre,
            tipo=tipo,
            celular=celular,
            correo=correo,
            direccion=direccion,
            limite_credito=limite_credito,
            usuario_id=usuario_id
        )

        if productos not in (None, ""):
            new_id = modelo.crear_proveedor_con_productos(productos=productos)
        else:
            new_id = modelo.crear_proveedor()

        return jsonify({"success": True, "id": new_id}), 201
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@proveedores_blueprint.route("/api/proveedores/<int:id_proveedor>", methods=["GET"])
@jwt_required
@tiene_permiso('Proveedores', 'consultar')
def api_obtener_proveedor(id_proveedor: int):
    """Obtiene un proveedor usando el stored procedure"""
    modelo = Proveedores(id_proveedor=id_proveedor)
    
    # Intentar usar el procedure primero
    resultado = modelo.obtener_proveedor_con_productos_procedure()
    
    if resultado.get("success", False) and resultado.get("proveedor"):
        return jsonify({
            "success": True, 
            "proveedor": resultado.get("proveedor"), 
            "productos": resultado.get("productos", [])
        })
    
    # Fallback: usar métodos tradicionales
    proveedor = modelo.obtener_proveedor()
    
    if not proveedor:
        return jsonify({"success": False, "error": "Proveedor no encontrado."}), 404

    productos = modelo.listar_productos_por_proveedor() or []
    return jsonify({"success": True, "proveedor": proveedor, "productos": productos})


@proveedores_blueprint.route("/api/proveedores/<int:id_proveedor>", methods=["PUT"])
@jwt_required
@tiene_permiso('Proveedores', 'modificar')
def api_actualizar_proveedor(id_proveedor: int):
    datos = request.get_json(silent=True) or {}
    
    rif = str(datos.get("rif", "")).strip() or None
    nombre = str(datos.get("nombre", "")).strip()
    tipo = str(datos.get("tipo", "")).strip() or None
    celular = str(datos.get("celular", "")).strip() or None
    correo = str(datos.get("correo", "")).strip() or None
    direccion = str(datos.get("direccion", "")).strip() or None
    limite_credito = datos.get("limite_credito")

    try:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")

        modelo = Proveedores(
            id_proveedor=id_proveedor,
            rif=rif,
            nombre=nombre,
            tipo=tipo,
            celular=celular,
            correo=correo,
            direccion=direccion,
            limite_credito=limite_credito,
            usuario_id=usuario_id
        )

        ok = modelo.actualizar_proveedor()

        return jsonify({"success": True, "updated": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@proveedores_blueprint.route("/api/proveedores/<int:id_proveedor>/verificar-eliminacion", methods=["GET"])
@jwt_required
@tiene_permiso('Proveedores', 'eliminar')
def api_verificar_eliminacion_proveedor(id_proveedor: int):
    """Verifica si un proveedor puede ser eliminado"""
    modelo = Proveedores(id_proveedor=id_proveedor)
    try:
        tiene_relaciones, mensaje = modelo.tiene_relaciones_activas()
        detalle = modelo.obtener_detalle_relaciones() if tiene_relaciones else {}
        
        return jsonify({
            "success": True,
            "puede_eliminar": not tiene_relaciones,
            "mensaje": mensaje if tiene_relaciones else None,
            "detalle": detalle if tiene_relaciones else None
        })
    except Exception as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 400


@proveedores_blueprint.route("/api/proveedores/<int:id_proveedor>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Proveedores', 'eliminar')
def api_eliminar_proveedor(id_proveedor: int):
    try:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        modelo = Proveedores(
            id_proveedor=id_proveedor,
            usuario_id=usuario_id
        )
        
        proveedor = modelo.obtener_proveedor()
        nombre_proveedor = proveedor.get("nombre", str(id_proveedor)) if proveedor else str(id_proveedor)
        
        modelo.nombre = nombre_proveedor
        
        tiene_relaciones, mensaje = modelo.tiene_relaciones_activas()
        
        if tiene_relaciones:
            detalle = modelo.obtener_detalle_relaciones()
            return jsonify({
                "success": False, 
                "error": mensaje,
                "detalle": detalle
            }), 400
        
        ok = modelo.eliminar_proveedor()
        
        return jsonify({"success": True, "deleted": bool(ok)})
    except Exception as error:
        error_msg = str(error)
        if "foreign key constraint fails" in error_msg.lower():
            return jsonify({
                "success": False, 
                "error": "No se puede eliminar el proveedor porque tiene registros relacionados en otras tablas (órdenes de compra, productos suministrados, etc.)"
            }), 400
        return jsonify({"success": False, "error": error_msg}), 400


@proveedores_blueprint.route("/api/proveedores/<int:id_proveedor>/productos", methods=["GET"])
@jwt_required
@tiene_permiso('Proveedores', 'consultar')
def api_listar_productos_proveedor(id_proveedor: int):
    modelo = Proveedores(id_proveedor=id_proveedor)
    productos = modelo.listar_productos_por_proveedor() or []
    return jsonify({"success": True, "productos": productos})


@proveedores_blueprint.route("/api/proveedores/<int:id_proveedor>/productos", methods=["POST"])
@jwt_required
@tiene_permiso('Proveedores', 'modificar')
def api_upsert_producto_proveedor(id_proveedor: int):
    datos = request.get_json(silent=True) or {}
    try:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")

        modelo = Proveedores(
            id_proveedor=id_proveedor,
            usuario_id=usuario_id
        )

        ok = modelo.upsert_producto_proveedor(id_modelo=datos.get("id_modelo"), costo=datos.get("costo"))

        return jsonify({"success": True, "updated": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@proveedores_blueprint.route(
    "/api/proveedores/<int:id_proveedor>/productos/<string:id_modelo>", methods=["DELETE"]
)
@jwt_required
@tiene_permiso('Proveedores', 'modificar')
def api_eliminar_producto_proveedor(id_proveedor: int, id_modelo: str):
    try:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        modelo = Proveedores(
            id_proveedor=id_proveedor,
            usuario_id=usuario_id
        )
        
        ok = modelo.eliminar_producto_proveedor(id_modelo=id_modelo)
        
        return jsonify({"success": True, "deleted": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@proveedores_blueprint.route("/api/proveedores/modelos", methods=["GET"])
@jwt_required
@tiene_permiso('Proveedores', 'consultar')
def api_listar_modelos_para_proveedores():
    q = request.args.get("q", default=None, type=str)
    modelo = Producto()
    modelos = modelo.listar_productos(q=q) or []
    return jsonify({"success": True, "modelos": modelos})


# ==================== REPORTES ====================

@proveedores_blueprint.route("/api/proveedores/reportes", methods=["POST"])
@jwt_required
@tiene_permiso('Proveedores', 'consultar')
def api_reportes_proveedores():
    from datetime import datetime
    
    datos = request.get_json(silent=True) or {}
    
    filtros = {
        "q": datos.get("q", "").strip(),
        "tipo": datos.get("tipo"),
        "limite_credito_min": datos.get("limite_credito_min"),
        "limite_credito_max": datos.get("limite_credito_max"),
    }
    
    modelo = Proveedores()
    proveedores = modelo.listar_proveedores(q=filtros["q"] if filtros["q"] else None) or []
    
    proveedores_filtrados = []
    for p in proveedores:
        if filtros["tipo"] and p.get("tipo") != filtros["tipo"]:
            continue
        
        limite = p.get("limite_credito") or 0
        if filtros["limite_credito_min"] is not None and limite < int(filtros["limite_credito_min"]):
            continue
        if filtros["limite_credito_max"] is not None and limite > int(filtros["limite_credito_max"]):
            continue
        
        proveedores_filtrados.append(p)
    
    for p in proveedores_filtrados:
        modelo_temp = Proveedores(id_proveedor=int(p["id"]))
        productos = modelo_temp.listar_productos_por_proveedor() or []
        p["total_productos"] = len(productos)
        p["costo_total"] = sum(item.get("costo", 0) or 0 for item in productos)
    
    return jsonify({
        "success": True,
        "proveedores": proveedores_filtrados,
        "total": len(proveedores_filtrados),
        "fecha_reporte": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


@proveedores_blueprint.route("/api/proveedores/tipos", methods=["GET"])
@jwt_required
@tiene_permiso('Proveedores', 'consultar')
def api_listar_tipos_proveedores():
    return jsonify({
        "success": True,
        "tipos": ["Nacional", "Internacional"]
    })