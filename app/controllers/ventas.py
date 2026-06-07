from flask import Blueprint, jsonify, render_template, request, g, redirect
from app.utils.decorators import jwt_required, tiene_permiso, solo_roles
from app.models.bitacora import registrar_en_bitacora
from app.models.catalogo import CatalogoModel
from app.models.carrito import CarritoModel
from app.models.venta import VentaModel
from app.models.pago_validacion import ValidacionPagosModel
from app.models.entrega import EntregaModel
import requests

ventas_blueprint = Blueprint("ventas", __name__)


def _usuario_actual() -> str:
    """Obtiene el ID del usuario actual"""
    user = getattr(g, 'user', None)
    if not user:
        return "SYSTEM"
    if isinstance(user, dict):
        return str(user.get("usuario_id") or user.get("id") or "SYSTEM")
    return str(getattr(user, "usuario_id", None) or getattr(user, "id", None) or "SYSTEM")


def _obtener_id_empleado() -> str:
    """Obtiene el ID del empleado actual (cédula como string)"""
    user = getattr(g, 'user', None)
    if not user:
        return None
    
    if isinstance(user, dict):
        cedula = user.get("cedula_personal") or user.get("cedula")
    else:
        cedula = getattr(user, "cedula_personal", None) or getattr(user, "cedula", None)
    
    return str(cedula) if cedula else None


def obtener_cliente_id_actual() -> str:
    """Obtiene el ID del cliente actual (cédula como string)"""
    usuario = getattr(g, "user", {}) or {}
    cliente_id = usuario.get("cedula") or usuario.get("cedula_personal") or usuario.get("id_c") or usuario.get("id_cliente")
    
    if not cliente_id:
        return None
    
    cliente_id_str = str(cliente_id)
    
    modelo_clientes = GestionClientes()
    existente = modelo_clientes.obtener_cliente_por_id(cliente_id_str)
    
    return cliente_id_str if existente else None


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
        p["precio_bs_oficial"] = round(p["precio_usd"] * tasas["oficial"], 2)
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
def api_listar_productos_catalogo():
    """API para obtener productos del catálogo con filtros"""
    modelo_catalogo = CatalogoModel()
    
    clase_id = request.args.get("clase_id", type=str)
    marca_id = request.args.get("marca_id", type=str)
    q = request.args.get("q", "")
    
    productos = modelo_catalogo.listar_productos_catalogo(
        clase_id=clase_id,
        marca_id=marca_id,
        q=q if q else None
    )
    
    tasas = get_dolar_rates()
    productos = calcular_precios_bs(productos, tasas)
    
    mas_vendidos = modelo_catalogo.productos_mas_vendidos(limite=5)
    mas_vendidos = calcular_precios_bs(mas_vendidos, tasas)
    
    clases = modelo_catalogo.listar_clases()
    marcas = modelo_catalogo.listar_marcas()
    
    return jsonify({
        "success": True,
        "productos": productos,
        "mas_vendidos": mas_vendidos,
        "clases": clases,
        "marcas": marcas,
        "tasas": tasas
    })


# ==================== CARRITO ====================

@ventas_blueprint.route("/api/carrito", methods=["GET"])
@jwt_required
def api_obtener_carrito():
    """Obtener el carrito del cliente actual"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    cliente_id = obtener_cliente_id_actual()
    if not cliente_id:
        return jsonify({"success": False, "error": "Cliente no identificado"}), 400
    
    modelo_carrito = CarritoModel()
    carrito = modelo_carrito.obtener_carrito(cliente_id)
    
    tasas = get_dolar_rates()
    carrito = calcular_precios_bs(carrito, tasas)
    
    total_usd = sum(p["precio_usd"] * p["cantidad"] for p in carrito)
    total_bs_paralelo = sum(p["precio_bs_paralelo"] * p["cantidad"] for p in carrito)
    total_bs_oficial = sum(p["precio_bs_oficial"] * p["cantidad"] for p in carrito)
    
    return jsonify({
        "success": True,
        "items": carrito,
        "total_usd": round(total_usd, 2),
        "total_bs_paralelo": round(total_bs_paralelo, 2),
        "total_bs_oficial": round(total_bs_oficial, 2),
        "tasas": tasas
    })


@ventas_blueprint.route("/api/carrito", methods=["POST"])
@jwt_required
@tiene_permiso('Carrito', 'modificar')
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
    
    modelo_carrito = CarritoModel()
    try:
        modelo_carrito.agregar_al_carrito(cliente_id, str(producto_id), cantidad)
        registrar_en_bitacora(
            accion="Agregar al carrito",
            descripcion=f"Cliente ID: {cliente_id} agregó producto ID: {producto_id} - Cantidad: {cantidad}",
            usuario_id=_usuario_actual(),
            modulo_nombre="Carrito"
        )
        return jsonify({"success": True, "message": "Producto agregado al carrito"})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@ventas_blueprint.route("/api/carrito/<string:producto_id>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Carrito', 'modificar')
def api_eliminar_carrito(producto_id):
    """Eliminar producto del carrito"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    cliente_id = obtener_cliente_id_actual()
    if not cliente_id:
        return jsonify({"success": False, "error": "Cliente no identificado"}), 400
    
    modelo_carrito = CarritoModel()
    modelo_carrito.eliminar_item(cliente_id, producto_id)
    return jsonify({"success": True})


@ventas_blueprint.route("/api/carrito", methods=["PUT"])
@jwt_required
@tiene_permiso('Carrito', 'modificar')
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
    
    modelo_carrito = CarritoModel()
    try:
        modelo_carrito.actualizar_cantidad(cliente_id, str(producto_id), cantidad)
        return jsonify({"success": True})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400


@ventas_blueprint.route("/api/carrito/vaciar", methods=["DELETE"])
@jwt_required
@tiene_permiso('Carrito', 'modificar')
def api_vaciar_carrito():
    """Vaciar todo el carrito"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    cliente_id = obtener_cliente_id_actual()
    if not cliente_id:
        return jsonify({"success": False, "error": "Cliente no identificado"}), 400
    
    modelo_carrito = CarritoModel()
    modelo_carrito.vaciar_carrito(cliente_id)
    return jsonify({"success": True})


# ==================== PROCESO DE PAGO ====================

@ventas_blueprint.route("/pagar")
@jwt_required
@tiene_permiso('Ventas', 'registrar')
def pagina_pagos():
    """Página de selección de método de pago"""
    if not hasattr(g, 'user') or not g.user:
        return redirect("/login")
    
    cliente_id = obtener_cliente_id_actual()
    if not cliente_id:
        return redirect("/catalogo")
    
    modelo_carrito = CarritoModel()
    carrito = modelo_carrito.obtener_carrito(cliente_id)
    
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
@tiene_permiso('Ventas', 'registrar')
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
    
    modelo_carrito = CarritoModel()
    modelo_venta = VentaModel()
    
    carrito = modelo_carrito.obtener_carrito(cliente_id)
    if not carrito:
        return jsonify({"success": False, "error": "Carrito vacío"}), 400
    
    # Crear la venta
    factura_id = modelo_venta.crear_venta_desde_carrito(
        cliente_id=cliente_id,
        items=carrito,
        metodo_pago=metodo_pago,
        estado_pago="Pendiente" if metodo_pago not in ("efectivo_bs", "efectivo_usd") else "Pagado"
    )
    
    # Guardar registro de pago (solo para métodos que no son efectivo)
    if metodo_pago not in ("efectivo_bs", "efectivo_usd"):
        modelo_venta.guardar_registro_pago(
            factura_id=factura_id,
            metodo_pago=metodo_pago,
            datos_pago=datos_pago
        )
    
    # Vaciar el carrito
    modelo_carrito.vaciar_carrito(cliente_id)
    
    registrar_en_bitacora(
        accion="Realizar venta",
        descripcion=f"Cliente ID: {cliente_id} realizó venta ID: {factura_id} - Método: {metodo_pago}",
        usuario_id=_usuario_actual(),
        modulo_nombre="Ventas"
    )
    
    return jsonify({
        "success": True,
        "factura_id": factura_id,
        "mensaje": "Venta registrada. Tu pago está siendo verificado."
    })


# ==================== VALIDACIÓN DE PAGOS ====================

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


@ventas_blueprint.route("/api/admin/pagos-pendientes")
@jwt_required
@tiene_permiso('Ventas', 'consultar')
def api_pagos_pendientes():
    """Obtener pagos pendientes de verificación"""
    modelo = ValidacionPagosModel()
    pagos = modelo.obtener_pagos_pendientes()
    return jsonify({"success": True, "pagos": pagos})


@ventas_blueprint.route("/api/admin/pagos-aprobados")
@jwt_required
@tiene_permiso('Ventas', 'consultar')
def api_pagos_aprobados():
    """Obtener pagos aprobados"""
    modelo = ValidacionPagosModel()
    pagos = modelo.obtener_pagos_aprobados()
    return jsonify({"success": True, "pagos": pagos})


@ventas_blueprint.route("/api/admin/pagos-rechazados")
@jwt_required
@tiene_permiso('Ventas', 'consultar')
def api_pagos_rechazados():
    """Obtener pagos rechazados"""
    modelo = ValidacionPagosModel()
    pagos = modelo.obtener_pagos_rechazados()
    return jsonify({"success": True, "pagos": pagos})


@ventas_blueprint.route("/api/admin/aprobar-pago/<factura_id>", methods=["POST"])
@jwt_required
@tiene_permiso('Ventas', 'modificar')
def api_aprobar_pago(factura_id):
    """Aprobar un pago"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    empleado_id = _obtener_id_empleado()
    
    modelo = ValidacionPagosModel()
    modelo.aprobar_pago(factura_id, empleado_id)
    
    registrar_en_bitacora(
        accion="Aprobar pago",
        descripcion=f"Se aprobó el pago de la factura ID: {factura_id}",
        usuario_id=_usuario_actual(),
        modulo_nombre="Ventas"
    )
    
    return jsonify({"success": True, "mensaje": "Pago aprobado correctamente"})


@ventas_blueprint.route("/api/admin/rechazar-pago/<factura_id>", methods=["POST"])
@jwt_required
@tiene_permiso('Ventas', 'modificar')
def api_rechazar_pago(factura_id):
    """Rechazar un pago con motivo"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    datos = request.get_json(silent=True) or {}
    motivo = datos.get("motivo", "")
    
    if not motivo:
        return jsonify({"success": False, "error": "Debe especificar un motivo"}), 400
    
    empleado_id = _obtener_id_empleado()
    
    modelo = ValidacionPagosModel()
    modelo.rechazar_pago(factura_id, empleado_id, motivo)
    
    registrar_en_bitacora(
        accion="Rechazar pago",
        descripcion=f"Se rechazó el pago de la factura ID: {factura_id} - Motivo: {motivo}",
        usuario_id=_usuario_actual(),
        modulo_nombre="Ventas"
    )
    
    return jsonify({"success": True, "mensaje": "Pago rechazado"})


# ==================== VENTAS LOCALES ====================

@ventas_blueprint.route("/api/clientes")
@jwt_required
def api_listar_clientes():
    """Listar clientes para autocompletado"""
    modelo_clientes = GestionClientes()
    clientes = modelo_clientes.listar_clientes()
    
    return jsonify({
        "success": True,
        "clientes": clientes
    })


@ventas_blueprint.route("/api/admin/ventas-local", methods=["POST"])
@jwt_required
@tiene_permiso('Ventas', 'registrar')
def api_registrar_venta_local():
    """Registrar venta realizada en el local"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    empleado_id = _obtener_id_empleado()
    datos = request.get_json(silent=True) or {}
    
    cliente_id = str(datos.get("cliente_id"))
    items = datos.get("items", [])
    metodo_pago = datos.get("metodo_pago", "efectivo_usd")
    
    if not cliente_id:
        return jsonify({"success": False, "error": "Cliente no especificado"}), 400
    
    if not items:
        return jsonify({"success": False, "error": "Debe seleccionar al menos un producto"}), 400
    
    modelo_venta = VentaModel()
    
    factura_id = modelo_venta.crear_venta_local(
        cliente_id=cliente_id,
        empleado_id=empleado_id,
        items=items,
        metodo_pago=metodo_pago
    )
    
    registrar_en_bitacora(
        accion="Registrar venta local",
        descripcion=f"Venta local registrada - Factura ID: {factura_id} - Cliente ID: {cliente_id}",
        usuario_id=_usuario_actual(),
        modulo_nombre="Ventas"
    )
    
    return jsonify({
        "success": True,
        "factura_id": factura_id,
        "mensaje": "Venta registrada exitosamente"
    })


# ==================== ENTREGAS ====================

@ventas_blueprint.route("/api/admin/registrar-entrega", methods=["POST"])
@jwt_required
@tiene_permiso('Ventas', 'modificar')
def api_registrar_entrega():
    """Registrar entrega de producto"""
    if not hasattr(g, 'user') or not g.user:
        return jsonify({"success": False, "error": "No autorizado"}), 401
    
    datos = request.get_json(silent=True) or {}
    factura_id = datos.get("factura_id")
    cedula_delivery = datos.get("cedula_delivery")
    direccion = datos.get("direccion")
    
    if not factura_id or not cedula_delivery or not direccion:
        return jsonify({"success": False, "error": "Faltan datos requeridos"}), 400
    
    modelo_entrega = EntregaModel()
    entrega_id = modelo_entrega.registrar_entrega(
        factura_id=factura_id,
        cedula_delivery=cedula_delivery,
        direccion=direccion
    )
    
    registrar_en_bitacora(
        accion="Registrar entrega",
        descripcion=f"Se registró entrega ID: {entrega_id} para factura ID: {factura_id}",
        usuario_id=_usuario_actual(),
        modulo_nombre="Ventas"
    )
    
    return jsonify({
        "success": True,
        "entrega_id": entrega_id,
        "mensaje": "Entrega registrada"
    })
