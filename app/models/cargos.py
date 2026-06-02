from __future__ import annotations

from datetime import date

from app.models.database import conectar

class Cargo(conectar):

    def listar_cargos(self):
        db = self.conexion1()
        if not db:
            Mensaje = "Error al conectar a la base de datos."
            return Mensaje

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    ID_cargo AS id,
                    Nombre_cargo AS nombre,
                    Descripcion_cargo AS descripcion
                FROM Cargo
                ORDER BY ID_cargo ASC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()


    def agregar_cargo(self, nuevo_cargo: str, descripcion_cargo: str) -> str:

        if not nuevo_cargo or not descripcion_cargo:
            mensaje = "El nombre y la descripción del cargo no pueden estar vacíos."
            return mensaje
        
        if len(nuevo_cargo) > 30:
            mensaje = "El nombre del cargo no puede exceder los 30 caracteres."
            return mensaje
        
        if len(descripcion_cargo) > 255:
            mensaje = "La descripción del cargo no puede exceder los 255 caracteres."
            return mensaje
        
        if self.verificar_cargo(nuevo_cargo):
            mensaje = f"El cargo '{nuevo_cargo}' ya existe."
            return mensaje

        db = self.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje

        cursor = db.cursor()
        try:
            sql= 'CALL Crear_cargo(%s, %s)'
            cursor.execute(sql, (nuevo_cargo, descripcion_cargo))
            while cursor.nextset():
                pass
            db.commit()
            mensaje = f"Cargo agregado exitosamente. ID: {cursor.lastrowid}."
            return mensaje
        except Exception as e:
            print(f"Error al agregar cargo: {e}")
            db.rollback()
            mensaje = "Error al agregar cargo."
            return mensaje
        finally:
            cursor.close()
            db.close()

    def eliminar_cargo(self, cargo_id: str) -> str:

        if not cargo_id:
            mensaje = "El identificador del cargo no puede estar vacío."
            return mensaje
        
        if len(cargo_id) > 10:
            mensaje = "El identificador del cargo no puede exceder los 10 caracteres."
            return mensaje
      
        if not self.verificar_cargo_por_id(cargo_id):
            return f"El cargo con identificador {cargo_id} no existe."

        db = self.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje

        cursor = db.cursor()
        try:
            sql = "DELETE FROM Cargo WHERE ID_cargo = %s"
            cursor.execute(sql, (cargo_id,))
            db.commit()
            mensaje = "Cargo eliminado exitosamente."
            return mensaje
        except Exception as e:
            db.rollback()
            print(f"Error al eliminar cargo: {e}")
            if hasattr(e, 'errno') and e.errno == 1451:
                mensaje = f"No se puede eliminar el cargo con ID {cargo_id} porque está en uso por empleados."
                return mensaje
            mensaje = "Error al eliminar cargo."
            return mensaje
        finally:
            cursor.close()
            db.close()

    def actualizar_cargo(self, cargo_id: str, nuevo_cargo: str, descripcion_cargo: str) -> str:
        if not cargo_id:
            return "El identificador del cargo es obligatorio."

        if len(cargo_id) > 10:
            return "El identificador del cargo no puede exceder los 10 caracteres."

        if not nuevo_cargo or not descripcion_cargo:
            return "El nombre y la descripción del cargo no pueden estar vacíos."

        if len(nuevo_cargo) > 30:
            return "El nombre del cargo no puede exceder los 30 caracteres."

        if len(descripcion_cargo) > 255:
            return "La descripción del cargo no puede exceder los 255 caracteres."

        if not self.verificar_cargo_por_id(cargo_id):
            return f"El cargo con identificador {cargo_id} no existe."

        cargo_id_existente = self.obtener_id_por_nombre(nuevo_cargo)
        if cargo_id_existente and cargo_id_existente != cargo_id:
            return f"El cargo '{nuevo_cargo}' ya existe."

        db = self.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            sql = """
                UPDATE Cargo
                SET Nombre_cargo = %s,
                    Descripcion_cargo = %s
                WHERE ID_cargo = %s
            """
            cursor.execute(sql, (nuevo_cargo, descripcion_cargo, cargo_id))
            db.commit()
            return "Cargo actualizado exitosamente."
        except Exception as e:
            print(f"Error al actualizar cargo: {e}")
            db.rollback()
            return "Error al actualizar cargo."
        finally:
            cursor.close()
            db.close()
    
    def verificar_cargo(self, cargo: str) -> bool:
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM Cargo WHERE Nombre_cargo = %s LIMIT 1",
                (cargo,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    def verificar_cargo_por_id(self, cargo_id: str) -> bool:
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM Cargo WHERE ID_cargo = %s LIMIT 1",
                (cargo_id,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    def obtener_id_por_nombre(self, cargo: str) -> str | None:
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT ID_cargo FROM Cargo WHERE Nombre_cargo = %s LIMIT 1",
                (cargo,),
            )
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            cursor.close()
            db.close()