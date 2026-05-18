import os
from uuid import uuid4

from flask import Blueprint, jsonify, render_template, request, current_app
from werkzeug.utils import secure_filename
from app.utils.decorators import jwt_required
from app.models.ordenes_servicio import OrdenServicio
from app.models.test import Tests

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
	test_orden = test.buscar_ordenes(id_orden)
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


@taller_blueprint.route("/api/taller/fotos/<int:id_evidencia>", methods=["DELETE"])
@jwt_required
def eliminar_foto_orden(id_evidencia):
	ordenes = OrdenServicio()
	if not ordenes.eliminar_foto_orden(id_evidencia):
		return jsonify({"ok": False, "message": "No se pudo eliminar la imagen."}), 404

	return jsonify({"ok": True, "message": "Imagen eliminada correctamente."})