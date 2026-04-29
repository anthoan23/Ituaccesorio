from flask import Blueprint, jsonify, render_template
from app.models.telefonos import Telefonos

telefonos_blueprint = Blueprint("telefonos", __name__)


@telefonos_blueprint.route("/telefonos", methods=["GET"])
def pagina_telefonos():
	return render_template(
		"telefonos.html"
	)

@telefonos_blueprint.route("/api/telefonos", methods=["GET"])
def obtener_telefonos_json():
    modelo = Telefonos()
    telefonos_db = modelo.obtener_telefonos() or []
    return jsonify({
        "success": True,
        "telefonos": telefonos_db
    })
