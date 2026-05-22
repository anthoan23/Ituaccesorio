from flask import Blueprint, jsonify, render_template, request, g

from app.models.empleados import Empleados
from app.models.ordenes_servicio import OrdenServicio
from app.models.test import Tests
from app.utils.decorators import jwt_required
import traceback

ordenes_servicio_blueprint = Blueprint("ordenes_servicio", __name__)


def _obtener_id_empleado() -> int:
    usuario = getattr(g, "user", {}) or {}
    if isinstance(usuario, dict):
        cedula = usuario.get("cedula_personal")
    else:
        cedula = getattr(usuario, "cedula_personal", None)
    try:
        return int(cedula) if cedula else 1004
    except Exception:
        return 1004


@ordenes_servicio_blueprint.route("/ordenes-servicio", methods=["GET"])
@jwt_required
def pagina_ordenes_servicio():
    return render_template(
        "ordenes_servicio.html",
        show_navbar=True,
        show_notifications=True,
        active_page="ordenes_servicio",
    )


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes", methods=["GET"])
@jwt_required
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

    id_empleado = _obtener_id_empleado()
    modelo.registrar_interaccion(nueva_id, id_empleado, "Recepcion")

    return jsonify({"success": True, "id": nueva_id})


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes/<int:id_orden>/asignar", methods=["POST"])
@jwt_required
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
    return jsonify({"success": True})


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/tecnicos", methods=["GET"])
@jwt_required
def listar_tecnicos():
    modelo = Empleados()
    tecnicos = modelo.listar_tecnicos() or []
    return jsonify({"success": True, "tecnicos": tecnicos})


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/tecnicos/<int:id_empleado>/ordenes", methods=["GET"])
@jwt_required
def listar_ordenes_tecnico(id_empleado):
    modelo = OrdenServicio()
    ordenes = modelo.ordenes_asignadas_tecnico(id_empleado) or []
    return jsonify({"success": True, "ordenes": ordenes})


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes/<int:id_orden>/revision", methods=["POST"])
@jwt_required
def registrar_test_orden(id_orden):
	# Espera JSON con los campos del test. ID_em y Fecha se gestionan en el servidor.
	datos = request.get_json() or {}

	# empleado por defecto (cambiar para usar usuario real)
	id_empleado = 1004

	# Campos en el mismo orden que la función registrar_test espera
	campos = [
		'ID_em', 'Num_test', 'Btn_power','Btn_vol','Cornetas','Mica','LCD','Tactil','Wifi',
		'Puerto_carga','Cam_pos','Cam_del','Microfono','Flash','Btn_sil','Auricular',
		'Senal','Sensor_proximidad','Face_id','Bluetooth','Observaciones'
	]

	valores = []
	for campo in campos:
		if campo == 'ID_em':
			valores.append(id_empleado)
			continue

		if campo in datos:
			v = datos.get(campo)
			# Empty string -> None (no revisado)
			if v is None or v == '':
				valores.append(None)
			else:
				# Observaciones is text
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
