from flask import Blueprint, render_template

from app.utils.decorators import jwt_required


taller_blueprint = Blueprint("taller", __name__)


@taller_blueprint.route("/taller", methods=["GET"])
@jwt_required
def pagina_taller():
	return render_template(
		"taller.html",
		show_navbar=True,
		show_notifications=True,
		active_page="taller",
	)
