# app/models/backup.py
from __future__ import annotations
import os
import datetime
import pymysql
from app.models.database import conectar
from app.models.bitacora import Bitacora

class Backup:
    def __init__(self, id_backup: int = None, id_usuario: str = None, estado: str = None,
                 fecha: datetime.datetime = None, direccion_bd: str = None, nombre: str = None):
        self.id_backup = id_backup
        self.id_usuario = id_usuario
        self.estado = estado
        self.fecha = fecha
        self.direccion_bd = direccion_bd
        self.nombre = nombre
        self.__conexion_bd = conectar()

    def listar_backups(self) -> list:
        """Lista todos los respaldos registrados"""
        db = self.__conexion_bd.conexion2()  # Base de datos de seguridad
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    b.id_backup,
                    b.id_usuario,
                    u.nombre AS usuario_nombre,
                    b.estado,
                    b.fecha,
                    b.direccion_bd,
                    b.nombre
                FROM backup b
                LEFT JOIN usuario u ON b.id_usuario = u.id
                ORDER BY b.fecha DESC
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def registrar_backup(self, direccion_bd: str, nombre: str) -> str:
        """Registra un nuevo respaldo en la base de datos"""
        if not self.id_usuario:
            return "ID de usuario no proporcionado"

        db = self.__conexion_bd.conexion2()  # Base de datos de seguridad
        if not db:
            return "Error al conectar a la base de datos de seguridad"

        cursor = db.cursor()
        try:
            sql = """
                INSERT INTO backup (id_usuario, estado, direccion_bd, nombre)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (self.id_usuario, 'completado', direccion_bd, nombre))
            db.commit()
            
            # Registrar en bitácora
            bitacora = Bitacora(
                accion="Crear backup",
                descripcion=f"Se creó backup: {nombre} en {direccion_bd}",
                usuario_id=self.id_usuario,
                modulo_nombre="Backup"
            )
            bitacora.registrar()
            
            return "Backup registrado exitosamente"
        except Exception as e:
            print(f"Error al registrar backup: {e}")
            db.rollback()
            return f"Error al registrar backup: {str(e)}"
        finally:
            cursor.close()
            db.close()

    def actualizar_estado(self, id_backup: int, estado: str) -> str:
        """Actualiza el estado de un backup"""
        db = self.__conexion_bd.conexion2()
        if not db:
            return "Error al conectar a la base de datos"

        cursor = db.cursor()
        try:
            sql = "UPDATE backup SET estado = %s WHERE id_backup = %s"
            cursor.execute(sql, (estado, id_backup))
            db.commit()
            return "Estado actualizado exitosamente"
        except Exception as e:
            print(f"Error al actualizar estado: {e}")
            db.rollback()
            return f"Error al actualizar estado: {str(e)}"
        finally:
            cursor.close()
            db.close()

    def eliminar_backup(self, id_backup: int) -> str:
        """Elimina un respaldo (tanto el registro como el archivo)"""
        db = self.__conexion_bd.conexion2()
        if not db:
            return "Error al conectar a la base de datos"

        cursor = db.cursor()
        try:
            # Primero obtener la ruta del archivo
            cursor.execute("SELECT direccion_bd FROM backup WHERE id_backup = %s", (id_backup,))
            row = cursor.fetchone()
            
            if row:
                file_path = row[0]
                # Eliminar el archivo físico si existe
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error al eliminar archivo: {e}")
            
            # Eliminar el registro
            sql = "DELETE FROM backup WHERE id_backup = %s"
            cursor.execute(sql, (id_backup,))
            db.commit()
            
            if self.id_usuario:
                bitacora = Bitacora(
                    accion="Eliminar backup",
                    descripcion=f"Se eliminó el backup ID: {id_backup}",
                    usuario_id=self.id_usuario,
                    modulo_nombre="Backup"
                )
                bitacora.registrar()
            
            return "Backup eliminado exitosamente"
        except Exception as e:
            print(f"Error al eliminar backup: {e}")
            db.rollback()
            return f"Error al eliminar backup: {str(e)}"
        finally:
            cursor.close()
            db.close()

    def obtener_info_backup(self, id_backup: int) -> dict:
        """Obtiene la información de un backup específico"""
        db = self.__conexion_bd.conexion2()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    id_backup,
                    id_usuario,
                    estado,
                    fecha,
                    direccion_bd,
                    nombre
                FROM backup 
                WHERE id_backup = %s
            """, (id_backup,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()

    def restaurar_backup(self, id_backup: int, db_config: dict) -> dict:
        """
        Restaura un backup en la base de datos correspondiente
        
        Args:
            id_backup: ID del backup a restaurar
            db_config: Configuración de la base de datos destino
            
        Returns:
            dict: {success: bool, message: str}
        """
        # Obtener información del backup
        backup_info = self.obtener_info_backup(id_backup)
        if not backup_info:
            return {"success": False, "message": "No se encontró el backup"}

        ruta_archivo = backup_info.get('direccion_bd')
        if not ruta_archivo or not os.path.exists(ruta_archivo):
            return {"success": False, "message": f"El archivo de backup no existe: {ruta_archivo}"}

        try:
            # Conectar a la base de datos destino
            connection = pymysql.connect(
                host=db_config.get('host'),
                user=db_config.get('user'),
                password=db_config.get('password'),
                database=db_config.get('database'),
                port=db_config.get('port', 3306),
                charset='utf8mb4',
                connect_timeout=60
            )
            
            cursor = connection.cursor()
            
            # Leer el archivo SQL
            with open(ruta_archivo, 'r', encoding='utf-8') as file:
                sql_content = file.read()
            
            # Dividir el SQL en statements individuales
            # Esto maneja procedimientos, triggers, etc.
            statements = self._split_sql_statements(sql_content)
            
            # Ejecutar cada statement
            total_statements = len(statements)
            executed = 0
            errors = []
            
            for i, statement in enumerate(statements):
                if not statement or statement.strip() == '':
                    continue
                    
                try:
                    # Ejecutar el statement
                    cursor.execute(statement)
                    executed += 1
                    
                    # Commit cada cierto número de statements para no sobrecargar
                    if executed % 100 == 0:
                        connection.commit()
                        
                except Exception as e:
                    error_msg = f"Error en statement {i+1}: {str(e)[:100]}..."
                    errors.append(error_msg)
                    # Si hay un error crítico, hacer rollback y detener
                    if "syntax error" in str(e).lower() or "access denied" in str(e).lower():
                        connection.rollback()
                        connection.close()
                        return {
                            "success": False, 
                            "message": f"Error crítico al restaurar: {error_msg}"
                        }
            
            # Commit final
            connection.commit()
            connection.close()
            
            # Registrar en bitácora
            bitacora = Bitacora(
                accion="Restaurar backup",
                descripcion=f"Se restauró el backup ID: {id_backup} - Archivo: {backup_info.get('nombre')}",
                usuario_id=self.id_usuario,
                modulo_nombre="Backup"
            )
            bitacora.registrar()
            
            return {
                "success": True,
                "message": f"Backup restaurado exitosamente. {executed} statements ejecutados.",
                "executed": executed,
                "errors": errors if errors else None
            }
            
        except pymysql.Error as e:
            return {"success": False, "message": f"Error de base de datos: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"Error al restaurar backup: {str(e)}"}

    def _split_sql_statements(self, sql_content: str) -> list:
        """
        Divide un archivo SQL en statements individuales,
        respetando DELIMITER para procedimientos y triggers
        """
        statements = []
        current_statement = []
        in_procedure = False
        in_trigger = False
        in_function = False
        delimiter = ';'
        
        lines = sql_content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Detectar cambio de DELIMITER
            if line.upper().startswith('DELIMITER'):
                parts = line.split()
                if len(parts) >= 2:
                    delimiter = parts[1]
                continue
            
            # Detectar inicio de procedimiento, función o trigger
            if line.upper().startswith('CREATE PROCEDURE'):
                in_procedure = True
            elif line.upper().startswith('CREATE FUNCTION'):
                in_function = True
            elif line.upper().startswith('CREATE TRIGGER'):
                in_trigger = True
            
            # Agregar línea al statement actual
            current_statement.append(line)
            
            # Verificar si el statement ha terminado
            if line.endswith(delimiter) and not (in_procedure or in_function or in_trigger):
                # Si es un statement normal y termina con el delimitador
                full_statement = '\n'.join(current_statement)
                # Remover el delimitador final
                if full_statement.endswith(delimiter):
                    full_statement = full_statement[:-len(delimiter)]
                if full_statement.strip():
                    statements.append(full_statement)
                current_statement = []
            elif (in_procedure or in_function or in_trigger) and line.endswith(delimiter):
                # Para procedimientos, funciones y triggers, buscar END seguido del delimiter
                # El delimiter puede ser $$ o ;
                if line.upper().strip().startswith('END') or line.upper().strip().startswith('END;'):
                    full_statement = '\n'.join(current_statement)
                    # Remover el delimitador final
                    if full_statement.endswith(delimiter):
                        full_statement = full_statement[:-len(delimiter)]
                    if full_statement.strip():
                        statements.append(full_statement)
                    current_statement = []
                    in_procedure = False
                    in_function = False
                    in_trigger = False
        
        # Agregar cualquier statement pendiente
        if current_statement:
            full_statement = '\n'.join(current_statement)
            if full_statement.strip():
                statements.append(full_statement)
        
        return statements
    
# app/models/backup.py - Agregar este método

def obtener_info_backup(self, id_backup: int) -> dict:
    """Obtiene la información de un backup específico"""
    db = self.__conexion_bd.conexion2()
    if not db:
        return None

    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                id_backup,
                id_usuario,
                estado,
                fecha,
                direccion_bd,
                nombre
            FROM backup 
            WHERE id_backup = %s
        """, (id_backup,))
        return cursor.fetchone()
    finally:
        cursor.close()
        db.close()