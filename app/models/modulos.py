from __future__ import annotations

from app.models.database import conectar


class Modulo:
    def __init__(self, id: str = "", nombre: str = "", descripcion: str = ""):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.__conexion_bd = conectar()

    def listar_modulos(self):
        db = self.__conexion_bd.conexion2()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, nombre, descripcion
                FROM modulo
                ORDER BY nombre
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def verificar_modulo_por_id(self) -> bool:
        if not self.id:
            return False

        db = self.__conexion_bd.conexion2()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM modulo WHERE id = %s LIMIT 1",
                (self.id,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    def verificar_modulo_por_nombre(self) -> bool:
        if not self.nombre:
            return False

        db = self.__conexion_bd.conexion2()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM modulo WHERE nombre = %s LIMIT 1",
                (self.nombre,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    def agregar_modulo(self) -> str:
        nombre = self.nombre.strip()
        descripcion = self.descripcion.strip() if self.descripcion else ""

        if not nombre:
            return "El nombre del módulo es obligatorio."

        if len(nombre) > 50:
            return "El nombre del módulo no puede exceder los 50 caracteres."

        if len(descripcion) > 255:
            return "La descripción del módulo no puede exceder los 255 caracteres."

        if self.verificar_modulo_por_nombre():
            return f"El módulo '{nombre}' ya existe."

        db = self.__conexion_bd.conexion2()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO modulo (nombre, descripcion) VALUES (%s, %s)",
                (nombre, descripcion),
            )
            db.commit()
            self.id = str(cursor.lastrowid)
            return f"Módulo agregado exitosamente."
        except Exception as e:
            print(f"Error al agregar módulo: {e}")
            db.rollback()
            return "Error al agregar módulo."
        finally:
            cursor.close()
            db.close()

    def actualizar_modulo(self) -> str:
        modulo_id = self.id.strip()
        nombre = self.nombre.strip()
        descripcion = self.descripcion.strip() if self.descripcion else ""

        if not modulo_id or not nombre:
            return "ID y nombre del módulo son obligatorios."

        if len(nombre) > 50:
            return "El nombre del módulo no puede exceder los 50 caracteres."

        if len(descripcion) > 255:
            return "La descripción del módulo no puede exceder los 255 caracteres."

        if not self.verificar_modulo_por_id():
            return f"El módulo con ID {modulo_id} no existe."

        # Verificar si el nuevo nombre ya existe (excepto para el mismo módulo)
        nombre_actual = self.obtener_modulo_por_id()
        if nombre_actual and nombre_actual["nombre"].lower() != nombre.lower():
            if self.verificar_modulo_por_nombre():
                return f"El módulo '{nombre}' ya existe."

        db = self.__conexion_bd.conexion2()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE modulo SET nombre = %s, descripcion = %s WHERE id = %s",
                (nombre, descripcion, modulo_id),
            )
            db.commit()
            return "Módulo actualizado exitosamente."
        except Exception as e:
            print(f"Error al actualizar módulo: {e}")
            db.rollback()
            return "Error al actualizar módulo."
        finally:
            cursor.close()
            db.close()

    def eliminar_modulo(self) -> str:
        modulo_id = self.id.strip()

        if not modulo_id:
            return "El identificador del módulo no puede estar vacío."

        if not self.verificar_modulo_por_id():
            return f"El módulo con identificador {modulo_id} no existe."

        db = self.__conexion_bd.conexion2()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM modulo WHERE id = %s", (modulo_id,))
            db.commit()
            return "Módulo eliminado exitosamente."
        except Exception as e:
            print(f"Error al eliminar módulo: {e}")
            db.rollback()
            return "Error al eliminar módulo. Verifica que no esté en uso por permisos."
        finally:
            cursor.close()
            db.close()

    def obtener_modulo_por_id(self, modulo_id: str = None):
        id_buscar = modulo_id or self.id
        if not id_buscar:
            return None

        db = self.__conexion_bd.conexion2()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, nombre, descripcion FROM modulo WHERE id = %s LIMIT 1",
                (id_buscar,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()