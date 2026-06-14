from __future__ import annotations

from datetime import date

from app.models.database import conectar
from app.models.bitacora import Bitacora


class Especialidad():

    def __init__(self, id_especialidad: str = "", nombre_especialidad: str = "", 
                 descripcion_especialidad: str = "", usuario_id: str = None):
        self.id_especialidad = id_especialidad
        self.nombre_especialidad = nombre_especialidad
        self.descripcion_especialidad = descripcion_especialidad
        self.usuario_id = usuario_id

        self.__conexion_bd = conectar()

    def listar_especialidades(self):
        db = self.__conexion_bd.conexion1()
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

    def agregar_especialidad(self) -> str:
        nombre = self.nombre_especialidad.strip()
        descripcion = self.descripcion_especialidad.strip()

        if not nombre or not descripcion:
            return "El nombre y la descripción de la especialidad no pueden estar vacíos."
        
        if len(nombre) > 30:
            return "El nombre de la especialidad no puede exceder los 30 caracteres."
        
        if len(descripcion) > 255:
            return "La descripción de la especialidad no puede exceder los 255 caracteres."
        
        if self.verificar_especialidad():
            return f"La especialidad '{nombre}' ya existe."

        db = self.__conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            sql = 'CALL Crear_especialidad(%s, %s)'
            cursor.execute(sql, (nombre, descripcion))
            while cursor.nextset():
                pass
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Crear especialidad",
                    descripcion=f"Se creó la especialidad: {nombre}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Especialidades"
                )
                bitacora.registrar()
            
            return "Especialidad agregada exitosamente."
        except Exception as e:
            print(f"Error al agregar especialidad: {e}")
            db.rollback()
            return "Error al agregar especialidad."
        finally:
            cursor.close()
            db.close()

    def eliminar_especialidad(self) -> str:
        especialidad_id = self.id_especialidad.strip()

        if not especialidad_id:
            return "El identificador de la especialidad no puede estar vacío."
        
        if not self.verificar_especialidad_por_id():
            return f"La especialidad con identificador {especialidad_id} no existe."

        db = self.__conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            sql = "DELETE FROM Especialidad WHERE ID_especialidad = %s"
            cursor.execute(sql, (especialidad_id,))
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Eliminar especialidad",
                    descripcion=f"Se eliminó la especialidad ID: {especialidad_id}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Especialidades"
                )
                bitacora.registrar()
            
            return "Especialidad eliminada exitosamente."
        except Exception as e:
            print(f"Error al eliminar especialidad: {e}")
            db.rollback()
            if hasattr(e, 'errno') and e.errno == 1451:
                return f"No se puede eliminar la especialidad con ID {especialidad_id} porque está en uso por empleados."
            return "Error al eliminar especialidad. Verifica que no esté en uso por empleados."
        finally:
            cursor.close()
            db.close()

    def actualizar_especialidad(self) -> str:
        # Usar los atributos de la instancia
        especialidad_id = self.id_especialidad.strip()
        nuevo_nombre = self.nombre_especialidad.strip()
        nueva_descripcion = self.descripcion_especialidad.strip()

        # Validaciones
        if not especialidad_id:
            return "El identificador de la especialidad es obligatorio."

        if not nuevo_nombre or not nueva_descripcion:
            return "El nombre y la descripción de la especialidad no pueden estar vacíos."

        if len(nuevo_nombre) > 30:
            return "El nombre de la especialidad no puede exceder los 30 caracteres."

        if len(nueva_descripcion) > 255:
            return "La descripción de la especialidad no puede exceder los 255 caracteres."

        # Verificar si la especialidad existe
        if not self.verificar_especialidad_por_id():
            return f"La especialidad con identificador {especialidad_id} no existe."

        # Verificar si el nuevo nombre ya existe (excepto para la misma especialidad)
        especialidad_id_existente = self.obtener_id_por_nombre()
        if especialidad_id_existente and especialidad_id_existente != especialidad_id:
            return f"La especialidad '{nuevo_nombre}' ya existe."

        db = self.__conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            sql = """
                UPDATE Especialidad
                SET Nombre_especialidad = %s,
                    Descripcion_especialidad = %s
                WHERE ID_especialidad = %s
            """
            cursor.execute(sql, (nuevo_nombre, nueva_descripcion, especialidad_id))
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Actualizar especialidad",
                    descripcion=f"Se actualizó la especialidad ID: {especialidad_id} - Nuevo nombre: {nuevo_nombre}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Especialidades"
                )
                bitacora.registrar()
            
            return "Especialidad actualizada exitosamente."
        except Exception as e:
            print(f"Error al actualizar especialidad: {e}")
            db.rollback()
            return "Error al actualizar especialidad."
        finally:
            cursor.close()
            db.close()
    
    def verificar_especialidad(self) -> bool:
        # Usar el atributo nombre_especialidad
        especialidad = self.nombre_especialidad.strip()
        
        db = self.__conexion_bd.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM Especialidad WHERE Nombre_especialidad = %s LIMIT 1",
                (especialidad,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    def verificar_especialidad_por_id(self) -> bool:
        especialidad_id = self.id_especialidad.strip()
        
        db = self.__conexion_bd.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM Especialidad WHERE ID_especialidad = %s LIMIT 1",
                (especialidad_id,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    def obtener_especialidad_por_id(self, especialidad_id: str = None):
        id_buscar = especialidad_id or self.id_especialidad
        if not id_buscar:
            return None

        db = self.__conexion_bd.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT ID_especialidad AS id, Nombre_especialidad AS nombre, Descripcion_especialidad AS descripcion "
                "FROM Especialidad WHERE ID_especialidad = %s LIMIT 1",
                (id_buscar,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()

    def obtener_id_por_nombre(self) -> str | None:
        # Usar el atributo nombre_especialidad
        especialidad = self.nombre_especialidad.strip()
        
        db = self.__conexion_bd.conexion1()
        if not db:
            return None

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT ID_especialidad FROM Especialidad WHERE Nombre_especialidad = %s LIMIT 1",
                (especialidad,),
            )
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            cursor.close()
            db.close()