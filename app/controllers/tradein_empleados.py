from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso, solo_roles
from app.models.tradein_empleados import TradeInEmpleados
from app.models.bitacora import registrar_en_bitacora
import traceback
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

tradein_empleados_blueprint = Blueprint("tradein_empleados", __name__)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def _guardar_foto_trade_in(archivo):
    """Guarda una foto de trade-in y retorna la ruta"""
    if not archivo or not getattr(archivo, "filename", ""):
        return None
    
    if not "." in archivo.filename or archivo.filename.rsplit(".", 1)[1].lower() not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("Formato de imagen no válido")
    
    nombre_seguro = secure_filename(archivo.filename)
    _, extension = os.path.splitext(nombre_seguro)
    extension = extension.lower()[:10] or ".jpg"
    nombre_final = f"tradein_{uuid.uuid4().hex}{extension}"
    
    carpeta_destino = os.path.join(current_app.static_folder, "img", "evidencias", "trade_in")
    os.makedirs(carpeta_destino, exist_ok=True)
    
    ruta_fisica = os.path.join(carpeta_destino, nombre_final)
    archivo.save(ruta_fisica)
    return f"/static/img/evidencias/trade_in/{nombre_final}"


@tradein_empleados_blueprint.route("/empleados/tradein")
@jwt_required
@solo_roles(['admin', 'ventas', 'tecnico'])
def pagina_tradein_empleados():
    """Panel de gestión de Trade-In para empleados"""
    return render_template(
        "tradein_empleados.html",
        show_navbar=True,
        show_notifications=True,
        active_page="tradein_empleados"
    )


# ==================== REGISTRAR NUEVO TRADE-IN ====================

@tradein_empleados_blueprint.route("/api/tradein", methods=["POST"])
@jwt_required
@tiene_permiso('Trade-in', 'registrar')
def api_registrar_trade_in():
    """Registra un nuevo equipo recibido en trade-in"""
    try:
        # Obtener datos del formulario (multipart/form-data)
        cliente_id = request.form.get("cliente_id", "").strip()
        id_producto = request.form.get("id_producto", "").strip()
        valor_pagado = request.form.get("valor_pagado", "").strip()
        
        # Datos del equipo (opcionales)
        imei = request.form.get("imei", "").strip() or None
        color = request.form.get("color", "").strip() or None
        capacidad = request.form.get("capacidad", "").strip() or None
        clave = request.form.get("clave", "").strip() or None
        patron = request.form.get("patron", "").strip() or None
        observaciones = request.form.get("observaciones", "").strip() or None
        
        # Validaciones
        if not cliente_id:
            return jsonify({"success": False, "error": "Debe seleccionar un cliente"}), 400
        
        if not id_producto:
            return jsonify({"success": False, "error": "Debe seleccionar un producto/modelo"}), 400
        
        if not valor_pagado:
            return jsonify({"success": False, "error": "Debe ingresar el valor pagado"}), 400
        
        try:
            valor_pagado_float = float(valor_pagado)
        except ValueError:
            return jsonify({"success": False, "error": "El valor pagado debe ser un número válido"}), 400
        
        # Obtener empleado
        empleado_id = g.user.get("cedula") if isinstance(g.user, dict) else getattr(g.user, "cedula", None)
        empleado_id = str(empleado_id) if empleado_id else None
        
        if not empleado_id:
            return jsonify({"success": False, "error": "Empleado no identificado"}), 400
        
        # Guardar fotos
        fotos = []
        archivos = request.files.getlist("fotos")
        for archivo in archivos:
            try:
                ruta = _guardar_foto_trade_in(archivo)
                if ruta:
                    fotos.append(ruta)
            except ValueError as e:
                return jsonify({"success": False, "error": str(e)}), 400
        
        # Registrar trade-in
        modelo = TradeInEmpleados()
        resultado = modelo.registrar_trade_in(
            cliente_id=cliente_id,
            id_producto=id_producto,
            valor_pagado=valor_pagado_float,
            empleado_id=empleado_id,
            imei=imei,
            color=color,
            capacidad=capacidad,
            clave=clave,
            patron=patron,
            observaciones=observaciones,
            fotos=fotos
        )
        
        if resultado["success"]:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            
            registrar_en_bitacora(
                accion="Registrar Trade-in",
                descripcion=f"Se registró nuevo trade-in ID: {resultado['trade_in_id']} - Cliente: {cliente_id} - Valor: {valor_pagado}",
                usuario_id=usuario_id,
                modulo_nombre="Trade-in"
            )
            return jsonify(resultado), 201
        else:
            return jsonify({"success": False, "error": resultado.get("error", "Error al registrar")}), 500
            
    except Exception as e:
        print(f"Error en api_registrar_trade_in: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== REGISTRAR TESTS ====================

@tradein_empleados_blueprint.route("/api/tradein/<tradein_id>/tests", methods=["POST"])
@jwt_required
@tiene_permiso('Trade-in', 'modificar')
def api_registrar_tests_trade_in(tradein_id):
    """Registra los tests realizados a un equipo trade-in"""
    try:
        datos = request.get_json(silent=True) or {}
        tests = datos.get("tests", [])
        
        if not tests:
            return jsonify({"success": False, "error": "Debe proporcionar al menos un test"}), 400
        
        # Validar formato de tests
        for test in tests:
            if not test.get("nombre"):
                return jsonify({"success": False, "error": "Cada test debe tener un nombre"}), 400
            if not test.get("resultado"):
                return jsonify({"success": False, "error": "Cada test debe tener un resultado"}), 400
        
        modelo = TradeInEmpleados()
        resultado = modelo.registrar_tests_trade_in(tradein_id, tests)
        
        if resultado["success"]:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            
            registrar_en_bitacora(
                accion="Registrar tests Trade-in",
                descripcion=f"Se registraron {len(tests)} tests para trade-in ID: {tradein_id}",
                usuario_id=usuario_id,
                modulo_nombre="Trade-in"
            )
            return jsonify(resultado), 200
        else:
            return jsonify({"success": False, "error": resultado.get("error", "Error al registrar tests")}), 500
            
    except Exception as e:
        print(f"Error en api_registrar_tests_trade_in: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== LISTAR TRADE-INS ====================

@tradein_empleados_blueprint.route("/api/tradein", methods=["GET"])
@jwt_required
@tiene_permiso('Trade-in', 'consultar')
def api_listar_trade_ins():
    """Obtiene todos los trade-ins registrados"""
    try:
        modelo = TradeInEmpleados()
        resultados = modelo.obtener_trade_ins()
        return jsonify({"success": True, "tradeins": resultados})
    except Exception as e:
        print(f"Error en api_listar_trade_ins: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@tradein_empleados_blueprint.route("/api/tradein/cliente/<cliente_id>", methods=["GET"])
@jwt_required
@tiene_permiso('Trade-in', 'consultar')
def api_trade_ins_por_cliente(cliente_id):
    """Obtiene el historial de trade-ins de un cliente"""
    try:
        modelo = TradeInEmpleados()
        resultados = modelo.obtener_trade_ins_por_cliente(cliente_id)
        return jsonify({"success": True, "tradeins": resultados})
    except Exception as e:
        print(f"Error en api_trade_ins_por_cliente: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== OBTENER DETALLES ====================

@tradein_empleados_blueprint.route("/api/tradein/<tradein_id>/detalle", methods=["GET"])
@jwt_required
@tiene_permiso('Trade-in', 'consultar')
def api_tradein_detalle(tradein_id):
    """Obtiene el detalle completo de un trade-in"""
    try:
        modelo = TradeInEmpleados()
        detalle = modelo.obtener_detalle_trade_in(tradein_id)
        tests = modelo.obtener_tests_trade_in(tradein_id)
        fotos = modelo.obtener_fotos_trade_in(tradein_id)
        
        return jsonify({
            "success": True,
            "detalle": detalle,
            "tests": tests,
            "fotos": fotos
        })
    except Exception as e:
        print(f"Error en api_tradein_detalle: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== ESTADÍSTICAS ====================

@tradein_empleados_blueprint.route("/api/tradein/estadisticas", methods=["GET"])
@jwt_required
@tiene_permiso('Trade-in', 'consultar')
def api_tradein_estadisticas():
    """Obtiene estadísticas de trade-ins"""
    try:
        modelo = TradeInEmpleados()
        estadisticas = modelo.obtener_estadisticas()
        return jsonify({"success": True, "estadisticas": estadisticas})
    except Exception as e:
        print(f"Error en api_tradein_estadisticas: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== CATÁLOGOS PARA FORMULARIOS ====================

@tradein_empleados_blueprint.route("/api/tradein/productos", methods=["GET"])
@jwt_required
@tiene_permiso('Trade-in', 'consultar')
def api_productos_disponibles():
    """Obtiene productos disponibles para trade-in"""
    try:
        modelo = TradeInEmpleados()
        productos = modelo.obtener_productos_disponibles()
        return jsonify({"success": True, "productos": productos})
    except Exception as e:
        print(f"Error en api_productos_disponibles: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@tradein_empleados_blueprint.route("/api/tradein/clientes", methods=["GET"])
@jwt_required
@tiene_permiso('Trade-in', 'consultar')
def api_buscar_clientes():
    """Busca clientes para autocompletar"""
    try:
        q = request.args.get("q", "").strip()
        modelo = TradeInEmpleados()
        clientes = modelo.obtener_clientes(q if q else None)
        return jsonify({"success": True, "clientes": clientes})
    except Exception as e:
        print(f"Error en api_buscar_clientes: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@tradein_empleados_blueprint.route("/api/tradein/catalogo-tests", methods=["GET"])
@jwt_required
@tiene_permiso('Trade-in', 'consultar')
def api_catalogo_tests():
    """Obtiene el catálogo de pruebas disponibles para realizar al equipo"""
    catalogo_tests = [
        {"nombre": "Botón power", "categoria": "Botones"},
        {"nombre": "Botones volumen", "categoria": "Botones"},
        {"nombre": "Cornetas", "categoria": "Audio"},
        {"nombre": "Mica", "categoria": "Pantalla"},
        {"nombre": "LCD", "categoria": "Pantalla"},
        {"nombre": "Táctil", "categoria": "Pantalla"},
        {"nombre": "Botones laterales", "categoria": "Botones"},
        {"nombre": "Botones inferiores", "categoria": "Botones"},
        {"nombre": "Puerto de carga", "categoria": "Conectividad"},
        {"nombre": "WiFi", "categoria": "Conectividad"},
        {"nombre": "Bluetooth", "categoria": "Conectividad"},
        {"nombre": "Cámara trasera", "categoria": "Cámara"},
        {"nombre": "Cámara delantera", "categoria": "Cámara"},
        {"nombre": "Flash", "categoria": "Cámara"},
        {"nombre": "Micrófono", "categoria": "Audio"},
        {"nombre": "Sensor de proximidad", "categoria": "Sensores"},
        {"nombre": "Face ID", "categoria": "Seguridad"},
        {"nombre": "Batería", "categoria": "Batería"},
        {"nombre": "Altavoz", "categoria": "Audio"},
        {"nombre": "Vibrador", "categoria": "Otros"},
        {"nombre": "GPS", "categoria": "Conectividad"},
        {"nombre": "NFC", "categoria": "Conectividad"},
    ]
    return jsonify({"success": True, "tests": catalogo_tests})


# ==================== ELIMINAR ====================

@tradein_empleados_blueprint.route("/api/tradein/<tradein_id>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Trade-in', 'eliminar')
def api_eliminar_trade_in(tradein_id):
    """Elimina un trade-in"""
    try:
        modelo = TradeInEmpleados()
        resultado = modelo.eliminar_trade_in(tradein_id)
        
        if resultado["success"]:
            usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
            
            registrar_en_bitacora(
                accion="Eliminar Trade-in",
                descripcion=f"Se eliminó el trade-in ID: {tradein_id}",
                usuario_id=usuario_id,
                modulo_nombre="Trade-in"
            )
            return jsonify(resultado), 200
        else:
            return jsonify({"success": False, "error": resultado.get("error", "Error al eliminar")}), 400
    except Exception as e:
        print(f"Error en api_eliminar_trade_in: {e}")
        return jsonify({"success": False, "error": str(e)}), 500