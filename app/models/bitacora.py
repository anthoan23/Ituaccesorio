import mysql.connector
from app.models.database import conectar
from app.utils.notificaciones_bus import bus_notificaciones


class Bitacora(conectar):
    def _cerrar_cursor_conexion(self, cursor, db):
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            if db:
                db.close()
        except Exception:
            pass

    def obtener_modulo_id(self, modulo_nombre):
        if not modulo_nombre:
            return 1

        db = self.conexion2()
        if not db:
            return 1

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id FROM modulo WHERE nombre = %s LIMIT 1", (modulo_nombre,))
            fila = cursor.fetchone()
            if fila and fila.get("id") is not None:
                return int(fila["id"])

            cursor.execute("SELECT id FROM modulo ORDER BY id ASC LIMIT 1")
            fila = cursor.fetchone()
            if fila and fila.get("id") is not None:
                return int(fila["id"])
            return 1
        except mysql.connector.Error:
            return 1
        finally:
            self._cerrar_cursor_conexion(cursor, db)

    def registrar(self, accion, descripcion, usuario_id="SYSTEM", modulo_nombre=None):
        db = self.conexion2()
        if not db:
            return {
                "success": False,
                "warning": "No se pudo conectar con la base de seguridad para registrar la bitácora.",
            }

        cursor = db.cursor()
        try:
            modulo_id = self.obtener_modulo_id(modulo_nombre)
            sql = (
                "INSERT INTO bitacora (usuario_id, modulo_id, accion, descripcion) "
                "VALUES (%s, %s, %s, %s)"
            )
            cursor.execute(sql, (usuario_id, modulo_id, accion, descripcion))
            db.commit()

            # Publicamos despues del commit para que la notificacion solo salga
            # cuando la bitacora quedo realmente persistida.
            try:
                bus_notificaciones.publicar(
                    {
                        "tipo": "bitacora",
                        "titulo": "Nueva actividad registrada",
                        "accion": accion,
                        "descripcion": descripcion,
                        "modulo_nombre": modulo_nombre or "General",
                        "usuario_id": str(usuario_id),
                    },
                    autor_id=usuario_id,
                )
            except Exception:
                # La notificacion es un extra en tiempo real; si falla, no debe
                # impedir que la bitacora ya persistida llegue a la base.
                pass

            return {"success": True}
        except mysql.connector.Error as error:
            return {"success": False, "warning": f"No se pudo registrar la bitácora: {error}"}
        finally:
            self._cerrar_cursor_conexion(cursor, db)

    def listar_recientes(self, limite=100):
        db = self.conexion2()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, usuario_id, modulo_id, accion, descripcion, fecha_hora "
                "FROM bitacora ORDER BY id DESC LIMIT %s",
                (int(limite),),
            )
            return cursor.fetchall() or []
        except mysql.connector.Error:
            return []
        finally:
            self._cerrar_cursor_conexion(cursor, db)


def registrar_en_bitacora(accion, descripcion, usuario_id="SYSTEM", modulo_nombre=None):
    return Bitacora().registrar(accion, descripcion, usuario_id=usuario_id, modulo_nombre=modulo_nombre)
