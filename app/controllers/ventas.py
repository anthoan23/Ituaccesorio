from flask import Blueprint, jsonify, render_template, request, g, redirect
from app.utils.decorators import jwt_required
from app.models.ventas import VentasModel
from app.models.clientes import GestionClientes
from app.models.productos import Productos
import requests
import os

ventas_blueprint = Blueprint("ventas", __name__)


def obtener_cliente_id_actual() -> int | None:
    usuario = getattr(g, "user", {}) or {}
    cliente_id = usuario.get("cedula") or usuario.get("cedula_personal") or usuario.get("id_c") or usuario.get("id_cliente")
    if cliente_id is None:
        return None

    try:
        cliente_id_int = int(cliente_id)
    except (TypeError, ValueError):
        return None

    modelo_clientes = GestionClientes()
    existente = modelo_clientes.obtener_cliente_por_id(cliente_id_int)
    if existente:
        return cliente_id_int

    return None

# --- Helper para obtener tasas de cambio ---
def get_dolar_rates():
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

def calcular_precios_bs(productos):
    """Calcula precios en bolívares usando tasa paralelo y oficial"""
    tasas = get_dolar_rates()
    for p in productos:
        # Precio en bolívares según tasa oficial (para referencia)
        p["precio_bs_oficial"] = round(p["precio_usd"] * tasas["oficial"], 2)
        # Precio en bolívares según tasa paralelo (para pago en efectivo Bs)
        p["precio_bs_paralelo"] = round(p["precio_usd"] * tasas["paralelo"], 2)
    return productos

# ==================== VISTAS CLIENTE ====================

@ventas_blueprint.route("/catalogo")
def pagina_catalogo():
    """Página principal del catálogo de productos"""
    return render_template(
        "ventas/catalogo.html",
        show_navbar=True,
        show_notifications=True,
        active_page="catalogo"
    )

@ventas_blueprint.route("/api/catalogo/productos")
@jwt_required
def api_listar_productos_catalogo():
    """API para obtener productos del catálogo con filtros"""
    modelo_ventas = VentasModel()
    modelo_productos = Productos()
    
    # Obtener filtros
    clase_id = request.args.get("clase_id", type=int)
    marca_id = request.args.get("marca_id", type=int)
    q = request.args.get("q", "")
    
    # Obtener productos con sus precios en USD desde stock
    productos = modelo_ventas.listar_productos_catalogo(
        clase_id=clase_id,
        marca_id=marca_id,
        q=q
    )
    
    # Calcular precios en bolívares
    productos = calcular_precios_bs(productos)
    
    # Obtener productos más vendidos para destacar
    mas_vendidos = modelo_ventas.productos_mas_vendidos(limite=5)
    mas_vendidos = calcular_precios_bs(mas_vendidos)
    
    # Obtener clases y marcas para filtros
    clases = modelo_productos.listar_clases() or []
    marcas = modelo_productos.listar_marcas() or []
    
    return jsonify({
        "success": True,
        "productos": productos,
        "mas_vendidos": mas_vendidos,
        "clases": clases,
        "marcas": marcas,
        "tasas": get_dolar_rates()
    })

@ventas_blueprint.route("/api/carrito", methods=["GET"])
@jwt_required
def api_obtener_carrito():
    """Obtener el carrito del cliente actual"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    cliente_id = obtener_cliente_id_actual()
    if not cliente_id:
        return jsonify({"success": False, "error": "Cliente no identificado"}), 400
    
    modelo = VentasModel()
    carrito = modelo.obtener_carrito(cliente_id)
    carrito = calcular_precios_bs(carrito)
    
    total_usd = sum(p["precio_usd"] * p["cantidad"] for p in carrito)
    total_bs_paralelo = sum(p["precio_bs_paralelo"] * p["cantidad"] for p in carrito)
    total_bs_oficial = sum(p["precio_bs_oficial"] * p["cantidad"] for p in carrito)
    
    return jsonify({
        "success": True,
        "items": carrito,
        "total_usd": round(total_usd, 2),
        "total_bs_paralelo": round(total_bs_paralelo, 2),
        "total_bs_oficial": round(total_bs_oficial, 2),
        "cantidad_items": len(carrito)
    })

@ventas_blueprint.route("/api/carrito", methods=["POST"])
@jwt_required
def api_agregar_carrito():
    """Agregar producto al carrito"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    cliente_id = obtener_cliente_id_actual()
    if not cliente_id:
        return jsonify({"success": False, "error": "Cliente no identificado"}), 400
    
    datos = request.get_json(silent=True) or {}
    producto_id = datos.get("producto_id")
    cantidad = datos.get("cantidad", 1)
    
    if not producto_id:
        return jsonify({"success": False, "error": "Producto no especificado"}), 400
    
    modelo = VentasModel()
    try:
        modelo.agregar_carrito(cliente_id, producto_id, cantidad)
        return jsonify({"success": True, "message": "Producto agregado al carrito"})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400

@ventas_blueprint.route("/api/carrito/<int:producto_id>", methods=["DELETE"])
@jwt_required
def api_eliminar_carrito(producto_id):
    """Eliminar producto del carrito"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    cliente_id = obtener_cliente_id_actual()
    if not cliente_id:
        return jsonify({"success": False, "error": "Cliente no identificado"}), 400
    
    modelo = VentasModel()
    modelo.eliminar_carrito_item(cliente_id, producto_id)
    return jsonify({"success": True})

@ventas_blueprint.route("/api/carrito", methods=["PUT"])
@jwt_required
def api_actualizar_cantidad():
    """Actualizar cantidad de un producto en el carrito"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    cliente_id = obtener_cliente_id_actual()
    if not cliente_id:
        return jsonify({"success": False, "error": "Cliente no identificado"}), 400
    
    datos = request.get_json(silent=True) or {}
    producto_id = datos.get("producto_id")
    cantidad = datos.get("cantidad", 1)
    
    modelo = VentasModel()
    modelo.actualizar_carrito_cantidad(cliente_id, producto_id, cantidad)
    return jsonify({"success": True})

@ventas_blueprint.route("/api/carrito/vaciar", methods=["DELETE"])
@jwt_required
def api_vaciar_carrito():
    """Vaciar todo el carrito"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    cliente_id = obtener_cliente_id_actual()
    if not cliente_id:
        return jsonify({"success": False, "error": "Cliente no identificado"}), 400
    
    modelo = VentasModel()
    modelo.vaciar_carrito(cliente_id)
    return jsonify({"success": True})

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
    
    modelo = VentasModel()
    carrito = modelo.obtener_carrito(cliente_id)
    
    if not carrito:
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
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    cliente_id = obtener_cliente_id_actual()
    if not cliente_id:
        return jsonify({"success": False, "error": "Cliente no identificado"}), 400
    
    datos = request.get_json(silent=True) or {}
    metodo_pago = datos.get("metodo_pago")
    datos_pago = datos.get("datos_pago", {})
    
    if not metodo_pago:
        return jsonify({"success": False, "error": "Método de pago no seleccionado"}), 400
    
    modelo = VentasModel()
    
    # Obtener carrito
    carrito = modelo.obtener_carrito(cliente_id)
    if not carrito:
        return jsonify({"success": False, "error": "Carrito vacío"}), 400
    
    # Calcular totales
    tasas = get_dolar_rates()
    total_usd = sum(p["precio_usd"] * p["cantidad"] for p in carrito)
    total_bs = total_usd * tasas["paralelo"]
    
    # Crear factura
    factura_id = modelo.crear_venta(
        cliente_id=cliente_id,
        items=carrito,
        total_usd=total_usd,
        total_bs=total_bs,
        metodo_pago=metodo_pago,
        estado_pago="Por Verificar" if metodo_pago != "efectivo_bs" and metodo_pago != "efectivo_usd" else "Pendiente"
    )
    
    # Guardar reporte de pago según método
    if metodo_pago != "efectivo_bs" and metodo_pago != "efectivo_usd":
        modelo.guardar_reporte_pago(
            factura_id=factura_id,
            metodo_pago=metodo_pago,
            datos=datos_pago
        )
    
    # Vaciar carrito
    modelo.vaciar_carrito(cliente_id)
    
    return jsonify({
        "success": True,
        "factura_id": factura_id,
        "mensaje": "Venta registrada. Tu pago está siendo verificado."
    })

# ==================== VALIDACIÓN DE PAGOS (EMPLEADOS) ====================

@ventas_blueprint.route("/admin/validar-pagos")
@jwt_required
def pagina_validar_pagos():
    """Panel de validación de pagos para empleados"""
    return render_template(
        "ventas/validacion.html",
        show_navbar=True,
        show_notifications=True,
        active_page="validar_pagos"
    )

@ventas_blueprint.route("/api/admin/pagos-pendientes")
@jwt_required
def api_pagos_pendientes():
    """Obtener pagos pendientes de verificación"""
    modelo = VentasModel()
    pagos = modelo.obtener_pagos_pendientes()
    return jsonify({"success": True, "pagos": pagos})

@ventas_blueprint.route("/api/admin/pagos-aprobados")
@jwt_required
def api_pagos_aprobados():
    """Obtener pagos aprobados"""
    modelo = VentasModel()
    pagos = modelo.obtener_pagos_aprobados()
    return jsonify({"success": True, "pagos": pagos})

@ventas_blueprint.route("/api/admin/pagos-rechazados")
@jwt_required
def api_pagos_rechazados():
    """Obtener pagos rechazados"""
    modelo = VentasModel()
    pagos = modelo.obtener_pagos_rechazados()
    return jsonify({"success": True, "pagos": pagos})

@ventas_blueprint.route("/api/admin/aprobar-pago/<factura_id>", methods=["POST"])
@jwt_required
def api_aprobar_pago(factura_id):
    """Aprobar un pago"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    empleado_id = g.user.get("id_em") or g.user.get("id_empleado")
    
    modelo = VentasModel()
    modelo.aprobar_pago(factura_id, empleado_id)
    
    return jsonify({"success": True, "mensaje": "Pago aprobado correctamente"})

@ventas_blueprint.route("/api/admin/rechazar-pago/<factura_id>", methods=["POST"])
@jwt_required
def api_rechazar_pago(factura_id):
    """Rechazar un pago con motivo"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    datos = request.get_json(silent=True) or {}
    motivo = datos.get("motivo", "")
    
    if not motivo:
        return jsonify({"success": False, "error": "Debe especificar un motivo"}), 400
    
    empleado_id = g.user.get("id_em") or g.user.get("id_empleado")
    
    modelo = VentasModel()
    modelo.rechazar_pago(factura_id, empleado_id, motivo)
    
    return jsonify({"success": True, "mensaje": "Pago rechazado"})

@ventas_blueprint.route("/api/admin/ventas-local", methods=["POST"])
@jwt_required
def api_registrar_venta_local():
    """Registrar venta realizada en el local (efectivo)"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    empleado_id = g.user.get("id_em") or g.user.get("id_empleado")
    datos = request.get_json(silent=True) or {}
    
    cliente_id = datos.get("cliente_id")
    items = datos.get("items", [])
    total_pagado = datos.get("total_pagado")
    metodo_pago = datos.get("metodo_pago", "efectivo_usd")
    
    if not items:
        return jsonify({"success": False, "error": "Debe seleccionar al menos un producto"}), 400
    
    modelo = VentasModel()
    tasas = get_dolar_rates()
    
    # Calcular totales
    total_usd = 0
    for item in items:
        producto = modelo.obtener_producto(item["producto_id"])
        if producto:
            total_usd += producto["precio_usd"] * item["cantidad"]
    
    total_bs = total_usd * tasas["paralelo"]
    
    # Crear venta
    factura_id = modelo.crear_venta_local(
        cliente_id=cliente_id,
        empleado_id=empleado_id,
        items=items,
        total_usd=total_usd,
        total_bs=total_bs,
        metodo_pago=metodo_pago,
        total_pagado=total_pagado
    )
    
    return jsonify({
        "success": True,
        "factura_id": factura_id,
        "mensaje": "Venta registrada exitosamente"
    })

# ==================== ENTREGAS ====================

@ventas_blueprint.route("/api/admin/registrar-entrega", methods=["POST"])
@jwt_required
def api_registrar_entrega():
    """Registrar entrega de producto"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    datos = request.get_json(silent=True) or {}
    factura_id = datos.get("factura_id")
    empleado_delivery_id = datos.get("empleado_delivery_id")
    direccion = datos.get("direccion")
    
    modelo = VentasModel()
    modelo.registrar_entrega(factura_id, empleado_delivery_id, direccion)
    
    return jsonify({"success": True, "mensaje": "Entrega registrada"})# app/controllers/ventas.py
from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required
from app.models.ventas import VentasModel
from app.models.productos import Productos
import requests
import os

ventas_blueprint = Blueprint("ventas", __name__)

# --- Helper para obtener tasas de cambio ---
def get_dolar_rates():
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

def calcular_precios_bs(productos):
    """Calcula precios en bolívares usando tasa paralelo y oficial"""
    tasas = get_dolar_rates()
    for p in productos:
        # Precio en bolívares según tasa oficial (para referencia)
        p["precio_bs_oficial"] = round(p["precio_usd"] * tasas["oficial"], 2)
        # Precio en bolívares según tasa paralelo (para pago en efectivo Bs)
        p["precio_bs_paralelo"] = round(p["precio_usd"] * tasas["paralelo"], 2)
    return productos

# ==================== VISTAS CLIENTE ====================

@ventas_blueprint.route("/catalogo")
def pagina_catalogo():
    """Página principal del catálogo de productos"""
    return render_template(
        "ventas/catalogo.html",
        show_navbar=True,
        show_notifications=True,
        active_page="catalogo"
    )

@ventas_blueprint.route("/api/catalogo/productos")
@jwt_required
def api_listar_productos_catalogo():
    """API para obtener productos del catálogo con filtros"""
    modelo_ventas = VentasModel()
    modelo_productos = Productos()
    
    # Obtener filtros
    clase_id = request.args.get("clase_id", type=int)
    marca_id = request.args.get("marca_id", type=int)
    q = request.args.get("q", "")
    
    # Obtener productos con sus precios en USD desde stock
    productos = modelo_ventas.listar_productos_catalogo(
        clase_id=clase_id,
        marca_id=marca_id,
        q=q
    )
    
    # Calcular precios en bolívares
    productos = calcular_precios_bs(productos)
    
    # Obtener productos más vendidos para destacar
    mas_vendidos = modelo_ventas.productos_mas_vendidos(limite=5)
    mas_vendidos = calcular_precios_bs(mas_vendidos)
    
    # Obtener clases y marcas para filtros
    clases = modelo_productos.listar_clases() or []
    marcas = modelo_productos.listar_marcas() or []
    
    return jsonify({
        "success": True,
        "productos": productos,
        "mas_vendidos": mas_vendidos,
        "clases": clases,
        "marcas": marcas,
        "tasas": get_dolar_rates()
    })

@ventas_blueprint.route("/api/carrito", methods=["GET"])
@jwt_required
def api_obtener_carrito():
    """Obtener el carrito del cliente actual"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    cliente_id = obtener_cliente_id_actual()
    if not cliente_id:
        return jsonify({"success": False, "error": "Cliente no identificado"}), 400
    
    modelo = VentasModel()
    carrito = modelo.obtener_carrito(cliente_id)
    carrito = calcular_precios_bs(carrito)
    
    total_usd = sum(p["precio_usd"] * p["cantidad"] for p in carrito)
    total_bs_paralelo = sum(p["precio_bs_paralelo"] * p["cantidad"] for p in carrito)
    total_bs_oficial = sum(p["precio_bs_oficial"] * p["cantidad"] for p in carrito)
    
    return jsonify({
        "success": True,
        "items": carrito,
        "total_usd": round(total_usd, 2),
        "total_bs_paralelo": round(total_bs_paralelo, 2),
        "total_bs_oficial": round(total_bs_oficial, 2),
        "cantidad_items": len(carrito)
    })

@ventas_blueprint.route("/api/carrito", methods=["POST"])
@jwt_required
def api_agregar_carrito():
    """Agregar producto al carrito"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    cliente_id = obtener_cliente_id_actual()
    if not cliente_id:
        return jsonify({"success": False, "error": "Cliente no identificado"}), 400
    
    datos = request.get_json(silent=True) or {}
    producto_id = datos.get("producto_id")
    cantidad = datos.get("cantidad", 1)
    
    if not producto_id:
        return jsonify({"success": False, "error": "Producto no especificado"}), 400
    
    modelo = VentasModel()
    try:
        modelo.agregar_carrito(cliente_id, producto_id, cantidad)
        return jsonify({"success": True, "message": "Producto agregado al carrito"})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400

@ventas_blueprint.route("/api/carrito/<int:producto_id>", methods=["DELETE"])
@jwt_required
def api_eliminar_carrito(producto_id):
    """Eliminar producto del carrito"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    cliente_id = obtener_cliente_id_actual()
    if not cliente_id:
        return jsonify({"success": False, "error": "Cliente no identificado"}), 400
    
    modelo = VentasModel()
    modelo.eliminar_carrito_item(cliente_id, producto_id)
    return jsonify({"success": True})

@ventas_blueprint.route("/api/carrito", methods=["PUT"])
@jwt_required
def api_actualizar_cantidad():
    """Actualizar cantidad de un producto en el carrito"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    cliente_id = obtener_cliente_id_actual()
    if not cliente_id:
        return jsonify({"success": False, "error": "Cliente no identificado"}), 400
    
    datos = request.get_json(silent=True) or {}
    producto_id = datos.get("producto_id")
    cantidad = datos.get("cantidad", 1)
    
    modelo = VentasModel()
    modelo.actualizar_carrito_cantidad(cliente_id, producto_id, cantidad)
    return jsonify({"success": True})

@ventas_blueprint.route("/api/carrito/vaciar", methods=["DELETE"])
@jwt_required
def api_vaciar_carrito():
    """Vaciar todo el carrito"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    cliente_id = obtener_cliente_id_actual()
    if not cliente_id:
        return jsonify({"success": False, "error": "Cliente no identificado"}), 400
    
    modelo = VentasModel()
    modelo.vaciar_carrito(cliente_id)
    return jsonify({"success": True})

# ==================== PROCESO DE PAGO ====================

@ventas_blueprint.route("/pagar")
@jwt_required
def pagina_pagos():
    """Página de selección de método de pago"""
    if not hasattr(g, 'user') or not g.user:
        return redirect("/login")
    
    cliente_id = g.user.get("cedula") or g.user.get("cedula_personal") or g.user.get("id_c") or g.user.get("id_cliente")
    if not cliente_id:
        return redirect("/catalogo")
    
    modelo = VentasModel()
    carrito = modelo.obtener_carrito(cliente_id)
    
    if not carrito:
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
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    cliente_id = g.user.get("cedula") or g.user.get("cedula_personal") or g.user.get("id_c") or g.user.get("id_cliente")
    if not cliente_id:
        return jsonify({"success": False, "error": "Cliente no identificado"}), 400
    
    datos = request.get_json(silent=True) or {}
    metodo_pago = datos.get("metodo_pago")
    datos_pago = datos.get("datos_pago", {})
    
    if not metodo_pago:
        return jsonify({"success": False, "error": "Método de pago no seleccionado"}), 400
    
    modelo = VentasModel()
    
    # Obtener carrito
    carrito = modelo.obtener_carrito(cliente_id)
    if not carrito:
        return jsonify({"success": False, "error": "Carrito vacío"}), 400
    
    # Calcular totales
    tasas = get_dolar_rates()
    total_usd = sum(p["precio_usd"] * p["cantidad"] for p in carrito)
    total_bs = total_usd * tasas["paralelo"]
    
    # Crear factura
    factura_id = modelo.crear_venta(
        cliente_id=cliente_id,
        items=carrito,
        total_usd=total_usd,
        total_bs=total_bs,
        metodo_pago=metodo_pago,
        estado_pago="Por Verificar" if metodo_pago != "efectivo_bs" and metodo_pago != "efectivo_usd" else "Pendiente"
    )
    
    # Guardar reporte de pago según método
    if metodo_pago != "efectivo_bs" and metodo_pago != "efectivo_usd":
        modelo.guardar_reporte_pago(
            factura_id=factura_id,
            metodo_pago=metodo_pago,
            datos=datos_pago
        )
    
    # Vaciar carrito
    modelo.vaciar_carrito(cliente_id)
    
    return jsonify({
        "success": True,
        "factura_id": factura_id,
        "mensaje": "Venta registrada. Tu pago está siendo verificado."
    })

# ==================== VALIDACIÓN DE PAGOS (EMPLEADOS) ====================

@ventas_blueprint.route("/admin/validar-pagos")
@jwt_required
def pagina_validar_pagos():
    """Panel de validación de pagos para empleados"""
    return render_template(
        "ventas/validacion.html",
        show_navbar=True,
        show_notifications=True,
        active_page="validar_pagos"
    )

@ventas_blueprint.route("/api/admin/pagos-pendientes")
@jwt_required
def api_pagos_pendientes():
    """Obtener pagos pendientes de verificación"""
    modelo = VentasModel()
    pagos = modelo.obtener_pagos_pendientes()
    return jsonify({"success": True, "pagos": pagos})

@ventas_blueprint.route("/api/admin/pagos-aprobados")
@jwt_required
def api_pagos_aprobados():
    """Obtener pagos aprobados"""
    modelo = VentasModel()
    pagos = modelo.obtener_pagos_aprobados()
    return jsonify({"success": True, "pagos": pagos})

@ventas_blueprint.route("/api/admin/pagos-rechazados")
@jwt_required
def api_pagos_rechazados():
    """Obtener pagos rechazados"""
    modelo = VentasModel()
    pagos = modelo.obtener_pagos_rechazados()
    return jsonify({"success": True, "pagos": pagos})

@ventas_blueprint.route("/api/admin/aprobar-pago/<factura_id>", methods=["POST"])
@jwt_required
def api_aprobar_pago(factura_id):
    """Aprobar un pago"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    empleado_id = g.user.get("id_em") or g.user.get("id_empleado")
    
    modelo = VentasModel()
    modelo.aprobar_pago(factura_id, empleado_id)
    
    return jsonify({"success": True, "mensaje": "Pago aprobado correctamente"})

@ventas_blueprint.route("/api/admin/rechazar-pago/<factura_id>", methods=["POST"])
@jwt_required
def api_rechazar_pago(factura_id):
    """Rechazar un pago con motivo"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    datos = request.get_json(silent=True) or {}
    motivo = datos.get("motivo", "")
    
    if not motivo:
        return jsonify({"success": False, "error": "Debe especificar un motivo"}), 400
    
    empleado_id = g.user.get("id_em") or g.user.get("id_empleado")
    
    modelo = VentasModel()
    modelo.rechazar_pago(factura_id, empleado_id, motivo)
    
    return jsonify({"success": True, "mensaje": "Pago rechazado"})

@ventas_blueprint.route("/api/admin/ventas-local", methods=["POST"])
@jwt_required
def api_registrar_venta_local():
    """Registrar venta realizada en el local (efectivo)"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    empleado_id = g.user.get("id_em") or g.user.get("id_empleado")
    datos = request.get_json(silent=True) or {}
    
    cliente_id = datos.get("cliente_id")
    items = datos.get("items", [])
    total_pagado = datos.get("total_pagado")
    metodo_pago = datos.get("metodo_pago", "efectivo_usd")
    
    if not items:
        return jsonify({"success": False, "error": "Debe seleccionar al menos un producto"}), 400
    
    modelo = VentasModel()
    tasas = get_dolar_rates()
    
    # Calcular totales
    total_usd = 0
    for item in items:
        producto = modelo.obtener_producto(item["producto_id"])
        if producto:
            total_usd += producto["precio_usd"] * item["cantidad"]
    
    total_bs = total_usd * tasas["paralelo"]
    
    # Crear venta
    factura_id = modelo.crear_venta_local(
        cliente_id=cliente_id,
        empleado_id=empleado_id,
        items=items,
        total_usd=total_usd,
        total_bs=total_bs,
        metodo_pago=metodo_pago,
        total_pagado=total_pagado
    )
    
    return jsonify({
        "success": True,
        "factura_id": factura_id,
        "mensaje": "Venta registrada exitosamente"
    })

# ==================== ENTREGAS ====================

@ventas_blueprint.route("/api/admin/registrar-entrega", methods=["POST"])
@jwt_required
def api_registrar_entrega():
    """Registrar entrega de producto"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    datos = request.get_json(silent=True) or {}
    factura_id = datos.get("factura_id")
    empleado_delivery_id = datos.get("empleado_delivery_id")
    direccion = datos.get("direccion")
    
    modelo = VentasModel()
    modelo.registrar_entrega(factura_id, empleado_delivery_id, direccion)
    
    return jsonify({"success": True, "mensaje": "Entrega registrada"})