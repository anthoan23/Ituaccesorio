import json
from queue import Empty

from flask import Blueprint, Response, g, stream_with_context

from app.utils.decorators import jwt_required
from app.utils.notificaciones_bus import bus_notificaciones


notificaciones_blueprint = Blueprint("notificaciones", __name__)


def _usuario_autenticado_id():
    usuario = getattr(g, "user", None)
    if not usuario:
        return None

    if isinstance(usuario, dict):
        return usuario.get("usuario_id") or usuario.get("user_id") or usuario.get("id")

    return getattr(usuario, "usuario_id", None) or getattr(usuario, "user_id", None) or getattr(usuario, "id", None)


def _usuario_autenticado_info():
    """Obtiene la información completa del usuario autenticado"""
    usuario = getattr(g, "user", None)
    if not usuario:
        return {"id": "SYSTEM", "nombre": "SISTEMA", "foto": None}
    
    if isinstance(usuario, dict):
        user_id = usuario.get("usuario_id") or usuario.get("id") or "SYSTEM"
        user_name = usuario.get("usuario_nombre") or usuario.get("nombre") or usuario.get("username") or "USUARIO"
        user_foto = usuario.get("foto_perfil") or None
        return {"id": user_id, "nombre": user_name, "foto": user_foto}
    
    user_id = getattr(usuario, "usuario_id", None) or getattr(usuario, "id", None) or "SYSTEM"
    user_name = getattr(usuario, "usuario_nombre", None) or getattr(usuario, "nombre", None) or getattr(usuario, "username", None) or "USUARIO"
    user_foto = getattr(usuario, "foto_perfil", None) or None
    return {"id": user_id, "nombre": user_name, "foto": user_foto}


@notificaciones_blueprint.route("/notificaciones/stream/<string:usuario_id>")
@jwt_required
def stream_notificaciones(usuario_id):
    usuario_autenticado = _usuario_autenticado_id()
    if str(usuario_autenticado) != str(usuario_id):
        return {"success": False, "error": "No autorizado para este stream."}, 403

    cola = bus_notificaciones.suscribir(usuario_id)

    def generar_eventos():
        try:
            yield ": conectado\n\n"

            while True:
                try:
                    evento = cola.get(timeout=15)
                except Empty:
                    yield ": ping\n\n"
                    continue

                payload = json.dumps(evento, ensure_ascii=False)
                yield "event: bitacora\n"
                yield f"data: {payload}\n\n"
        finally:
            bus_notificaciones.desuscribir(usuario_id, cola)

    response = Response(stream_with_context(generar_eventos()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response