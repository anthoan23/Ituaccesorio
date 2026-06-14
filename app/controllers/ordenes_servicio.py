from flask import Blueprint, jsonify, render_template, request, g
from app.models.empleados import Empleados
from app.models.ordenes_servicio import Orden_servicio as OrdenServicio
from app.models.test import Tests
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.equipo import Equipo

import traceback

ordenes_servicio_blueprint = Blueprint("ordenes_servicio", __name__)


@ordenes_servicio_blueprint.route("/ordenes-servicio", methods=["POST"])
@jwt_required
def registrar_equipo():
    data = request.get_json(silent=True) or request.form
    id_equipo = data.get("ID_equipo", "").strip()
    color = data.get("Color", "").strip()
    capacidad = data.get("Capacidad", "").strip() or None
    clave = data.get("Clave", "").strip() or None
    patron = data.get("Patron", "").strip()

    if not id_equipo or not color or not patron:
        return jsonify({"success": False, "message": "ID del equipo, color y patrón son obligatorios."}), 400

    try:
        id_equipo_val = int(id_equipo)
        patron_val = int(patron)
    except Exception:
        return jsonify({"success": False, "message": "ID del equipo y patrón deben ser números enteros."}), 400

    equipo_model = Equipo(
        ID_equipo=id_equipo_val,
        Color=color,
        Capacidad=capacidad,
        Clave=clave,
        Patron=patron_val
    )
    mensaje = equipo_model.registrar_equipo()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 201
    else:
        return jsonify({"success": False, "message": mensaje}), 400












def _obtener_nombre_cliente(cliente_id):
    """Obtiene el nombre de un cliente por su ID"""
    try:
        orden = OrdenServicio()
        # Buscar en órdenes existentes o llamar a un método específico
        ordenes = orden.listado_ordenes_servicio()
        for o in ordenes:
            if o.get("ID_cliente") == cliente_id:
                return o.get("Nombre_cliente", str(cliente_id))
    except Exception:
        pass
    return str(cliente_id)


@ordenes_servicio_blueprint.route("/ordenes-servicio", methods=["GET"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'consultar')
def pagina_ordenes_servicio():
    return render_template(
        "ordenes_servicio.html",
        show_navbar=True,
        show_notifications=True,
        active_page="ordenes_servicio",
    )


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes", methods=["GET"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'consultar')
def listar_ordenes_servicio():
    estado = (request.args.get("estado") or "").strip()
    estados = [s.strip() for s in estado.split(",") if s.strip()] if estado else []
    if estados:
        normalizadas = []
        for st in estados:
            if st.lower() in ("revisado", "revisada", "en revision", "en revisión"):
                normalizadas.extend(["Revisado", "En revisión"])
            else:
                normalizadas.append(st)
        estados = list(dict.fromkeys(normalizadas))

    modelo = OrdenServicio()
    try:
        ordenes = modelo.listado_ordenes_servicio(estados or None) or []
        return jsonify({"success": True, "ordenes": ordenes})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes/<int:id_orden>", methods=["GET"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'consultar')
def detalle_orden_servicio(id_orden):
    ordenes = OrdenServicio()
    tests = Tests()
    detalle = ordenes.detalles_orden(id_orden)
    if not detalle:
        return jsonify({"success": False, "error": "Orden no encontrada."}), 404
    fotos = ordenes.fotos_orden(id_orden) or []
    tests_orden = tests.buscar_test(id_orden) or []
    empleados = ordenes.empleados_asignados(id_orden) or []
    return jsonify(
        {
            "success": True,
            "detalle_orden": detalle,
            "fotos_orden": fotos,
            "test_orden": tests_orden,
            "empleados_orden": empleados,
        }
    )


@ordenes_servicio_blueprint.route("/api/ordenes-servicio", methods=["POST"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'registrar')
def crear_orden_servicio():
    datos = request.get_json(silent=True) or {}
    id_cliente = datos.get("id_cliente")
    id_modelo = datos.get("id_modelo")
    descripcion = (datos.get("descripcion") or "").strip()
    patron = datos.get("patron")
    clave = (datos.get("clave") or "").strip()
    fecha_ingreso = (datos.get("fecha_ingreso") or "").strip()
    nota = (datos.get("nota") or "").strip() or None

    if not id_cliente or not id_modelo or not descripcion or not fecha_ingreso:
        return jsonify({"success": False, "error": "Cliente, modelo, descripción y fecha son obligatorios."}), 400

    try:
        id_cliente_val = int(id_cliente)
        id_modelo_val = int(id_modelo)
    except Exception:
        return jsonify({"success": False, "error": "Cliente o modelo inválido."}), 400

    patron_val = None
    if patron not in (None, ""):
        try:
            patron_val = int(patron)
        except Exception:
            patron_val = None

    modelo = OrdenServicio()
    nueva_id = modelo.crear_orden(
        id_cliente=id_cliente_val,
        id_modelo=id_modelo_val,
        descripcion=descripcion,
        patron=patron_val,
        clave=clave or None,
        fecha_ingreso=fecha_ingreso,
        nota=nota,
    )
    if not nueva_id:
        return jsonify({"success": False, "error": "No se pudo crear la orden."}), 500

    # Obtener ID del empleado desde g.user
    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", 1004)
    try:
        id_empleado = int(usuario_id)
    except (ValueError, TypeError):
        id_empleado = 1004
    
    modelo.registrar_interaccion(nueva_id, id_empleado, "Recepcion")



    return jsonify({"success": True, "id": nueva_id})


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes/<int:id_orden>/asignar", methods=["POST"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'modificar')
def asignar_orden_servicio(id_orden):
    datos = request.get_json(silent=True) or {}
    id_empleado = datos.get("id_empleado")
    try:
        id_empleado_val = int(id_empleado)
    except Exception:
        return jsonify({"success": False, "error": "Empleado inválido."}), 400

    modelo = OrdenServicio()
    ok = modelo.asignar_orden_empleado(id_orden, id_empleado_val)
    if not ok:
        return jsonify({"success": False, "error": "No se pudo asignar la orden."}), 400
    
    # Obtener usuario actual
    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
    

    
    return jsonify({"success": True})


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/tecnicos", methods=["GET"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'consultar')
def listar_tecnicos():
    modelo = Empleados()
    tecnicos = modelo.listar_tecnicos() or []
    return jsonify({"success": True, "tecnicos": tecnicos})


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/tecnicos/<int:id_empleado>/ordenes", methods=["GET"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'consultar')
def listar_ordenes_tecnico(id_empleado):
    modelo = OrdenServicio()
    ordenes = modelo.ordenes_asignadas_tecnico(id_empleado) or []
    return jsonify({"success": True, "ordenes": ordenes})


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes/<int:id_orden>/revision", methods=["POST"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'modificar')
def registrar_test_orden(id_orden):
    datos = request.get_json() or {}
    
    # Obtener empleado ID desde g.user
    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", 1004)
    try:
        empleado_id = int(usuario_id)
    except (ValueError, TypeError):
        empleado_id = 1004

    campos = [
        'ID_em', 'Num_test', 'Btn_power','Btn_vol','Cornetas','Mica','LCD','Tactil','Wifi',
        'Puerto_carga','Cam_pos','Cam_del','Microfono','Flash','Btn_sil','Auricular',
        'Senal','Sensor_proximidad','Face_id','Bluetooth','Observaciones'
    ]

    valores = []
    for campo in campos:
        if campo == 'ID_em':
            valores.append(empleado_id)
            continue

        if campo in datos:
            v = datos.get(campo)
            if v is None or v == '':
                valores.append(None)
            else:
                if campo == 'Observaciones':
                    valores.append(str(v))
                else:
                    try:
                        valores.append(int(v))
                    except Exception:
                        valores.append(None)
        else:
            valores.append(None)

    test_model = Tests()
    ok = test_model.registrar_test(tuple(valores), id_orden)

    
    return jsonify({"ok": bool(ok)})


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes/<int:id_orden>/estado", methods=["PUT"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'modificar')
def actualizar_estado_orden(id_orden):
    """Actualiza el estado de una orden de servicio"""
    datos = request.get_json(silent=True) or {}
    nuevo_estado = datos.get("estado", "").strip()
    
    if not nuevo_estado:
        return jsonify({"success": False, "error": "El estado es obligatorio."}), 400
    
    modelo = OrdenServicio()
    ok = modelo.actualizar_estado(id_orden, nuevo_estado)
    
    if not ok:
        return jsonify({"success": False, "error": "No se pudo actualizar el estado."}), 400
    
    # Obtener usuario actual
    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
    
    # Registrar en bitácora
    registrar_en_bitacora(
        accion="Actualizar estado de orden",
        descripcion=f"Se actualizó el estado de la orden ID: {id_orden} a: {nuevo_estado}",
        usuario_id=usuario_id,
        modulo_nombre="Órdenes de servicio"
    )
    
    return jsonify({"success": True, "message": "Estado actualizado"})


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes/<int:id_orden>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'eliminar')
def eliminar_orden_servicio(id_orden):
    """Elimina una orden de servicio"""
    modelo = OrdenServicio()
    
    # Obtener información de la orden antes de eliminar
    detalle = modelo.detalles_orden(id_orden)
    nombre_cliente = detalle.get("Nombre_cliente", "N/A") if detalle else "N/A"
    
    ok = modelo.eliminar_orden(id_orden)
    
    if not ok:
        return jsonify({"success": False, "error": "No se pudo eliminar la orden."}), 400
    
    # Obtener usuario actual
    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
    


    
    return jsonify({"success": True, "message": "Orden eliminada"})