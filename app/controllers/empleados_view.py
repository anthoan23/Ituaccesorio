from flask import Blueprint, render_template
from app.utils.decorators import jwt_required, tiene_permiso

empleados_blueprint = Blueprint("empleados", __name__)


@empleados_blueprint.route("/empleados", methods=["GET"])
@jwt_required
@tiene_permiso("Productos", "consultar")
def pagina_empleados():
    return render_template(
        "empleados.html",
        show_navbar=True,
        show_notifications=True,
        active_page="empleados",
    )
