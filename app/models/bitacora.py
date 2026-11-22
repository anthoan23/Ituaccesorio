import logging
import mysql.connector
from app.models.database import conectar
from app.utils.notificaciones_bus import bus_notificaciones
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


class Bitacora(conectar):
    def __init__(self, accion="", descripcion="", usuario_id="SYSTEM", modulo_nombre=None):
        super().__init__()
        self.accion = accion
        self.descripcion = descripcion
        self.usuario_id = usuario_id
        self.modulo_nombre = modulo_nombre

    def obtener_modulo_id(self, modulo_nombre=None):
        """Obtiene el ID del módulo por su nombre"""
        nombre = modulo_nombre or self.modulo_nombre
        
        if not nombre:
            return 1

        db = self.conexion2()
        if not db:
            return 1

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id FROM modulo WHERE nombre = %s LIMIT 1", (nombre,))
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
            self.cerrar_conexion(cursor, db)

    def registrar(self, accion=None, descripcion=None, usuario_id=None, modulo_nombre=None):
        """
        Registra una acción en la bitácora usando los atributos de la instancia
        o los valores pasados como parámetros (los parámetros tienen prioridad)
        """
        # Usar parámetros si se proporcionan, sino usar atributos
        accion_final = accion if accion is not None else self.accion
        descripcion_final = descripcion if descripcion is not None else self.descripcion
        usuario_id_final = usuario_id if usuario_id is not None else self.usuario_id
        modulo_nombre_final = modulo_nombre if modulo_nombre is not None else self.modulo_nombre

        if not accion_final or not descripcion_final:
            return {
                "success": False,
                "warning": "Acción y descripción son obligatorias para registrar en bitácora.",
            }

        db = self.conexion2()
        if not db:
            return {
                "success": False,
                "warning": "No se pudo conectar con la base de seguridad para registrar la bitácora.",
            }

        cursor = db.cursor()
        try:
            modulo_id = self.obtener_modulo_id(modulo_nombre_final)
            sql = (
                "INSERT INTO bitacora (usuario_id, modulo_id, accion, descripcion) "
                "VALUES (%s, %s, %s, %s)"
            )
            cursor.execute(sql, (usuario_id_final, modulo_id, accion_final, descripcion_final))
            db.commit()

            # Publicar notificación (NO se guarda en BD, solo para UI en tiempo real)
            try:
                bus_notificaciones.publicar(
                    {
                        "tipo": "bitacora",
                        "titulo": "Nueva actividad registrada",
                        "accion": accion_final,
                        "descripcion": descripcion_final,
                        "modulo_nombre": modulo_nombre_final or "General",
                        "usuario_id": str(usuario_id_final),
                    },
                    autor_id=usuario_id_final,
                )
            except Exception as error:
                # La notificación en tiempo real no debe tumbar el registro de bitácora
                logger.debug("No se pudo publicar la notificación de bitácora: %s", error)

            return {"success": True}
        except mysql.connector.Error as error:
            return {"success": False, "warning": f"No se pudo registrar la bitácora: {error}"}
        finally:
            self.cerrar_conexion(cursor, db)

    def listar_recientes(self, limite=100):
        """Lista los registros recientes de bitácora"""
        db = self.conexion2()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT 
                    b.id, 
                    b.usuario_id, 
                    b.modulo_id, 
                    b.accion, 
                    b.descripcion, 
                    b.fecha_hora,
                    m.nombre as modulo_nombre
                FROM bitacora b
                LEFT JOIN modulo m ON b.modulo_id = m.id
                ORDER BY b.id DESC LIMIT %s""",
                (int(limite),),
            )
            registros = cursor.fetchall() or []
            
            # Enriquecer con datos del usuario en UNA consulta en lote
            ids = [r.get('usuario_id') for r in registros
                   if r.get('usuario_id') and r.get('usuario_id') != 'SYSTEM']
            usuarios = self._obtener_info_usuarios(list(set(ids)))
            for reg in registros:
                uid = reg.get('usuario_id')
                if uid == 'SYSTEM':
                    reg['usuario_nombre'] = 'Sistema'
                    reg['usuario_foto'] = None
                    continue
                usuario_info = usuarios.get(uid)
                if usuario_info:
                    reg['usuario_nombre'] = usuario_info.get('nombre')
                    reg['usuario_foto'] = usuario_info.get('foto_perfil')
                else:
                    reg['usuario_nombre'] = uid
                    reg['usuario_foto'] = None
    
            return registros
        except mysql.connector.Error as e:
            logger.error(f"Error al listar bitácora: {e}")
            return []
        finally:
            self.cerrar_conexion(cursor, db)

    def _obtener_info_usuario(self, usuario_id):
        """Obtiene nombre y foto de un usuario desde la BD principal"""
        if not usuario_id or usuario_id == "SYSTEM":
            return {"nombre": "Sistema", "foto_perfil": None}
            
        db = self.conexion1()
        if not db:
            return None
            
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT nombre, foto_perfil FROM usuario WHERE id = %s LIMIT 1",
                (usuario_id,)
            )
            return cursor.fetchone()
        except Exception:
            return None
        finally:
            cursor.close()
            db.close()

    def _obtener_info_usuarios(self, ids_usuarios):
        """Obtiene nombre y foto de VARIOS usuarios en UNA consulta.

        Reemplaza el N+1 de _obtener_info_usuario: listar 100 registros
        abría 100 conexiones nuevas a la BD principal.
        """
        if not ids_usuarios:
            return {}
        db = self.conexion1()
        if not db:
            return {}
        marcadores = ", ".join(["%s"] * len(ids_usuarios))
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                f"SELECT id, nombre, foto_perfil FROM usuario WHERE id IN ({marcadores})",  # nosec B608: marcadores '%s' literales
                tuple(ids_usuarios)
            )
            return {fila["id"]: fila for fila in (cursor.fetchall() or [])}
        except Exception:
            return {}
        finally:
            cursor.close()
            db.close()

    def listar_actividad_reciente(self, limite: int = 5):
        """Obtiene las últimas actividades para el dashboard con tiempo relativo"""
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
            
            # Enriquecer con datos del usuario y tiempo relativo
            ids = [r.get('usuario_id') for r in registros
                   if r.get('usuario_id') and r.get('usuario_id') != 'SYSTEM']
            usuarios = self._obtener_info_usuarios(list(set(ids)))
            
            # La BD escribe fecha_hora en -04:00; el contenedor Python va en
            # UTC: sin fijar la zona, un evento de hace segundos mostraba
            # "hace 4 horas".
            zona = timezone(timedelta(hours=-4))
            ahora = datetime.now(tz=zona)
            
            for reg in registros:
                uid = reg.get('usuario_id')
                if uid == 'SYSTEM':
                    reg['usuario_nombre'] = 'Sistema'
                    reg['usuario_foto'] = None
                else:
                    usuario_info = usuarios.get(uid)
                    if usuario_info:
                        reg['usuario_nombre'] = usuario_info.get('nombre')
                        reg['usuario_foto'] = usuario_info.get('foto_perfil')
                    else:
                        reg['usuario_nombre'] = uid
                        reg['usuario_foto'] = None
                
                # Calcular tiempo relativo
                if reg.get('fecha_hora'):
                    fecha = reg['fecha_hora']
                    if isinstance(fecha, datetime):
                        if fecha.tzinfo is None:
                            fecha = fecha.replace(tzinfo=zona)
                        diff = ahora - fecha
                        if diff.total_seconds() < 0:
                            reg['tiempo_relativo'] = 'ahora mismo'
                        elif diff.days > 0:
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
            logger.error(f"Error en listar_actividad_reciente: {e}")
            return []
        finally:
            self.cerrar_conexion(cursor, db)


def listar_actividad_reciente_dashboard(limite: int = 5):
    """Función helper para obtener actividades recientes del dashboard"""
    bitacora = Bitacora()
    return bitacora.listar_actividad_reciente(limite)