from flask import Blueprint, jsonify, render_template, request
from app.utils.decorators import jwt_required
from app.models.ordenes_servicio import OrdenServicio
from app.models.test import Tests

taller_blueprint = Blueprint("taller", __name__)


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
	resultado = ordenes.listado_ordenes()
	return jsonify(resultado)

@taller_blueprint.route("/api/taller/ordenes/<int:id_orden>", methods=["POST"])
@jwt_required
def obtener_detalles_orden(id_orden):
	ordenes = OrdenServicio()
	test = Tests()
	detalle_orden = ordenes.detalles_orden(id_orden)
	fotos_orden = ordenes.fotos_orden(id_orden)
	test_orden = test.buscar_ordenes(id_orden)

	resultado = {
		"detalle_orden": detalle_orden,
		"fotos_orden": fotos_orden,
		"test_orden": test_orden
	}

	return jsonify(resultado)	