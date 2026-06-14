from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.bitacora import registrar_en_bitacora
from app.models.proveedores import Proveedores
from app.models.productos import Producto

proveedores_blueprint = Blueprint("proveedores", __name__)
proveedores_modelo = Proveedores()
productos_modelo = Producto()


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
    id_proveedor = datos.get("id")
    nombre = str(datos.get("nombre", "")).strip()
    tipo = str(datos.get("tipo", "")).strip() or None
    celular = str(datos.get("celular", "")).strip() or None
    correo = str(datos.get("correo", "")).strip() or None
    direccion = str(datos.get("direccion", "")).strip() or None
    limite_credito = datos.get("limite_credito")
    productos = datos.get("productos")

    if nombre == "":
        return jsonify({"success": False, "error": "El nombre del proveedor es obligatorio."}), 400

    modelo = Proveedores()
    
    # Validar ID del proveedor (0 significa que el modelo generará el ID automáticamente)
    if id_proveedor in (None, ""):
        id_val = 0  # El modelo asignará automáticamente el siguiente ID
    else:
        try:
            id_val = int(str(id_proveedor).strip())
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "El ID del proveedor debe ser un número válido."}), 400

    # Validar límite de crédito
    try:
        if limite_credito in (None, ""):
            limite_val = None
        else:
            limite_val = int(limite_credito)
    except Exception:
        return jsonify({"success": False, "error": "El límite de crédito debe ser numérico."}), 400

    if productos not in (None, "") and not isinstance(productos, list):
        return jsonify({"success": False, "error": "Productos debe ser una lista."}), 400

    productos_norm: list[dict] = []
    for item in (productos or []):
        if not isinstance(item, dict):
            return jsonify({"success": False, "error": "Cada producto debe ser un objeto."}), 400
        if "id_modelo" not in item:
            return jsonify({"success": False, "error": "id_modelo es obligatorio en productos."}), 400
        id_modelo_val = str(item.get("id_modelo") or "").strip()
        if not id_modelo_val:
            return jsonify({"success": False, "error": "id_modelo es obligatorio en productos."}), 400
        costo = item.get("costo")
        try:
            if costo in (None, ""):
                costo_val = None
            else:
                costo_val = int(costo)
        except Exception:
            return jsonify({"success": False, "error": "El costo debe ser numérico."}), 400
        productos_norm.append({"id_modelo": id_modelo_val, "costo": costo_val})

    try:
        # Asignar valores a la instancia del modelo
        modelo.id_proveedor = id_val
        modelo.nombre = nombre
        modelo.tipo = tipo
        modelo.celular = celular
        modelo.correo = correo
        modelo.direccion = direccion
        modelo.limite_credito = limite_val

        if productos_norm:
            new_id = modelo.crear_proveedor_con_productos(productos=productos_norm)
        else:
            new_id = modelo.crear_proveedor()
        
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Crear proveedor",
            descripcion=f"Se creó el proveedor: {nombre} - Tipo: {tipo or 'N/A'} - Límite crédito: {limite_val or 0}",
            usuario_id=usuario_id,
            modulo_nombre="Proveedores"
        )
        
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@proveedores_blueprint.route("/api/proveedores/<int:id_proveedor>", methods=["GET"])
@jwt_required
@tiene_permiso('Proveedores', 'consultar')
def api_obtener_proveedor(id_proveedor: int):
    modelo = Proveedores()
    proveedor = modelo.obtener_proveedor(id_proveedor=id_proveedor)
    if not proveedor:
        return jsonify({"success": False, "error": "Proveedor no encontrado."}), 404

    productos = modelo.listar_productos_por_proveedor(id_proveedor=id_proveedor) or []
    return jsonify({"success": True, "proveedor": proveedor, "productos": productos})


@proveedores_blueprint.route("/api/proveedores/<int:id_proveedor>", methods=["PUT"])
@jwt_required
@tiene_permiso('Proveedores', 'modificar')
def api_actualizar_proveedor(id_proveedor: int):
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    tipo = str(datos.get("tipo", "")).strip() or None
    celular = str(datos.get("celular", "")).strip() or None
    correo = str(datos.get("correo", "")).strip() or None
    direccion = str(datos.get("direccion", "")).strip() or None
    limite_credito = datos.get("limite_credito")

    if nombre == "":
        return jsonify({"success": False, "error": "El nombre del proveedor es obligatorio."}), 400

    try:
        if limite_credito in (None, ""):
            limite_val = None
        else:
            limite_val = int(limite_credito)
    except Exception:
        return jsonify({"success": False, "error": "El límite de crédito debe ser numérico."}), 400

    modelo = Proveedores()
    try:
        # Asignar valores a la instancia del modelo
        modelo.id_proveedor = id_proveedor
        modelo.nombre = nombre
        modelo.tipo = tipo
        modelo.celular = celular
        modelo.correo = correo
        modelo.direccion = direccion
        modelo.limite_credito = limite_val
        
        ok = modelo.actualizar_proveedor()
        
        if ok:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            
            registrar_en_bitacora(
                accion="Actualizar proveedor",
                descripcion=f"Se actualizó el proveedor ID: {id_proveedor} - Nuevo nombre: {nombre}",
                usuario_id=usuario_id,
                modulo_nombre="Proveedores"
            )
        
        return jsonify({"success": True, "updated": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@proveedores_blueprint.route("/api/proveedores/<int:id_proveedor>/verificar-eliminacion", methods=["GET"])
@jwt_required
@tiene_permiso('Proveedores', 'eliminar')
def api_verificar_eliminacion_proveedor(id_proveedor: int):
    """Verifica si un proveedor puede ser eliminado"""
    modelo = Proveedores()
    try:
        tiene_relaciones, mensaje = modelo.tiene_relaciones_activas(id_proveedor=id_proveedor)
        detalle = modelo.obtener_detalle_relaciones(id_proveedor=id_proveedor) if tiene_relaciones else {}
        
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
    modelo = Proveedores()
    try:
        # Primero verificar si tiene relaciones activas
        tiene_relaciones, mensaje = modelo.tiene_relaciones_activas(id_proveedor=id_proveedor)
        
        if tiene_relaciones:
            detalle = modelo.obtener_detalle_relaciones(id_proveedor=id_proveedor)
            return jsonify({
                "success": False, 
                "error": mensaje,
                "detalle": detalle
            }), 400
        
        # Obtener nombre antes de eliminar
        proveedor = modelo.obtener_proveedor(id_proveedor=id_proveedor)
        nombre_proveedor = proveedor.get("nombre", str(id_proveedor)) if proveedor else str(id_proveedor)
        
        ok = modelo.eliminar_proveedor(id_proveedor=id_proveedor)
        
        if ok:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            
            registrar_en_bitacora(
                accion="Eliminar proveedor",
                descripcion=f"Se eliminó el proveedor ID: {id_proveedor} - Nombre: {nombre_proveedor}",
                usuario_id=usuario_id,
                modulo_nombre="Proveedores"
            )
        
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
    modelo = Proveedores()
    productos = modelo.listar_productos_por_proveedor(id_proveedor=id_proveedor) or []
    return jsonify({"success": True, "productos": productos})


@proveedores_blueprint.route("/api/proveedores/<int:id_proveedor>/productos", methods=["POST"])
@jwt_required
@tiene_permiso('Proveedores', 'modificar')
def api_upsert_producto_proveedor(id_proveedor: int):
    datos = request.get_json(silent=True) or {}
    id_modelo = datos.get("id_modelo")
    costo = datos.get("costo")

    id_modelo_val = str(id_modelo or "").strip()
    if not id_modelo_val:
        return jsonify({"success": False, "error": "El modelo es obligatorio."}), 400

    try:
        if costo in (None, ""):
            costo_val = None
        else:
            costo_val = int(costo)
    except Exception:
        return jsonify({"success": False, "error": "El costo debe ser numérico."}), 400

    modelo = Proveedores()
    try:
        ok = modelo.upsert_producto_proveedor(
            id_proveedor=id_proveedor,
            id_modelo=id_modelo_val,
            costo=costo_val,
        )
        
        if ok:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            
            proveedor = modelo.obtener_proveedor(id_proveedor=id_proveedor)
            nombre_proveedor = proveedor.get("nombre", str(id_proveedor)) if proveedor else str(id_proveedor)
            
            registrar_en_bitacora(
                accion="Actualizar producto de proveedor",
                descripcion=f"Se actualizó producto para proveedor: {nombre_proveedor} (ID: {id_proveedor}) - Modelo ID: {id_modelo_val} - Costo: {costo_val}",
                usuario_id=usuario_id,
                modulo_nombre="Proveedores"
            )
        
        return jsonify({"success": True, "updated": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@proveedores_blueprint.route(
    "/api/proveedores/<int:id_proveedor>/productos/<string:id_modelo>", methods=["DELETE"]
)
@jwt_required
@tiene_permiso('Proveedores', 'modificar')
def api_eliminar_producto_proveedor(id_proveedor: int, id_modelo: str):
    modelo = Proveedores()
    try:
        ok = modelo.eliminar_producto_proveedor(id_proveedor=id_proveedor, id_modelo=id_modelo)
        
        if ok:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            
            proveedor = modelo.obtener_proveedor(id_proveedor=id_proveedor)
            nombre_proveedor = proveedor.get("nombre", str(id_proveedor)) if proveedor else str(id_proveedor)
            
            registrar_en_bitacora(
                accion="Eliminar producto de proveedor",
                descripcion=f"Se eliminó producto del proveedor: {nombre_proveedor} (ID: {id_proveedor}) - Modelo ID: {id_modelo}",
                usuario_id=usuario_id,
                modulo_nombre="Proveedores"
            )
        
        return jsonify({"success": True, "deleted": bool(ok)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@proveedores_blueprint.route("/api/proveedores/modelos", methods=["GET"])
@jwt_required
@tiene_permiso('Proveedores', 'consultar')
def api_listar_modelos_para_proveedores():
    q = request.args.get("q", default=None, type=str)
    modelo = Producto()
    modelos = modelo.listar(q=q) or []
    return jsonify({"success": True, "modelos": modelos})


# ==================== REPORTES ====================

@proveedores_blueprint.route("/api/proveedores/reportes", methods=["POST"])
@jwt_required
@tiene_permiso('Proveedores', 'consultar')
def api_reportes_proveedores():
    """Obtiene proveedores para reportes con filtros avanzados"""
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
        productos = modelo.listar_productos_por_proveedor(id_proveedor=int(p["id"])) or []
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
    """Lista los tipos de proveedores disponibles para filtros"""
    return jsonify({
        "success": True,
        "tipos": ["Nacional", "Internacional"]
    })