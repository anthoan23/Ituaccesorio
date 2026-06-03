from __future__ import annotations

from datetime import date

from app.models.database import conectar

class Especialidad(conectar):

    def listar_especialidades(self):
        db = self.conexion1()
        if not db:
            Mensaje = "Error al conectar a la base de datos."
            return Mensaje

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    ID_especialidad AS id,
                    Nombre_especialidad AS nombre,
                    Descripcion_especialidad AS descripcion
                FROM Especialidad
                ORDER BY ID_especialidad ASC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def agregar_especialidad(self, nueva_especialidad: str, descripcion_especialidad: str) -> str:

        if not nueva_especialidad or not descripcion_especialidad:
            mensaje = "El nombre y la descripción de la especialidad no pueden estar vacíos."
            return mensaje
        
        if len(nueva_especialidad) > 30:
            mensaje = "El nombre de la especialidad no puede exceder los 30 caracteres."
            return mensaje
        
        if len(descripcion_especialidad) > 255:
            mensaje = "La descripción de la especialidad no puede exceder los 255 caracteres."
            return mensaje
        
        if self.verificar_especialidad_nombre(nueva_especialidad):
            mensaje = f"La especialidad '{nueva_especialidad}' ya existe."
            return mensaje

        db = self.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje

        cursor = db.cursor()
        try:
            sql= 'CALL Crear_especialidad(%s, %s)'
            cursor.execute(sql, (nueva_especialidad, descripcion_especialidad))
            while cursor.nextset():
                pass
            db.commit()
            mensaje = f"Especialidad '{nueva_especialidad}' agregada exitosamente."
            return mensaje
        except Exception as e:
            db.rollback()
            mensaje = f"Error al agregar la especialidad: {str(e)}"
            return mensaje
        finally:
            cursor.close()
            db.close()

    def actualizar_especialidad(self, especialidad_id: int, nueva_especialidad: str, descripcion_especialidad: str) -> str:

        if not nueva_especialidad or not descripcion_especialidad:
            mensaje = "El nombre y la descripción de la especialidad no pueden estar vacíos."
            return mensaje
        
        if len(nueva_especialidad) > 30:
            mensaje = "El nombre de la especialidad no puede exceder los 30 caracteres."
            return mensaje
        
        if len(descripcion_especialidad) > 255:
            mensaje = "La descripción de la especialidad no puede exceder los 255 caracteres."
            return mensaje
    
        especialidad_id_existente = self.obtener_id_por_nombre(nueva_especialidad)
        if especialidad_id_existente != especialidad_id:
            return f"La especialidad '{nueva_especialidad}' ya existe."


        db = self.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje

        cursor = db.cursor()
        try:
            sql= 'UPDATE Especialidad SET Nombre_especialidad = %s, Descripcion_especialidad = %s WHERE ID_especialidad = %s'
            cursor.execute(sql, (nueva_especialidad, descripcion_especialidad, especialidad_id))
            while cursor.nextset():
                pass
            db.commit()
            mensaje = f"Especialidad con ID {especialidad_id} actualizada exitosamente."
            return mensaje
        except Exception as e:
            db.rollback()
            mensaje = f"Error al actualizar la especialidad: {str(e)}"
            return mensaje
        finally:
            cursor.close()
            db.close()

    def eliminar_especialidad(self, especialidad_id: int) -> str:

        if not especialidad_id:
            mensaje = "El identificador de la especialidad no puede estar vacío."
            return mensaje
        
        if not self.verificar_especialidad_id(especialidad_id):
            return f"La especialidad con ID {especialidad_id} no existe."

        db = self.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje

        cursor = db.cursor()
        try:
            sql= 'DELETE FROM Especialidad WHERE ID_especialidad = %s'
            cursor.execute(sql, (especialidad_id,))
            while cursor.nextset():
                pass
            db.commit()
            mensaje = f"Especialidad con ID {especialidad_id} eliminada exitosamente."
            return mensaje
        except Exception as e:
            db.rollback()
            if hasattr(e, 'errno') and e.errno == 1451:
                mensaje = f"No se puede eliminar la especialidad con ID {especialidad_id} porque está en uso por empleados."
                return mensaje
            mensaje = f"Error al eliminar la especialidad: {str(e)}"
            return mensaje
        finally:
            cursor.close()
            db.close()


    def verificar_especialidad_nombre(self, nombre_especialidad: str) -> bool:
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            sql = 'SELECT COUNT(*) FROM Especialidad WHERE Nombre_especialidad = %s'
            cursor.execute(sql, (nombre_especialidad,))
            result = cursor.fetchone()
            return result[0] > 0
        finally:
            cursor.close()
            db.close()

    def verificar_especialidad_id(self, especialidad_id: int) -> bool:
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            sql = 'SELECT COUNT(*) FROM Especialidad WHERE ID_especialidad = %s'
            cursor.execute(sql, (especialidad_id,))
            result = cursor.fetchone()
            return result[0] > 0
        finally:
            cursor.close()
            db.close()

    def obtener_id_por_nombre(self, nombre_especialidad: str) -> int | None:
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT ID_especialidad FROM Especialidad WHERE Nombre_especialidad = %s LIMIT 1",
                (nombre_especialidad,),
            )
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            cursor.close()
            db.close()