from flask import Blueprint, jsonify, render_template, request, g
from app.models.bitacora import Bitacora, registrar_en_bitacora
from app.utils.decorators import jwt_required


bitacora_blueprint = Blueprint("bitacora", __name__)


def _resolver_usuario_actual():
    usuario = getattr(g, "user", None)
    if not usuario:
        return "SYSTEM"

    if isinstance(usuario, dict):
        return str(usuario.get("user_id") or usuario.get("id") or usuario.get("username") or "SYSTEM")

    return str(
        getattr(usuario, "user_id", None)
        or getattr(usuario, "id", None)
        or getattr(usuario, "username", None)
        or "SYSTEM"
    )


@bitacora_blueprint.route("/bitacora", methods=["GET"])
@jwt_required
def pagina_bitacora():
    modelo = Bitacora()
    registros = modelo.listar_recientes(150)
    return render_template(
        "bitacora.html",
        show_navbar=True,
        show_notifications=True,
        active_page="bitacora",
        registros=registros,
    )


@bitacora_blueprint.route("/api/bitacora/registrar", methods=["POST"])
@jwt_required
def registrar_bitacora_api():
    payload = request.get_json(silent=True) or {}
    accion = str(payload.get("accion") or "").strip()
    descripcion = str(payload.get("descripcion") or "").strip()
    modulo_nombre = str(payload.get("modulo_nombre") or "").strip() or None

    if not accion or not descripcion:
        return jsonify({
            "success": False,
            "error": "Los campos 'accion' y 'descripcion' son obligatorios.",
        }), 400

    resultado = registrar_en_bitacora(
        accion,
        descripcion,
        usuario_id=_resolver_usuario_actual(),
        modulo_nombre=modulo_nombre,
    )
    estado = 200 if resultado.get("success") else 500
    return jsonify(resultado), estado
