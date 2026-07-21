from flask import Blueprint, jsonify, render_template, request, g
from app.utils.decorators import jwt_required, tiene_permiso
from app.utils.validators import validar_numero, validar_texto, validar_texto_numero, validar_email
from app.models.empleados import Empleados

empleados_blueprint = Blueprint("empleados", __name__)


@empleados_blueprint.route("/empleados", methods=["GET"])
@jwt_required
@tiene_permiso('Empleados', 'consultar')
def pagina_empleados():
    return render_template(
        "empleados.html",
        show_navbar=True,
        show_notifications=True,
        active_page="empleados",
    )


@empleados_blueprint.route("/api/empleados", methods=["GET"])
@jwt_required
@tiene_permiso('Empleados', 'consultar')
def api_listar_empleados():
    empleados_model = Empleados()
    resultado = empleados_model.listar_empleados()
    return jsonify(resultado)


@empleados_blueprint.route("/api/empleados/lista", methods=["GET"])
@jwt_required
@tiene_permiso('Empleados', 'consultar')
def api_listar_empleados_cargos():
    empleados_model = Empleados()
    resultado1 = empleados_model.listar_cargos()
    resultado2 = empleados_model.listar_especialidades()
    return jsonify({"cargos": resultado1, "especialidades": resultado2})


@empleados_blueprint.route("/api/empleados/graficos", methods=["GET"])
@jwt_required
@tiene_permiso('Empleados', 'consultar')
def api_listar_empleados_graficos():
    empleados_model = Empleados()
    resultado1 = empleados_model.listar_empleados_por_cargo()
    resultado2 = empleados_model.listar_empleados_por_especialidad()
    return jsonify({"cargos": resultado1, "especialidades": resultado2})


@empleados_blueprint.route("/api/empleados/consultar", methods=["POST"])
@jwt_required
@tiene_permiso('Empleados', 'consultar')
def api_consultar_empleado():
    datos = request.get_json(silent=True) or {}
    cedula = str(datos.get("cedula", "")).strip()
    
    validar_cedula = validar_numero(cedula, 6, 9, "Cédula")
    if validar_cedula:
        return jsonify({"success": False, "error": validar_cedula}), 400

    empleados_model = Empleados(id_empleado=cedula)
    resultado1 = empleados_model.consultar_empleado()
    
    if not resultado1:
        return jsonify({"success": False, "error": "Empleado no encontrado."}), 404
    
    
    if resultado1['cargo'] == 'Técnico':
        resultado2 = empleados_model.consultar_especialidades_empleado()
        return jsonify({"success": True, "empleado": resultado1, "especialidades": resultado2})
    
    return jsonify({"success": True, "empleado": resultado1})


@empleados_blueprint.route("/api/empleados", methods=["POST"])
@jwt_required
@tiene_permiso('Empleados', 'registrar')
def api_agregar_empleado():
    datos = request.get_json(silent=True) or {}

    cedula = str(datos.get("cedula", "")).strip()
    cargo_id = str(datos.get("id_cargo", "")).strip()
    nombre = str(datos.get("nombre", "")).strip()
    apellido = str(datos.get("apellido", "")).strip()
    celular = str(datos.get("celular", "")).strip()
    correo = str(datos.get("correo", "")).strip()
    direccion = str(datos.get("direccion", "")).strip()

    validar_cedula = validar_numero(cedula, 6, 9, "Cédula")
    if validar_cedula:
        return jsonify({"success": False, "error": validar_cedula}), 400
    
    validar_cargo_id = validar_texto_numero(cargo_id, 1, 10, "ID del Cargo")
    if validar_cargo_id:
        return jsonify({"success": False, "error": validar_cargo_id}), 400
    
    validar_nombre = validar_texto(nombre, 3, 30, "Nombre")
    if validar_nombre:
        return jsonify({"success": False, "error": validar_nombre}), 400
    
    validar_apellido = validar_texto(apellido, 3, 30, "Apellido")
    if validar_apellido:
        return jsonify({"success": False, "error": validar_apellido}), 400
    
    validar_celular = validar_numero(celular, 9, 15, "Celular")
    if validar_celular:
        return jsonify({"success": False, "error": validar_celular}), 400

    validar_email_ = validar_email(correo)
    if validar_email_:
        return jsonify({"success": False, "error": validar_email_}), 400
    
    validar_direccion = validar_texto_numero(direccion, 2, 60, "Dirección")
    if validar_direccion:
        return jsonify({"success": False, "error": validar_direccion}), 400

    especialidades = datos.get('especialidades') or []
    if isinstance(especialidades, str):
        try:
            import json
            especialidades = json.loads(especialidades)
        except Exception:
            especialidades = [s.strip() for s in especialidades.split(',') if s.strip()]

    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    empleados_model = Empleados(
        id_empleado=cedula,
        id_cargo=cargo_id,
        nombre_empleado=nombre,
        apellido_empleado=apellido,
        celular_empleado=celular,
        correo_empleado=correo,
        direccion_empleado=direccion,
        especialidades=especialidades,
        usuario_id=usuario_id
    )
    
    mensaje = empleados_model.agregar_empleado()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 201
    
    return jsonify({"success": False, "error": mensaje}), 400


@empleados_blueprint.route("/api/empleados", methods=["PUT"])
@jwt_required
@tiene_permiso('Empleados', 'modificar')
def api_actualizar_empleado():
    datos = request.get_json(silent=True) or {}
    
    id_empleado = str(datos.get("id_empleado", "")).strip()
    cedula = str(datos.get("cedula", "")).strip()
    cargo_id = str(datos.get("id_cargo", "")).strip()
    nombre = str(datos.get("nombre", "")).strip()
    apellido = str(datos.get("apellido", "")).strip()
    celular = str(datos.get("celular", "")).strip()
    correo = str(datos.get("correo", "")).strip()
    direccion = str(datos.get("direccion", "")).strip()


    validar_cedula = validar_numero(cedula, 6, 9, "Cédula")
    if validar_cedula:
        return jsonify({"success": False, "error": validar_cedula}), 400
    
    validar_cargo_id = validar_texto_numero(cargo_id, 1, 10, "ID del Cargo")
    if validar_cargo_id:
        return jsonify({"success": False, "error": validar_cargo_id}), 400
    
    validar_empleado_id = validar_texto_numero(id_empleado, 6, 9, "ID del Empleado")
    if validar_empleado_id:
        return jsonify({"success": False, "error": validar_empleado_id}), 400
    
    validar_nombre = validar_texto(nombre, 3, 30, "Nombre")
    if validar_nombre:
        return jsonify({"success": False, "error": validar_nombre}), 400
    
    validar_apellido = validar_texto(apellido, 3, 30, "Apellido")
    if validar_apellido:
        return jsonify({"success": False, "error": validar_apellido}), 400
    
    validar_celular = validar_numero(celular, 10, 10, "Celular")
    if validar_celular:
        return jsonify({"success": False, "error": validar_celular}), 400

    validar_email_ = validar_email(correo)
    if validar_email_:
        return jsonify({"success": False, "error": validar_email_}), 400
    
    validar_direccion = validar_texto_numero(direccion, 2, 60, "Dirección")
    if validar_direccion:
        return jsonify({"success": False, "error": validar_direccion}), 400
    

    especialidades = datos.get('especialidades') or []
    if isinstance(especialidades, str):
        try:
            import json
            especialidades = json.loads(especialidades)
        except Exception:
            especialidades = [s.strip() for s in especialidades.split(',') if s.strip()]

    if not id_empleado:
        return jsonify({"success": False, "error": "El ID del empleado es obligatorio."}), 400
    
    if not all([cedula, cargo_id, nombre, apellido]):
        return jsonify({
            "success": False,
            "error": "La cédula, cargo, nombre y apellido son obligatorios.",
        }), 400

    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    empleados_model = Empleados(
        id_empleado=id_empleado,
        id_cargo=cargo_id,
        nombre_empleado=nombre,
        apellido_empleado=apellido,
        celular_empleado=celular,
        correo_empleado=correo,
        direccion_empleado=direccion,
        especialidades=especialidades,
        usuario_id=usuario_id
    )
    
    mensaje = empleados_model.actualizar_empleado()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200
    
    return jsonify({"success": False, "error": mensaje}), 400


@empleados_blueprint.route("/api/empleados", methods=["DELETE"])
@jwt_required
@tiene_permiso('Empleados', 'eliminar')
def api_eliminar_empleado():
    datos = request.get_json(silent=True) or {}
    id_empleado = str(datos.get("id_empleado", "")).strip()

    validar_empleado_id = validar_texto_numero(id_empleado, 6, 9, "ID del Empleado")
    if validar_empleado_id:
        return jsonify({"success": False, "error": validar_empleado_id}), 400

    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    empleados_model = Empleados(
        id_empleado=id_empleado,
        usuario_id=usuario_id
    )
    
    mensaje = empleados_model.eliminar_empleado()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200
    
    return jsonify({"success": False, "error": mensaje}), 400


@empleados_blueprint.route("/api/empleados/tecnicos", methods=["GET"])
@jwt_required
@tiene_permiso('Empleados', 'consultar')
def api_listar_tecnicos():
    empleados_model = Empleados()
    tecnicos = empleados_model.listar_tecnicos()
    return jsonify(tecnicos)