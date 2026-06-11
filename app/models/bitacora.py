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

    def registrar(self, accion, descripcion, usuario_id="SYSTEM", modulo_nombre=None, usuario_nombre=None, usuario_foto=None):
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

            # Publicar notificación con información del usuario (sin guardar en BD)
            try:
                bus_notificaciones.publicar(
                    {
                        "tipo": "bitacora",
                        "titulo": "Nueva actividad registrada",
                        "accion": accion,
                        "descripcion": descripcion,
                        "modulo_nombre": modulo_nombre or "General",
                        "usuario_id": str(usuario_id),
                        "usuario_nombre": usuario_nombre or usuario_id,
                        "usuario_foto": usuario_foto,
                    },
                    autor_id=usuario_id,
                )
            except Exception:
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


def registrar_en_bitacora(accion, descripcion, usuario_id="SYSTEM", modulo_nombre=None, usuario_nombre=None, usuario_foto=None):
    return Bitacora().registrar(accion, descripcion, usuario_id=usuario_id, modulo_nombre=modulo_nombre, usuario_nombre=usuario_nombre, usuario_foto=usuario_foto)

def listar_actividad_reciente_dashboard(self, limite: int = 5):
    """Obtiene las últimas actividades para el dashboard"""
    db = self.conexion2()
    if not db:
        return []
    
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                b.id,
                b.usuario_id,
                b.accion,
                b.descripcion,
                b.fecha_hora,
                m.nombre as modulo_nombre
            FROM bitacora b
            LEFT JOIN modulo m ON b.modulo_id = m.id
            ORDER BY b.id DESC
            LIMIT %s
        """, (int(limite),))
        registros = cursor.fetchall() or []
        
        # Formatear tiempo relativo
        from datetime import datetime
        ahora = datetime.now()
        
        for reg in registros:
            if reg.get('fecha_hora'):
                fecha = reg['fecha_hora']
                if isinstance(fecha, datetime):
                    diff = ahora - fecha
                    if diff.days > 0:
                        if diff.days == 1:
                            reg['tiempo_relativo'] = 'hace 1 día'
                        else:
                            reg['tiempo_relativo'] = f'hace {diff.days} días'
                    elif diff.seconds >= 3600:
                        horas = diff.seconds // 3600
                        reg['tiempo_relativo'] = f'hace {horas} hora{"s" if horas > 1 else ""}'
                    elif diff.seconds >= 60:
                        minutos = diff.seconds // 60
                        reg['tiempo_relativo'] = f'hace {minutos} minuto{"s" if minutos > 1 else ""}'
                    else:
                        reg['tiempo_relativo'] = 'hace unos segundos'
                else:
                    reg['tiempo_relativo'] = 'recientemente'
            else:
                reg['tiempo_relativo'] = 'recientemente'
        
        return registros
    except Exception as e:
        print(f"Error en listar_actividad_reciente_dashboard: {e}")
        return []
    finally:
        cursor.close()
        db.close()