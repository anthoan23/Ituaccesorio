from __future__ import annotations

from app.models.database import conectar
from app.models.bitacora import Bitacora


class Cargo:

    def __init__(self, id_cargo: str = "", nombre_cargo: str = "", descripcion_cargo: str = "", usuario_id: str = None):
        self.id_cargo = id_cargo
        self.nombre_cargo = nombre_cargo
        self.descripcion_cargo = descripcion_cargo
        self.usuario_id = usuario_id 

        self.__conexion_bd = conectar()

    def listar_cargos(self):
        db = self.__conexion_bd.conexion1()
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

    def agregar_cargo(self) -> str:
        # Usar los atributos de la instancia
        nombre = self.nombre_cargo.strip()
        descripcion = self.descripcion_cargo.strip()


        if self.obtener_id_por_nombre():
            mensaje = f"El cargo '{nombre}' ya existe."
            return mensaje

        db = self.__conexion_bd.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje

        cursor = db.cursor()
        try:
            sql = 'CALL Crear_cargo(%s, %s)'
            cursor.execute(sql, (nombre, descripcion))
            while cursor.nextset():
                pass
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Crear cargo",
                    descripcion=f"Se creó el cargo: {nombre}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Cargos"
                )
                bitacora.registrar()
            
            return "Cargo agregado exitosamente."
        except Exception as e:
            print(f"Error al agregar cargo: {e}")
            db.rollback()
            mensaje = "Error al agregar cargo."
            return mensaje
        finally:
            cursor.close()
            db.close()

    def eliminar_cargo(self) -> str:
        # Usar el atributo id_cargo
        cargo_id = self.id_cargo.strip()
        
        if not self.verificar_cargo_por_id():
            return f"El cargo con identificador {cargo_id} no existe."

        db = self.__conexion_bd.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje

        cursor = db.cursor()
        try:
            sql = "DELETE FROM Cargo WHERE ID_cargo = %s"
            cursor.execute(sql, (cargo_id,))
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Eliminar cargo",
                    descripcion=f"Se eliminó el cargo ID: {cargo_id}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Cargos"
                )
                bitacora.registrar()
            
            return "Cargo eliminado exitosamente."
        except Exception as e:
            print(f"Error al eliminar cargo: {e}")
            db.rollback()
            mensaje = "Error al eliminar cargo. Verifica que no esté en uso por empleados."
            return mensaje
        finally:
            cursor.close()
            db.close()

    def actualizar_cargo(self) -> str:
        # Usar los atributos de la instancia
        cargo_id = self.id_cargo.strip()
        nuevo_nombre = self.nombre_cargo.strip()
        nueva_descripcion = self.descripcion_cargo.strip()

        # Verificar si el cargo existe
        if not self.verificar_cargo_por_id():
            return f"El cargo con identificador {cargo_id} no existe."

        # Verificar si el nuevo nombre ya existe (excepto para el mismo cargo)
        cargo_id_existente = self.obtener_id_por_nombre()
        if cargo_id_existente and cargo_id_existente != cargo_id:
            return f"El cargo '{nuevo_nombre}' ya existe."

        db = self.__conexion_bd.conexion1()
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
            cursor.execute(sql, (nuevo_nombre, nueva_descripcion, cargo_id))
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Actualizar cargo",
                    descripcion=f"Se actualizó el cargo ID: {cargo_id} - Nuevo nombre: {nuevo_nombre}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Cargos"
                )
                bitacora.registrar()
            
            return "Cargo actualizado exitosamente."
        except Exception as e:
            print(f"Error al actualizar cargo: {e}")
            db.rollback()
            return "Error al actualizar cargo."
        finally:
            cursor.close()
            db.close()

    def verificar_cargo_por_id(self) -> bool:
        # Usar el atributo id_cargo
        cargo_id = self.id_cargo.strip()
        
        db = self.__conexion_bd.conexion1()
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

    def obtener_id_por_nombre(self) -> str | None:
        # Usar el atributo nombre_cargo
        cargo = self.nombre_cargo.strip()
        
        db = self.__conexion_bd.conexion1()
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