import os
from uuid import uuid4

from flask import Blueprint, jsonify, render_template, request, current_app, g
from werkzeug.utils import secure_filename
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.ordenes_servicio import Orden_servicio
from app.models.test import Tests
from app.models.inventario import Inventario

taller_blueprint = Blueprint("taller", __name__)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}





@taller_blueprint.route("/taller", methods=["GET"])
@jwt_required
@tiene_permiso('Taller', 'consultar')
def pagina_taller():
    return render_template(
        "taller.html",
        active_page="taller",
        show_navbar=True,
        show_notifications=True,
    )


@taller_blueprint.route("/api/taller/ordenes", methods=["GET"])
@jwt_required
@tiene_permiso('Taller', 'consultar')
def obtener_ordenes_taller():
    ordenes = Orden_servicio()
    resultado = ordenes.listar_ordenes_taller()
    return jsonify(resultado)


@taller_blueprint.route("/api/taller/reparaciones-asignadas", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'consultar')
def obtener_reparaciones_asignadas():
    # Obtener ID del empleado desde g.user
    usuario_id = g.user.get("cedula_personal") if isinstance(g.user, dict) else getattr(g.user, "cedula_personal", None)
    try:
        id_empleado = int(usuario_id) if usuario_id else 32014004
    except (ValueError, TypeError):
        id_empleado = 32014004
    
    ordenes = Orden_servicio(ID_empleado=id_empleado)
    resultado = ordenes.listar_ordenes_tecnico()
    return jsonify(resultado)


@taller_blueprint.route("/api/taller/consultar-ordene", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'consultar')
def consultar_orden():
    id_orden = request.json.get("id_orden")
    if not id_orden:
        return jsonify({"error": "ID de orden no proporcionado"}), 400

    ordenes = Orden_servicio(ID_orden_servicio=id_orden)
    tests = Tests(ID_orden=id_orden)

    resultado_orden = ordenes.consultar_orden()
    resultado_tests = tests.listas_tests()

    # CORRECCIÓN: Validar si la consulta de la orden falló o no encontró nada antes de armar la respuesta
    if resultado_orden is None:
        return jsonify({"error": "Error al consultar la orden"}), 500
    elif not resultado_orden:
        return jsonify({"error": "Orden no encontrada"}), 404

    resultado = {
        "orden": resultado_orden, 
        "tests": resultado_tests
    }
    return jsonify(resultado)


@taller_blueprint.route("/api/taller/consultar-test", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'consultar')
def consultar_test():
    id_orden = request.json.get("id_orden")
    numero_test = request.json.get("numero_test")
    if not id_orden or not numero_test:
        return jsonify({"error": "ID de orden o número de test no proporcionado"}), 400

    tests = Tests(ID_orden=id_orden, Numero_test=numero_test)
    resultado_test = tests.consultar_test()

    if resultado_test is None:
        return jsonify({"error": "Error al consultar el test"}), 500
    elif not resultado_test:
        return jsonify({"error": "Test no encontrado para la orden especificada"}), 404

    return jsonify(resultado_test)


@taller_blueprint.route("/api/taller/guardar-revision", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'editar')
def guardar_revision_tecnica():
    id_orden = request.json.get("id_orden")
    id_empleado = 32014004
    numero_test = request.json.get("numero_test")
    componentes = request.json.get("componentes_evaluados")

    if not id_orden or not id_empleado or not numero_test or not componentes:
        return jsonify({"error": "Faltan datos obligatorios para registrar la revisión técnica"}), 400

    # Obtener usuario actual para bitácora
    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    tests = Tests(
        ID_orden=id_orden,
        ID_empleado=id_empleado,
        Numero_test=numero_test,
        lista_tests=componentes,
        usuario_id=usuario_actual_id
    )

    # 4. Ejecutar el método que modificaste
    resultado_mensaje = tests.registrar_revision_test()

    # 5. Evaluar la respuesta del método para retornar el código HTTP correcto
    if "exitosamente" in resultado_mensaje:
        return jsonify({"mensaje": resultado_mensaje}), 200
    
    # Si devuelve algún mensaje de validación del ID, longitud o nulos
    elif "inválido" in resultado_mensaje or "obligatorio" in resultado_mensaje or "lista válida" in resultado_mensaje:
        return jsonify({"error": resultado_mensaje}), 400
        
    # Cualquier otro error interno de base de datos o excepciones (Exceptions)
    else:
        return jsonify({"error": resultado_mensaje}), 500


@taller_blueprint.route("/api/taller/asignar-orden", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'editar')
def asignar_orden_tecnico():
    id_orden = request.json.get("id_orden")
    id_empleado = 32014004

    if not id_orden or not id_empleado:
        return jsonify({"error": "ID de orden o ID de empleado no proporcionado"}), 400

    # Obtener usuario actual para bitácora
    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    ordenes = Orden_servicio(
        ID_orden_servicio=id_orden, 
        ID_empleado=id_empleado,
    )
    resultado = ordenes.asignar_orden_empleado()

    if resultado is True:
        return jsonify({"mensaje": "Técnico asignado exitosamente a la orden"}), 200
    else:
        return jsonify({"error": "Error al asignar el técnico a la orden"}), 500


@taller_blueprint.route("/api/taller/liberar-orden", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'editar')
def liberar_orden_tecnico():
    id_orden = request.json.get("id_orden")
    id_empleado = 32014004

    if not id_orden or not id_empleado:
        return jsonify({"error": "ID de orden o ID de empleado no proporcionado"}), 400

    ordenes = Orden_servicio(ID_orden_servicio=id_orden, ID_empleado=id_empleado)
    resultado = ordenes.liberar_orden_empleado()

    if resultado is True:
        return jsonify({"mensaje": "Técnico liberado exitosamente de la orden"}), 200
    else:
        return jsonify({"error": "Error al liberar el técnico de la orden"}), 500


@taller_blueprint.route("/api/taller/consultar-inventario", methods=["GET"])
@jwt_required
@tiene_permiso('Taller', 'consultar')
def consultar_inventario():
    inventario = Inventario()
    resultado = inventario.listar_inventario_taller()
    return jsonify(resultado)


@taller_blueprint.route("/api/taller/guardar-reparacion", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'registrar')
def registrar_reparacion():
    try:
        # Obtener datos del request
        data = request.json
        
        # Validar campos obligatorios
        id_orden = data.get("id_orden")
        descripcion = data.get("descripcion_reparacion")
        
        if not id_orden:
            return jsonify({"error": "El ID de orden es obligatorio"}), 400
        if not descripcion:
            return jsonify({"error": "La descripción de reparación es obligatoria"}), 400
        
        # Procesar lista de repuestos (convertir a JSON si es necesario)
        repuestos = data.get("repuestos_utilizados")
        if repuestos and isinstance(repuestos, (list, dict)):
            import json
            repuestos = json.dumps(repuestos)
        
        # Obtener usuario actual para bitácora
        usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
        
        # Crear instancia de Orden_servicio
        ordenes = Orden_servicio(
            ID_empleado=32014004,
            ID_orden_servicio=id_orden,
            Descripcion_reparacion=descripcion,
            lista_repuestos=repuestos,
        )
        
        # Registrar reparación
        resultado = ordenes.registrar_reparacion()
        
        # Procesar respuesta
        if resultado.get("success"):
            return jsonify({
                "mensaje": resultado.get("mensaje", "Reparación registrada exitosamente"),
                "data": resultado.get("data")
            }), 200
        else:
            error_msg = resultado.get("error", "Error desconocido")
            # Determinar código de estado según el error
            if any(palabra in error_msg.lower() for palabra in ["inválido", "obligatorio", "válida", "no encontrado"]):
                return jsonify({"error": error_msg}), 400
            elif "permiso" in error_msg.lower() or "autorización" in error_msg.lower():
                return jsonify({"error": error_msg}), 403
            else:
                return jsonify({"error": error_msg}), 500
                
    except Exception as e:
        print(f"Error en la ruta: {e}")
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
