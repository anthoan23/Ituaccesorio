from flask import Blueprint, jsonify, render_template, request, g
import mysql.connector
import re

from app.models.clientes import GestionClientes
from app.models.bitacora import registrar_en_bitacora
from app.utils.decorators import jwt_required, tiene_permiso

clientes_blueprint = Blueprint("clientes", __name__)


def _usuario_actual():
    """Obtiene el ID del usuario actual"""
    user = getattr(g, 'user', None)
    if not user:
        return "SYSTEM"
    if isinstance(user, dict):
        return str(user.get("usuario_id") or user.get("id") or "SYSTEM")
    return str(getattr(user, "usuario_id", None) or getattr(user, "id", None) or "SYSTEM")


def _respuesta_error(mensaje, status=400):
    return jsonify({"success": False, "error": mensaje}), status


def _respuesta_por_excepcion(error):
    if isinstance(error, (ValueError, TypeError)):
        return _respuesta_error("Hay datos invalidos en la solicitud.", 400)

    if isinstance(error, mysql.connector.IntegrityError):
        errno = getattr(error, "errno", None)
        mensajes = {
            1062: "Ya existe un registro con esos datos.",
            1048: "Hay campos obligatorios sin completar.",
            1451: "No se puede eliminar porque el registro esta siendo usado.",
            1452: "La relacion indicada no existe o no es valida.",
        }
        return _respuesta_error(
            mensajes.get(errno, "No se pudo guardar la informacion por una restriccion de datos."),
            409,
        )

    if isinstance(error, mysql.connector.DataError):
        return _respuesta_error("El formato o tamaño de los datos no es valido.", 400)

    if isinstance(error, mysql.connector.ProgrammingError):
        return _respuesta_error("Ocurrio un error interno al procesar la solicitud.", 500)

    if isinstance(error, mysql.connector.OperationalError):
        return _respuesta_error("No fue posible conectar con la base de datos en este momento.", 503)

    if isinstance(error, mysql.connector.DatabaseError):
        return _respuesta_error("Se produjo un error al consultar la base de datos.", 500)

    return _respuesta_error("Ocurrio un error inesperado.", 500)


def _validar_celular(celular):
    """Valida formato de celular"""
    if not celular:
        return False
    # Eliminar espacios y caracteres especiales
    limpio = re.sub(r'[\s\-\(\)\+]', '', celular)
    return limpio.isdigit() and len(limpio) >= 10


@clientes_blueprint.route("/clientes", methods=["GET"])
@jwt_required
@tiene_permiso('Clientes', 'consultar')
def pagina_clientes():
    return render_template(
        "clientes.html",
        show_navbar=True,
        show_notifications=True,
        active_page="clientes",
    )


@clientes_blueprint.route("/api/clientes", methods=["GET"])
@jwt_required
@tiene_permiso('Clientes', 'consultar')
def listar_clientes():
    modelo = GestionClientes()
    datos = modelo.listar_clientes() or []
    return jsonify({"success": True, "clientes": datos})


@clientes_blueprint.route("/api/clientes", methods=["POST"])
@jwt_required
@tiene_permiso('Clientes', 'registrar')
def crear_cliente():
    datos = request.get_json(silent=True) or {}
    cedula = (datos.get("cedula") or "").strip()
    nombre = (datos.get("nombre") or "").strip()
    apellido = (datos.get("apellido") or "").strip()
    celular = (datos.get("celular") or "").strip()
    correo = (datos.get("correo") or "").strip()
    direccion = (datos.get("direccion") or "").strip()

    # Validaciones
    if not cedula or not nombre or not apellido or not celular:
        return _respuesta_error("Cédula, nombre, apellido y celular son obligatorios.")

    if not cedula.isdigit():
        return _respuesta_error("La cédula debe contener solo números.")

    if not _validar_celular(celular):
        return _respuesta_error("El número de celular debe tener al menos 10 dígitos.")

    if correo and '@' not in correo:
        return _respuesta_error("Ingrese un correo electrónico válido.")

    modelo = GestionClientes()
    try:
        cliente_id = int(cedula)
        nombre_completo = f"{nombre} {apellido}".strip()
        
        cliente_creado = modelo.crear_cliente(
            cliente_id=cliente_id,
            nombre=nombre_completo,
            apellido=apellido,
            celular=celular,
            correo=correo if correo else None,
            direccion=direccion if direccion else None
        )
        
        if not cliente_creado:
            return _respuesta_error("No se pudo crear el cliente.", 500)
        
        # Registrar en bitácora
        registrar_en_bitacora(
            accion="Crear cliente",
            descripcion=f"Se creó el cliente: {nombre} {apellido} - Cédula: {cedula} - Celular: {celular}",
            usuario_id=_usuario_actual(),
            modulo_nombre="Clientes"
        )
            
        return jsonify({"success": True, "message": "Cliente creado.", "id": cliente_creado})
    except Exception as error:
        return _respuesta_por_excepcion(error)


@clientes_blueprint.route("/api/clientes/<int:cliente_id>", methods=["GET"])
@jwt_required
@tiene_permiso('Clientes', 'consultar')
def obtener_cliente(cliente_id):
    modelo = GestionClientes()
    cliente = modelo.obtener_cliente_por_id(cliente_id)
    if not cliente:
        return _respuesta_error("Cliente no encontrado.", 404)
    return jsonify({"success": True, "cliente": cliente})


@clientes_blueprint.route("/api/clientes/<int:cliente_id>", methods=["PUT"])
@jwt_required
@tiene_permiso('Clientes', 'modificar')
def actualizar_cliente(cliente_id):
    datos = request.get_json(silent=True) or {}
    cedula = (datos.get("cedula") or "").strip()
    nombre = (datos.get("nombre") or "").strip()
    apellido = (datos.get("apellido") or "").strip()
    celular = (datos.get("celular") or "").strip()
    correo = (datos.get("correo") or "").strip()
    direccion = (datos.get("direccion") or "").strip()

    # Validaciones
    if not cedula or not nombre or not apellido or not celular:
        return _respuesta_error("Cédula, nombre, apellido y celular son obligatorios.")

    if not cedula.isdigit():
        return _respuesta_error("La cédula debe contener solo números.")

    if not _validar_celular(celular):
        return _respuesta_error("El número de celular debe tener al menos 10 dígitos.")

    modelo = GestionClientes()
    cliente_existente = modelo.obtener_cliente_por_id(cliente_id)
    if not cliente_existente:
        return _respuesta_error("Cliente no encontrado.", 404)

    try:
        nombre_completo = f"{nombre} {apellido}".strip()
        
        modelo.actualizar_cliente(
            cliente_id_actual=cliente_id,
            nuevo_cliente_id=int(cedula),
            nombre=nombre_completo,
            apellido=apellido,
            celular=celular,
            correo=correo if correo else None,
            direccion=direccion if direccion else None,
        )
        
        # Registrar en bitácora
        registrar_en_bitacora(
            accion="Actualizar cliente",
            descripcion=f"Se actualizó el cliente ID: {cliente_id} - Nuevo nombre: {nombre} {apellido} - Nuevo ID: {cedula}",
            usuario_id=_usuario_actual(),
            modulo_nombre="Clientes"
        )
        
        return jsonify({"success": True, "message": "Cliente actualizado."})
    except Exception as error:
        return _respuesta_por_excepcion(error)


@clientes_blueprint.route("/api/clientes/<int:cliente_id>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Clientes', 'eliminar')
def eliminar_cliente(cliente_id):
    modelo = GestionClientes()
    cliente_existente = modelo.obtener_cliente_por_id(cliente_id)
    if not cliente_existente:
        return _respuesta_error("Cliente no encontrado.", 404)

    try:
        nombre_cliente = f"{cliente_existente.get('nombre', '')} {cliente_existente.get('apellido', '')}".strip()
        
        modelo.eliminar_cliente(cliente_id)
        
        # Registrar en bitácora
        registrar_en_bitacora(
            accion="Eliminar cliente",
            descripcion=f"Se eliminó el cliente ID: {cliente_id} - Nombre: {nombre_cliente}",
            usuario_id=_usuario_actual(),
            modulo_nombre="Clientes"
        )
        
        return jsonify({"success": True, "message": "Cliente eliminado."})
    except Exception as error:
        return _respuesta_por_excepcion(error)