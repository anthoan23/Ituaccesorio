import os
from uuid import uuid4

from flask import Blueprint, jsonify, render_template, request, current_app, g
from werkzeug.utils import secure_filename
from app.utils.decorators import jwt_required
from app.models.ordenes_servicio import OrdenServicio
from app.models.test import Tests
from app.models.inventario import Inventario

taller_blueprint = Blueprint("taller", __name__)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def _is_allowed_image(filename: str) -> bool:
	return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


@taller_blueprint.route("/taller", methods=["GET"])
@jwt_required
def pagina_taller():
	return render_template(
		"taller.html",
		active_page="taller",
	)


@taller_blueprint.route("/api/taller/ordenes", methods=["GET"])
@jwt_required
def obtener_ordenes_taller():
	# Lógica para obtener las órdenes del taller
	ordenes = OrdenServicio()
	resultado = ordenes.listado_ordenes_taller()
	return jsonify(resultado)

@taller_blueprint.route("/api/taller/reparaciones-asignadas", methods=["GET"])
@jwt_required
def obtener_reparaciones_asignadas():
	# Lógica para obtener las reparaciones asignadas al empleado
	ordenes = OrdenServicio()
	resultado = ordenes.ordenes_asignadas_empleado()
	return jsonify(resultado)

@taller_blueprint.route("/api/taller/ordenes/<int:id_orden>", methods=["POST"])
@jwt_required
def obtener_detalles_orden(id_orden):
	ordenes = OrdenServicio()
	test = Tests()
	detalle_orden = ordenes.detalles_orden(id_orden)
	fotos_orden = ordenes.fotos_orden(id_orden)
	test_orden = test.buscar_test(id_orden)
	empleados_orden = ordenes.empleados_asignados(id_orden)

	resultado = {
		"detalle_orden": detalle_orden,
		"fotos_orden": fotos_orden,
		"test_orden": test_orden,
		"empleados_orden": empleados_orden
	}

	return jsonify(resultado)	

@taller_blueprint.route("/api/taller/asignar/<int:id_orden>/<int:id_empleado>/estado", methods=["POST"])
@jwt_required
def asignar_estado_orden(id_orden, id_empleado):
	id_empleado = 1004
	ordenes = OrdenServicio()
	resultado = ordenes.asignar_orden_empleado(id_orden, id_empleado)
	return jsonify(resultado)


@taller_blueprint.route("/api/taller/liberar/<int:id_orden>/<int:id_empleado>/estado", methods=["POST"])
@jwt_required
def liberar_estado_orden(id_orden, id_empleado):
	id_empleado = 1004
	ordenes = OrdenServicio()
	resultado = ordenes.liberar_orden(id_orden, id_empleado)
	return jsonify(resultado)


@taller_blueprint.route("/api/taller/ordenes/<int:id_orden>/fotos", methods=["POST"])
@jwt_required
def registrar_fotos_orden(id_orden):
	files = request.files.getlist("fotos")
	if not files:
		return jsonify({"ok": False, "message": "No se recibieron fotos."}), 400

	base_dir = os.path.join(current_app.static_folder, "img", "evidencias", "taller", str(id_orden))
	os.makedirs(base_dir, exist_ok=True)

	rutas_guardadas = []
	rutas_locales = []
	for file in files:
		if not file or not file.filename:
			continue
		if not _is_allowed_image(file.filename):
			return jsonify({"ok": False, "message": f"Archivo no permitido: {file.filename}"}), 400

		nombre_seguro = secure_filename(file.filename)
		ext = nombre_seguro.rsplit(".", 1)[1].lower() if "." in nombre_seguro else "jpg"
		nombre_final = f"{uuid4().hex}.{ext}"
		ruta_fs = os.path.join(base_dir, nombre_final)
		file.save(ruta_fs)
		rutas_locales.append(ruta_fs)
		rutas_guardadas.append(f"/static/img/evidencias/taller/{id_orden}/{nombre_final}")

	ordenes = OrdenServicio()
	if not ordenes.registrar_fotos_orden(id_orden, rutas_guardadas):
		for ruta_local in rutas_locales:
			if os.path.exists(ruta_local):
				os.remove(ruta_local)
		return jsonify({"ok": False, "message": "No se pudieron registrar las fotos."}), 500

	return jsonify({"ok": True, "message": "Fotos registradas correctamente.", "fotos": rutas_guardadas})


@taller_blueprint.route("/api/taller/ordenes/<int:id_orden>/test", methods=["POST"])
@jwt_required
def registrar_test_orden(id_orden):
	# Espera JSON con los campos del test. ID_em y Fecha se gestionan en el servidor.
	datos = request.get_json() or {}

	# empleado por defecto (cambiar para usar usuario real)
	usuario = getattr(g, "user", {}) or {}
	if isinstance(usuario, dict):
		cedula = usuario.get("cedula_personal")
	else:
		cedula = getattr(usuario, "cedula_personal", None)
	try:
		id_empleado = int(cedula) if cedula else 1004
	except Exception:
		id_empleado = 1004

	test_model = Tests()
	valores = test_model.construir_valores_test(datos, id_empleado)
	ok = test_model.registrar_test(valores, id_orden)

	if ok:
		ordenes = OrdenServicio()
		ordenes.registrar_interaccion(id_orden, id_empleado, "Revision")

		costo = datos.get("Costo") or datos.get("costo")
		revision = datos.get("Revision") or datos.get("revision")
		costo_val = None
		if costo not in (None, ""):
			try:
				costo_val = int(costo)
			except Exception:
				costo_val = None
		revision_val = None if revision in (None, "") else str(revision)
		if costo_val is not None or revision_val is not None:
			ordenes.actualizar_revision_cotizacion(id_orden, revision=revision_val, costo=costo_val)

	return jsonify({"ok": bool(ok)})


@taller_blueprint.route("/api/taller/inventario/<string:N_modelo>", methods=["POST"])
@jwt_required
def obtener_inventarios(N_modelo):
	inventario = Inventario()
	inventraio_taller = inventario.listar_inventario()
	inventraio_modelo = inventario.listar_inventario_modelo(N_modelo)
	resultado = {
		"inventario_taller": inventraio_taller,
		"inventario_modelo": inventraio_modelo
	}
	return jsonify(resultado)


@taller_blueprint.route("/api/taller/reparacion/<int:id_orden>", methods=["POST"])
@jwt_required
def registrar_reparacion_orden(id_orden):
	# Espera JSON: { "id_productos": [1,2], "cantidades": [1,1], "id_empleado": 1004, "reparacion": "texto" }
	datos = request.get_json() or {}
	id_productos = datos.get('id_productos')
	cantidades = datos.get('cantidades')
	id_empleado = datos.get('id_empleado', 1004)
	# Texto explicativo de la reparación (opcional)
	reparacion = datos.get('reparacion')

	if not isinstance(id_productos, (list, tuple)) or not isinstance(cantidades, (list, tuple)):
		return jsonify({"ok": False, "message": "id_productos y cantidades deben ser arrays."}), 400
	if len(id_productos) != len(cantidades):
		return jsonify({"ok": False, "message": "Las longitudes de id_productos y cantidades deben coincidir."}), 400

	# Convertir a enteros
	try:
		ids = [int(x) for x in id_productos]
		qts = [int(x) for x in cantidades]
		id_empleado = int(id_empleado)
	except Exception:
		return jsonify({"ok": False, "message": "Valores inválidos en id_productos o cantidades."}), 400

	# Normalizar reparacion a string o None
	if reparacion is None:
		reparacion_val = None
	else:
		reparacion_val = str(reparacion)

	ordenes = OrdenServicio()
	ok = ordenes.Orden_reparada(id_orden, ids, qts, id_empleado, reparacion_val)
	if ok:
		return jsonify({"ok": True})
	return jsonify({"ok": False, "message": "No se pudo registrar la reparación."}), 500


@taller_blueprint.route("/api/taller/fotos/<int:id_evidencia>", methods=["DELETE"])
@jwt_required
def eliminar_foto_orden(id_evidencia):
	ordenes = OrdenServicio()
	if not ordenes.eliminar_foto_orden(id_evidencia):
		return jsonify({"ok": False, "message": "No se pudo eliminar la imagen."}), 404

	return jsonify({"ok": True, "message": "Imagen eliminada correctamente."})


