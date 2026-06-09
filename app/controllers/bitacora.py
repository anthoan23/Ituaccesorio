from flask import Blueprint, jsonify, render_template, request, g
from app.models.bitacora import Bitacora, registrar_en_bitacora
from app.utils.decorators import jwt_required, solo_roles

bitacora_blueprint = Blueprint("bitacora", __name__)


@bitacora_blueprint.route("/bitacora", methods=["GET"])
@jwt_required
@solo_roles(["admin"])
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
@solo_roles(["admin"])
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
        usuario_id=g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM"),
        modulo_nombre=modulo_nombre,
    )

    estado = 200 if resultado.get("success") else 500
    return jsonify(resultado), estado


@bitacora_blueprint.route("/api/bitacora/list", methods=["GET"])
@jwt_required
@solo_roles(["admin"])
def api_listar_bitacora():
    modelo = Bitacora()
    registros = modelo.listar_recientes(1000)
    return jsonify(registros), 200


@bitacora_blueprint.route("/api/bitacora/ultimas-notificaciones", methods=["GET"])
@jwt_required
@solo_roles(["admin"])
def api_ultimas_notificaciones():
    modelo = Bitacora()
    registros = modelo.listar_recientes(3) or []
    
    notificaciones = []
    for reg in registros:
        notificacion = {
            "tipo": "bitacora",
            "titulo": "Actividad registrada",
            "accion": reg.get("accion", ""),
            "descripcion": reg.get("descripcion", ""),
            "modulo_nombre": "General",
            "usuario_id": reg.get("usuario_id", "SYSTEM"),
            "usuario_nombre": reg.get("usuario_id", "Sistema"),
            "usuario_foto": None,
            "fecha_hora": reg.get("fecha_hora", "")
        }
        notificaciones.append(notificacion)
    
    return jsonify({"success": True, "notificaciones": notificaciones}), 200