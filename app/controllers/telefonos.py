from flask import Blueprint, jsonify, render_template
from app.models.telefonos import Telefonos
from app.utils.decorators import jwt_required

telefonos_blueprint = Blueprint("telefonos", __name__)


@telefonos_blueprint.route("/telefonos", methods=["GET"])
@jwt_required
def pagina_telefonos():
	return render_template(
        "telefonos.html",
        show_navbar=True,
        show_notifications=True,
        active_page="telefonos",
	)

@telefonos_blueprint.route("/api/telefonos", methods=["GET"])
@jwt_required
def obtener_telefonos_json():
    modelo = Telefonos()
    telefonos_db = modelo.obtener_telefonos() or []
    return jsonify({
        "success": True,
        "telefonos": telefonos_db
    })
