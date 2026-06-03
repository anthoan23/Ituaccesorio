from __future__ import annotations

from queue import Empty, Full, Queue
from threading import Lock
from datetime import datetime, timezone


class BusNotificaciones:
    """Bus de notificaciones en memoria basado en Queue.

    El bus vive dentro del proceso Python. Eso lo hace muy rapido para SSE,
    pero tambien significa que solo comparte mensajes entre hilos del mismo
    worker. En produccion debe ejecutarse con un solo worker y varios hilos
    si se quiere mantener este enfoque en memoria.
    """

    def __init__(self, maxsize: int = 200):
        self._maxsize = maxsize
        self._suscriptores: dict[str, set[Queue]] = {}
        self._lock = Lock()

    def _normalizar_usuario(self, usuario_id) -> str:
        return str(usuario_id if usuario_id is not None else "SYSTEM")

    def _crear_evento(self, mensaje: dict, autor_id=None) -> dict:
        evento = dict(mensaje or {})
        evento.setdefault("tipo", "bitacora")
        evento.setdefault("fecha_hora", datetime.now(timezone.utc).isoformat())
        if autor_id is not None:
            evento["autor_id"] = self._normalizar_usuario(autor_id)
        return evento

    def suscribir(self, usuario_id):
        """Crea una cola exclusiva para una conexion SSE activa."""
        clave_usuario = self._normalizar_usuario(usuario_id)
        cola = Queue(maxsize=self._maxsize)

        with self._lock:
            self._suscriptores.setdefault(clave_usuario, set()).add(cola)

        return cola

    def desuscribir(self, usuario_id, cola=None):
        """Elimina una conexion de la lista de suscripciones activas."""
        clave_usuario = self._normalizar_usuario(usuario_id)

        with self._lock:
            colas = self._suscriptores.get(clave_usuario)
            if not colas:
                return

            if cola is None:
                self._suscriptores.pop(clave_usuario, None)
                return

            colas.discard(cola)
            if not colas:
                self._suscriptores.pop(clave_usuario, None)

    def _enviar_a_cola(self, cola: Queue, evento: dict):
        try:
            cola.put_nowait(evento)
            return
        except Full:
            pass

        # Si la cola se llena, descartamos el evento mas antiguo para evitar
        # que un consumidor lento bloquee a los demas o consuma memoria de mas.
        try:
            cola.get_nowait()
        except Empty:
            pass

        try:
            cola.put_nowait(evento)
        except Full:
            pass

    def publicar(self, mensaje: dict, autor_id=None):
        """Envía un evento a todos los usuarios activos excepto al autor."""
        evento = self._crear_evento(mensaje, autor_id=autor_id)
        autor_clave = None if autor_id is None else self._normalizar_usuario(autor_id)

        with self._lock:
            suscriptores = {
                usuario: tuple(colas)
                for usuario, colas in self._suscriptores.items()
            }

        for usuario, colas in suscriptores.items():
            if autor_clave is not None and usuario == autor_clave:
                continue

            for cola in colas:
                self._enviar_a_cola(cola, evento)

        return evento


# Singleton del proceso. Con un solo worker de Gunicorn, todos los hilos comparten
# esta instancia y el SSE recibe los mismos mensajes en memoria.
bus_notificaciones = BusNotificaciones()
