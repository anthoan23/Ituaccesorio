import os
import uuid

from flask import Blueprint, jsonify, render_template, request, g, current_app
from werkzeug.utils import secure_filename
from app.utils.decorators import jwt_required, tiene_permiso, solo_roles
from app.models.tradein_empleados import TradeInEmpleados
from app.utils.validators import (
    validar_solo_letras,
    validar_solo_letras_numeros,
    validar_campo_comun,
    validar_sin_caracteres_especiales,
    validar_decimal
)
import traceback

tradein_empleados_blueprint = Blueprint("tradein_empleados", __name__)


# ==================== PÁGINAS ====================

@tradein_empleados_blueprint.route("/empleados/tradein")
@jwt_required
@solo_roles(['admin', 'ventas', 'tecnico'])
def pagina_tradein_empleados():
    return render_template(
        "tradein_empleados.html",
        show_navbar=True,
        show_notifications=True,
        active_page="tradein_empleados"
    )


# ==================== VALIDACIONES ====================

def _validar_datos_tradein(data):
    """
    Función auxiliar para validar los datos de trade-in.
    
    Args:
        data (dict): Datos del formulario
    
    Returns:
        tuple: (error_mensaje, error_codigo) o (None, None) si es válido
    """
    # Validar cliente (solo verificar que no esté vacío, la existencia se valida en el modelo)
    cliente_id = data.get("cliente_id", "").strip()
    if not cliente_id:
        return "El campo Cliente es obligatorio.", 400
    
    # Validar producto (solo verificar que no esté vacío, la existencia se valida en el modelo)
    id_producto = data.get("id_producto", "").strip()
    if not id_producto:
        return "El campo Producto/Modelo es obligatorio.", 400
    
    # Validar ID del equipo (IMEI) - solo números, sin espacios
    id_equipo = data.get("id_equipo", "").strip()
    if not id_equipo:
        return "El campo IMEI/ID del equipo es obligatorio.", 400
    
    error = validar_campo_comun(id_equipo, 'solo_numeros', "IMEI", min_len=8, max_len=20)
    if error:
        return error, 400
    
    # Validar color - solo letras, espacios, acentos y ñ
    color = data.get("color", "").strip()
    if color:
        error = validar_solo_letras(color, 1, 30, "Color", permitir_espacios=True)
        if error:
            return error, 400
    
    # Validar capacidad - solo letras y números
    capacidad = data.get("capacidad", "").strip()
    if capacidad:
        error = validar_solo_letras_numeros(capacidad, 1, 20, "Capacidad", permitir_espacios=True)
        if error:
            return error, 400
    
    # Validar clave numérica - solo números
    clave = data.get("clave", "").strip()
    if clave:
        error = validar_campo_comun(clave, 'solo_numeros', "Clave numérica", min_len=1, max_len=10)
        if error:
            return error, 400
    
    # Validar patrón - solo números
    patron = data.get("patron", "").strip()
    if patron:
        error = validar_campo_comun(patron, 'solo_numeros', "Patrón", min_len=1, max_len=20)
        if error:
            return error, 400
    
    # Validar valor pagado - decimal (hasta 2 decimales)
    valor_pagado = data.get("valor_pagado", "").strip()
    if not valor_pagado:
        return "El campo Valor pagado es obligatorio.", 400
    
    error = validar_decimal(valor_pagado, "Valor pagado")
    if error:
        return error, 400
    
    # Validar observaciones - sin caracteres especiales
    observaciones = data.get("observaciones", "").strip()
    if observaciones:
        error = validar_sin_caracteres_especiales(observaciones, 1, 500, "Observaciones", permitir_espacios=True)
        if error:
            return error, 400
    
    return None, 200


def _validar_tests_data(data):
    """
    Función auxiliar para validar los datos de tests.
    
    Args:
        data (dict): Datos de los tests
    
    Returns:
        tuple: (error_mensaje, error_codigo) o (None, None) si es válido
    """
    tests = data.get("tests", [])
    
    if not tests:
        return "Debe proporcionar al menos un test.", 400
    
    resultados_validos = ["Funciona", "No funciona", "No aplica", "Pendiente", "Sin revisar"]
    
    for i, test in enumerate(tests):
        nombre = test.get("nombre", "").strip()
        if not nombre:
            return f"El test #{i+1} debe tener un nombre.", 400
        
        # Validar que el nombre del test solo tenga caracteres válidos
        error = validar_sin_caracteres_especiales(nombre, 1, 100, f"Nombre del test #{i+1}", permitir_espacios=True)
        if error:
            return error, 400
        
        resultado = test.get("resultado", "").strip()
        if not resultado:
            return f"El test '{nombre}' debe tener un resultado.", 400
        
        # Validar que el resultado sea válido
        if resultado not in resultados_validos:
            return f"El resultado '{resultado}' no es válido para el test '{nombre}'. Opciones: {', '.join(resultados_validos)}", 400
    
    return None, 200


# ==================== REGISTRAR NUEVO TRADE-IN ====================

@tradein_empleados_blueprint.route("/api/tradein", methods=["POST"])
@jwt_required
@tiene_permiso('Trade-in', 'registrar')
def api_registrar_trade_in():
    try:
        # Validar datos
        error, status = _validar_datos_tradein(request.form)
        if error:
            return jsonify({"success": False, "error": error}), status
        
        cliente_id = request.form.get("cliente_id", "").strip()
        id_producto = request.form.get("id_producto", "").strip()
        valor_pagado = request.form.get("valor_pagado", "").strip()
        id_equipo = request.form.get("id_equipo", "").strip()
        color = request.form.get("color", "").strip() or None
        capacidad = request.form.get("capacidad", "").strip() or None
        clave = request.form.get("clave", "").strip() or None
        patron = request.form.get("patron", "").strip() or None
        observaciones = request.form.get("observaciones", "").strip() or None
        
        try:
            valor_pagado_float = float(valor_pagado)
        except ValueError:
            return jsonify({"success": False, "error": "El valor pagado debe ser un número válido"}), 400
        
        # Obtener usuario
        empleado_id = g.user.get("cedula") if isinstance(g.user, dict) else getattr(g.user, "cedula", None)
        empleado_id = str(empleado_id) if empleado_id else None
        
        if not empleado_id:
            return jsonify({"success": False, "error": "Empleado no identificado"}), 400
        
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", None)
        
        # Guardar fotos
        fotos = []
        archivos = request.files.getlist("fotos")
        for archivo in archivos:
            if archivo and getattr(archivo, "filename", ""):
                nombre_seguro = secure_filename(archivo.filename)
                _, extension = os.path.splitext(nombre_seguro)
                extension = extension.lower()[:10] or ".jpg"
                nombre_final = f"tradein_{uuid.uuid4().hex}{extension}"
                
                carpeta_destino = os.path.join(current_app.static_folder, "img", "evidencias", "trade_in")
                os.makedirs(carpeta_destino, exist_ok=True)
                
                ruta_fisica = os.path.join(carpeta_destino, nombre_final)
                archivo.save(ruta_fisica)
                fotos.append(f"/static/img/evidencias/trade_in/{nombre_final}")
        
        # Crear instancia del modelo con todos los datos
        modelo = TradeInEmpleados(
            cliente_id=cliente_id,
            id_producto=id_producto,
            valor_pagado=valor_pagado_float,
            empleado_id=empleado_id,
            id_equipo=id_equipo,
            usuario_id=usuario_id,
            color=color,
            capacidad=capacidad,
            clave=clave,
            patron=patron,
            observaciones=observaciones
        )
        
        resultado = modelo.registrar_trade_in(fotos=fotos)
        
        if resultado["success"]:
            return jsonify(resultado), 201
        else:
            return jsonify({"success": False, "error": resultado.get("error", "Error al registrar")}), 500
            
    except Exception as e:
        print(f"Error en api_registrar_trade_in: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@tradein_empleados_blueprint.route("/api/tradein/verificar-equipo/<id_equipo>", methods=["GET"])
@jwt_required
@tiene_permiso('Trade-in', 'consultar')
def api_verificar_equipo(id_equipo):
    try:
        modelo = TradeInEmpleados(id_equipo=id_equipo)
        equipo = modelo.verificar_equipo_existente()
        
        if equipo:
            return jsonify({
                "success": True,
                "exists": True,
                "equipo": equipo
            })
        else:
            return jsonify({
                "success": True,
                "exists": False
            })
    except Exception as e:
        print(f"Error en api_verificar_equipo: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== REGISTRAR TESTS ====================

@tradein_empleados_blueprint.route("/api/tradein/<tradein_id>/tests", methods=["POST"])
@jwt_required
@tiene_permiso('Trade-in', 'modificar')
def api_registrar_tests_trade_in(tradein_id):
    try:
        datos = request.get_json(silent=True) or {}
        
        error, status = _validar_tests_data(datos)
        if error:
            return jsonify({"success": False, "error": error}), status
        
        tests = datos.get("tests", [])
        
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", None)
        
        modelo = TradeInEmpleados(trade_in_id=tradein_id, usuario_id=usuario_id)
        resultado = modelo.registrar_tests_trade_in(tests)
        
        if resultado["success"]:
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
    try:
        modelo = TradeInEmpleados(cliente_id=cliente_id)
        resultados = modelo.obtener_trade_ins_por_cliente()
        return jsonify({"success": True, "tradeins": resultados})
    except Exception as e:
        print(f"Error en api_trade_ins_por_cliente: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== OBTENER DETALLES ====================

@tradein_empleados_blueprint.route("/api/tradein/<tradein_id>/detalle", methods=["GET"])
@jwt_required
@tiene_permiso('Trade-in', 'consultar')
def api_tradein_detalle(tradein_id):
    try:
        modelo = TradeInEmpleados(trade_in_id=tradein_id)
        detalle = modelo.obtener_detalle_trade_in()
        tests = modelo.obtener_tests_trade_in()
        fotos = modelo.obtener_fotos_trade_in()
        
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
    try:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", None)
        
        modelo = TradeInEmpleados(trade_in_id=tradein_id, usuario_id=usuario_id)
        resultado = modelo.eliminar_trade_in()
        
        if resultado["success"]:
            return jsonify(resultado), 200
        else:
            return jsonify({"success": False, "error": resultado.get("error", "Error al eliminar")}), 400
    except Exception as e:
        print(f"Error en api_eliminar_trade_in: {e}")
        return jsonify({"success": False, "error": str(e)}), 500