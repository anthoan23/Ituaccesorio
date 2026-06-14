import mysql.connector
from app.models.database import conectar
from app.utils.notificaciones_bus import bus_notificaciones
from datetime import datetime


class Bitacora(conectar):
    def __init__(self, accion="", descripcion="", usuario_id="SYSTEM", modulo_nombre=None):
        super().__init__()
        self.accion = accion
        self.descripcion = descripcion
        self.usuario_id = usuario_id
        self.modulo_nombre = modulo_nombre

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
            self._cerrar_cursor_conexion(cursor, db)

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
            except Exception:
                pass

            return {"success": True}
        except mysql.connector.Error as error:
            return {"success": False, "warning": f"No se pudo registrar la bitácora: {error}"}
        finally:
            self._cerrar_cursor_conexion(cursor, db)

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
            
            # Enriquecer con datos del usuario
            for reg in registros:
                usuario_info = self._obtener_info_usuario(reg.get('usuario_id'))
                if usuario_info:
                    reg['usuario_nombre'] = usuario_info.get('nombre')
                    reg['usuario_foto'] = usuario_info.get('foto_perfil')
                else:
                    reg['usuario_nombre'] = reg.get('usuario_id')
                    reg['usuario_foto'] = None
                    
            return registros
        except mysql.connector.Error as e:
            print(f"Error al listar bitácora: {e}")
            return []
        finally:
            self._cerrar_cursor_conexion(cursor, db)

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
            ahora = datetime.now()
            
            for reg in registros:
                # Obtener info del usuario
                usuario_info = self._obtener_info_usuario(reg.get('usuario_id'))
                if usuario_info:
                    reg['usuario_nombre'] = usuario_info.get('nombre')
                    reg['usuario_foto'] = usuario_info.get('foto_perfil')
                else:
                    reg['usuario_nombre'] = reg.get('usuario_id')
                    reg['usuario_foto'] = None
                
                # Calcular tiempo relativo
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
            print(f"Error en listar_actividad_reciente: {e}")
            return []
        finally:
            self._cerrar_cursor_conexion(cursor, db)


def listar_actividad_reciente_dashboard(limite: int = 5):
    """Función helper para obtener actividades recientes del dashboard"""
    bitacora = Bitacora()
    return bitacora.listar_actividad_reciente(limite)