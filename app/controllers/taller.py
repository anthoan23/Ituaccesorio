import os
from uuid import uuid4

from flask import Blueprint, jsonify, render_template, request, current_app, g
from werkzeug.utils import secure_filename
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.bitacora import registrar_en_bitacora
from app.models.ordenes_servicio import Orden_servicio
from app.models.test import Tests
from app.models.inventario import Inventario

taller_blueprint = Blueprint("taller", __name__)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def _usuario_actual():
    """Obtiene el ID del usuario actual"""
    user = getattr(g, 'user', None)
    if not user:
        return "SYSTEM"
    if isinstance(user, dict):
        return str(user.get("usuario_id") or user.get("id") or "SYSTEM")
    return str(getattr(user, "usuario_id", None) or getattr(user, "id", None) or "SYSTEM")


def _obtener_id_empleado():
    """Obtiene el ID del empleado actual"""
    user = getattr(g, 'user', None)
    if not user:
        return 1004
    if isinstance(user, dict):
        cedula = user.get("cedula_personal")
    else:
        cedula = getattr(user, "cedula_personal", None)
    try:
        return int(cedula) if cedula else 1004
    except Exception:
        return 1004


def _is_allowed_image(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


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
    ordenes = Orden_servicio(ID_empleado=32014004)
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
@tiene_permiso('Taller', 'registrar')  # O el permiso que tengas configurado para guardar ('guardar', 'registrar', etc.)
def guardar_revision_tecnica():
    # 1. Capturar los datos provenientes de la petición JSON del frontend
    id_orden = request.json.get("id_orden")
    id_empleado = request.json.get("id_empleado")       # ID del técnico que realiza la revisión
    numero_test = request.json.get("numero_test")       # Identificador del lote de pruebas (ej: 1, 2)
    componentes = request.json.get("componentes_evaluados") # El arreglo: [{"nombre": "Mica", "resultado": "Funciona"}, ...]

    # 2. Validar que los datos requeridos no vengan vacíos
    if not id_orden or not id_empleado or not numero_test or not componentes:
        return jsonify({"error": "Faltan datos obligatorios para registrar la revisión técnica"}), 400

    # 3. Instanciar tu objeto o modelo de Tests (Ajusta el nombre de la clase si se llama distinto)
    # Seteamos las propiedades directamente en la instancia como lo requiere tu método modificado
    tests = Tests(
        ID_orden=id_orden,
        ID_empleado=id_empleado,
        Numero_test=numero_test,
        lista_tests=componentes
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



