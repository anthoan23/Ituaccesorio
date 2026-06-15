import json
from queue import Empty

from flask import Blueprint, Response, g, stream_with_context

from app.utils.decorators import jwt_required
from app.utils.notificaciones_bus import bus_notificaciones
from app.utils.helpers import obtener_usuario_autenticado_id


notificaciones_blueprint = Blueprint("notificaciones", __name__)


@notificaciones_blueprint.route("/notificaciones/stream/<string:usuario_id>")
@jwt_required
def stream_notificaciones(usuario_id):
    usuario_autenticado = obtener_usuario_autenticado_id()
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