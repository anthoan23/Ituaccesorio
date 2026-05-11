from flask import Blueprint, render_template
from app.utils.decorators import jwt_required

productos_blueprint = Blueprint("productos", __name__)


@productos_blueprint.route("/productos", methods=["GET"])
@jwt_required
def pagina_productos():
    return render_template(
        "productos.html",
        show_navbar=True,
        show_notifications=True,
        active_page="productos",
    )
