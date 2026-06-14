from flask import Blueprint, jsonify, render_template, request, g, redirect
from app.utils.decorators import jwt_required, tiene_permiso, solo_roles
from app.models.catalogo import CatalogoModel
from app.models.carrito import CarritoModel
from app.models.venta import VentaModel
from app.models.clientes import Clientes
import requests
import traceback

ventas_blueprint = Blueprint("ventas", __name__)


def obtener_cliente_id_actual() -> str:
    """Obtiene el ID del cliente actual desde g.user y verifica que exista en la BD de clientes"""
    if not g.user:
        return None
    
    # Obtener cédula desde el usuario
    if isinstance(g.user, dict):
        cliente_id = g.user.get("cedula") or g.user.get("cedula_personal")
    else:
        cliente_id = getattr(g.user, "cedula", None) or getattr(g.user, "cedula_personal", None)
    
    if not cliente_id:
        return None
    
    cliente_id_str = str(cliente_id)
    
    # Verificar que el cliente existe en la base de datos del negocio
    modelo_clientes = Clientes(ID_cliente=cliente_id_str)
    try:
        if modelo_clientes.verificar_cliente_existe(int(cliente_id_str)):
            return cliente_id_str
        return None
    except Exception as e:
        print(f"Error al verificar cliente: {e}")
        return None


def get_dolar_rates() -> dict:
    """Obtiene tasas oficial y paralelo del dólar"""
    oficial_url = "https://ve.dolarapi.com/v1/dolares/oficial"
    paralelo_url = "https://ve.dolarapi.com/v1/dolares/paralelo"
    
    try:
        oficial_resp = requests.get(oficial_url, timeout=5)
        paralelo_resp = requests.get(paralelo_url, timeout=5)
        
        oficial = oficial_resp.json().get("promedio", 520.91) if oficial_resp.status_code == 200 else 520.91
        paralelo = paralelo_resp.json().get("promedio", 710.12) if paralelo_resp.status_code == 200 else 710.12
        
        return {"oficial": oficial, "paralelo": paralelo}
    except:
        return {"oficial": 520.91, "paralelo": 710.12}


def calcular_precios_bs(productos: list, tasas: dict = None) -> list:
    """Calcula precios en bolívares"""
    if tasas is None:
        tasas = get_dolar_rates()
    
    for p in productos:
        precio_usd = float(p.get("precio_usd", 0))
        p["precio_bs_oficial"] = round(precio_usd * tasas["oficial"], 2)
        p["precio_bs_paralelo"] = round(precio_usd * tasas["paralelo"], 2)
    
    return productos


# ==================== VISTAS CLIENTE ====================

@ventas_blueprint.route("/catalogo")
def pagina_catalogo():
    """Página principal del catálogo de productos - acceso público"""
    return render_template(
        "ventas/catalogo.html",
        show_navbar=True,
        show_notifications=True,
        active_page="catalogo"
    )


@ventas_blueprint.route("/api/catalogo/productos")
def api_listar_productos_catalogo():
    """API para obtener productos del catálogo con filtros - acceso público"""
    try:
        clase_id = request.args.get("clase_id", type=str)
        marca_id = request.args.get("marca_id", type=str)
        q = request.args.get("q", "")
        
        modelo_catalogo = CatalogoModel(
            clase_id=clase_id,
            marca_id=marca_id,
            q=q if q else None
        )
        
        productos = modelo_catalogo.listar_productos_catalogo()
        
        tasas = get_dolar_rates()
        productos = calcular_precios_bs(productos, tasas)
        
        modelo_mas_vendidos = CatalogoModel()
        mas_vendidos = modelo_mas_vendidos.productos_mas_vendidos()
        mas_vendidos = calcular_precios_bs(mas_vendidos, tasas)
        
        modelo_clases = CatalogoModel()
        clases = modelo_clases.listar_clases()
        
        modelo_marcas = CatalogoModel()
        marcas = modelo_marcas.listar_marcas()
        
        return jsonify({
            "success": True,
            "productos": productos,
            "mas_vendidos": mas_vendidos,
            "clases": clases,
            "marcas": marcas,
            "tasas": tasas
        })
    except Exception as e:
        print(f"Error en api_listar_productos_catalogo: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== CARRITO ====================

@ventas_blueprint.route("/api/carrito", methods=["GET"])
@jwt_required
def api_obtener_carrito():
    """Obtener el carrito del cliente actual"""
    try:
        if not hasattr(g, 'user') or not g.user:
            return jsonify({"success": False, "error": "No autorizado"}), 401
        
        cliente_id = obtener_cliente_id_actual()
        if not cliente_id:
            return jsonify({"success": True, "items": [], "total_usd": 0, "total_bs": 0, "tasas": get_dolar_rates()})
        
        modelo_carrito = CarritoModel(cliente_id=cliente_id)
        carrito = modelo_carrito.obtener_carrito()
        
        tasas = get_dolar_rates()
        carrito = calcular_precios_bs(carrito, tasas)
        
        total_usd = sum(float(p.get("precio_usd", 0)) * int(p.get("cantidad", 0)) for p in carrito)
        total_bs_paralelo = sum(float(p.get("precio_bs_paralelo", 0)) for p in carrito)
        total_bs_oficial = sum(float(p.get("precio_bs_oficial", 0)) for p in carrito)
        
        return jsonify({
            "success": True,
            "items": carrito,
            "total_usd": round(total_usd, 2),
            "total_bs_paralelo": round(total_bs_paralelo, 2),
            "total_bs_oficial": round(total_bs_oficial, 2),
            "tasas": tasas
        })
    except Exception as e:
        print(f"Error en api_obtener_carrito: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@ventas_blueprint.route("/api/carrito", methods=["POST"])
@jwt_required
def api_agregar_carrito():
    """Agregar producto al carrito"""
    try:
        if not hasattr(g, 'user') or not g.user:
            return jsonify({"success": False, "error": "No autorizado"}), 401
        
        cliente_id = obtener_cliente_id_actual()
        if not cliente_id:
            return jsonify({"success": False, "error": "Debes ser un cliente registrado para agregar productos al carrito"}), 400
        
        datos = request.get_json(silent=True) or {}
        producto_id = datos.get("producto_id")
        cantidad = datos.get("cantidad", 1)
        
        if not producto_id:
            return jsonify({"success": False, "error": "Producto no especificado"}), 400
        
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
        
        modelo_carrito = CarritoModel(
            cliente_id=cliente_id,
            inventario_id=str(producto_id),
            cantidad=cantidad,
            usuario_id=usuario_id
        )
        modelo_carrito.agregar_al_carrito()
        
        return jsonify({"success": True, "message": "Producto agregado al carrito"})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        print(f"Error en api_agregar_carrito: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@ventas_blueprint.route("/api/carrito/<string:producto_id>", methods=["DELETE"])
@jwt_required
def api_eliminar_carrito(producto_id):
    """Eliminar producto del carrito"""
    try:
        if not hasattr(g, 'user') or not g.user:
            return jsonify({"success": False, "error": "No autorizado"}), 401
        
        cliente_id = obtener_cliente_id_actual()
        if not cliente_id:
            return jsonify({"success": True})
        
        modelo_carrito = CarritoModel(cliente_id=cliente_id, inventario_id=producto_id)
        modelo_carrito.eliminar_item()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error en api_eliminar_carrito: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ventas_blueprint.route("/api/carrito", methods=["PUT"])
@jwt_required
def api_actualizar_cantidad():
    """Actualizar cantidad de un producto en el carrito"""
    try:
        if not hasattr(g, 'user') or not g.user:
            return jsonify({"success": False, "error": "No autorizado"}), 401
        
        cliente_id = obtener_cliente_id_actual()
        if not cliente_id:
            return jsonify({"success": False, "error": "Cliente no identificado"}), 400
        
        datos = request.get_json(silent=True) or {}
        producto_id = datos.get("producto_id")
        cantidad = datos.get("cantidad", 1)
        
        modelo_carrito = CarritoModel(
            cliente_id=cliente_id,
            inventario_id=str(producto_id),
            cantidad=cantidad
        )
        modelo_carrito.actualizar_cantidad()
        return jsonify({"success": True})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        print(f"Error en api_actualizar_cantidad: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ventas_blueprint.route("/api/carrito/vaciar", methods=["DELETE"])
@jwt_required
def api_vaciar_carrito():
    """Vaciar todo el carrito"""
    try:
        if not hasattr(g, 'user') or not g.user:
            return jsonify({"success": False, "error": "No autorizado"}), 401
        
        cliente_id = obtener_cliente_id_actual()
        if not cliente_id:
            return jsonify({"success": True})
        
        modelo_carrito = CarritoModel(cliente_id=cliente_id)
        modelo_carrito.vaciar_carrito()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error en api_vaciar_carrito: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== PROCESO DE PAGO ====================

@ventas_blueprint.route("/pagar")
@jwt_required
def pagina_pagos():
    """Página de selección de método de pago"""
    if not hasattr(g, 'user') or not g.user:
        return redirect("/login")
    
    cliente_id = obtener_cliente_id_actual()
    if not cliente_id:
        return redirect("/catalogo")
    
    return render_template(
        "ventas/pagos.html",
        show_navbar=True,
        show_notifications=True,
        active_page="pagos"
    )


@ventas_blueprint.route("/api/metodos-pago")
@jwt_required
def api_metodos_pago():
    """Obtener métodos de pago disponibles"""
    metodos = [
        {"id": "pago_movil", "nombre": "Pago Móvil (Bs)", "moneda": "VES"},
        {"id": "zelle", "nombre": "Zelle (USD)", "moneda": "USD"},
        {"id": "binance", "nombre": "Binance (USDT)", "moneda": "USDT"},
        {"id": "efectivo_bs", "nombre": "Efectivo (Bs)", "moneda": "VES"},
        {"id": "efectivo_usd", "nombre": "Efectivo (USD)", "moneda": "USD"}
    ]
    return jsonify({"success": True, "metodos": metodos})


@ventas_blueprint.route("/api/procesar-pago", methods=["POST"])
@jwt_required
def api_procesar_pago():
    """Procesar el pago y crear la venta"""
    import os
    import uuid
    import traceback
    from werkzeug.utils import secure_filename
    from datetime import datetime
    
    try:
        if not hasattr(g, 'user') or not g.user:
            return jsonify({"success": False, "error": "No autorizado"}), 401
        
        cliente_id = obtener_cliente_id_actual()
        if not cliente_id:
            return jsonify({"success": False, "error": "Cliente no identificado"}), 400
        
        # Obtener datos del formulario
        metodo_pago = request.form.get("metodo_pago")
        fecha_pago = request.form.get("fecha_pago")
        referencia = request.form.get("referencia", "")
        monto = request.form.get("monto", None)
        capture_file = request.files.get("capture")
        
        if not metodo_pago:
            return jsonify({"success": False, "error": "Método de pago no seleccionado"}), 400
        
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
        
        # Obtener carrito
        modelo_carrito = CarritoModel(cliente_id=cliente_id)
        carrito = modelo_carrito.obtener_carrito()
        if not carrito:
            return jsonify({"success": False, "error": "Carrito vacío"}), 400
        
        # Guardar imagen de captura si existe
        capture_path = None
        if capture_file and metodo_pago not in ("efectivo_bs", "efectivo_usd"):
            try:
                nombre_seguro = secure_filename(capture_file.filename)
                _, extension = os.path.splitext(nombre_seguro)
                extension = extension.lower()
                nombre_final = f"capture_{uuid.uuid4().hex}{extension}"
                
                static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
                carpeta_destino = os.path.join(static_folder, "img", "capturas")
                os.makedirs(carpeta_destino, exist_ok=True)
                
                ruta_fisica = os.path.join(carpeta_destino, nombre_final)
                capture_file.save(ruta_fisica)
                capture_path = f"/static/img/capturas/{nombre_final}"
            except Exception as e:
                print(f"Error guardando archivo: {e}")
        
        estado_pago = "Pendiente" if metodo_pago not in ("efectivo_bs", "efectivo_usd") else "Pagado"
        
        # Crear la venta
        modelo_venta = VentaModel(
            cliente_id=cliente_id,
            items=carrito,
            metodo_pago=metodo_pago,
            estado_pago=estado_pago,
            usuario_id=usuario_id
        )
        factura_id = modelo_venta.crear_venta_desde_carrito()
        
        # Guardar registro de pago
        datos_pago = {
            "fecha_pago": fecha_pago or datetime.now().isoformat(),
            "referencia": referencia,
            "monto": monto,
            "capture": capture_path
        }
        
        modelo_pago = VentaModel(
            factura_id=factura_id,
            metodo_pago=metodo_pago,
            estado_pago=estado_pago,
            datos_pago=datos_pago,
            usuario_id=usuario_id
        )
        modelo_pago.guardar_registro_pago()
        
        # Vaciar el carrito
        modelo_carrito.vaciar_carrito()
        
        return jsonify({
            "success": True,
            "factura_id": factura_id,
            "mensaje": "Venta registrada. Tu pago está siendo verificado."
        })
        
    except Exception as e:
        print(f"ERROR EN PROCESAR PAGO: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@ventas_blueprint.route("/admin/validar-pagos")
@jwt_required
@solo_roles(['admin', 'ventas'])
def pagina_validar_pagos():
    """Panel de validación de pagos para empleados"""
    return render_template(
        "ventas/validacion.html",
        show_navbar=True,
        show_notifications=True,
        active_page="validar_pagos"
    )


# ==================== DASHBOARD ====================

@ventas_blueprint.route("/api/dashboard/ventas-hoy", methods=["GET"])
@jwt_required
def api_ventas_hoy():
    """API para obtener el total de ventas del día de hoy"""
    try:
        modelo_venta = VentaModel()
        ventas_hoy = modelo_venta.obtener_ventas_hoy()
        
        total_formateado = f"{ventas_hoy['total_ventas']:,.2f}"
        moneda = ventas_hoy['moneda']
        
        return jsonify({
            "success": True,
            "total_ventas": ventas_hoy['total_ventas'],
            "total_formateado": total_formateado,
            "cantidad_ventas": ventas_hoy['cantidad_ventas'],
            "moneda": moneda
        })
    except Exception as e:
        print(f"Error en api_ventas_hoy: {e}")
        return jsonify({"success": False, "error": str(e)}), 500