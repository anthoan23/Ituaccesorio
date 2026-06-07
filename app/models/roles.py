from __future__ import annotations

from app.models.database import conectar


class Rol:
    def __init__(self, id: str = "", nombre: str = "", descripcion: str = ""):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.__conexion_bd = conectar()

    def listar_roles(self):
        db = self.__conexion_bd.conexion2()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, nombre, descripcion
                FROM rol
                ORDER BY nombre
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def verificar_rol_por_id(self) -> bool:
        if not self.id:
            return False

        db = self.__conexion_bd.conexion2()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM rol WHERE id = %s LIMIT 1",
                (self.id,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    def verificar_rol_por_nombre(self) -> bool:
        if not self.nombre:
            return False

        db = self.__conexion_bd.conexion2()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM rol WHERE nombre = %s LIMIT 1",
                (self.nombre,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    def agregar_rol(self) -> str:
        nombre = self.nombre.strip()
        descripcion = self.descripcion.strip() if self.descripcion else ""

        if not nombre:
            return "El nombre del rol es obligatorio."

        if len(nombre) > 50:
            return "El nombre del rol no puede exceder los 50 caracteres."

        if len(descripcion) > 255:
            return "La descripción del rol no puede exceder los 255 caracteres."

        if self.verificar_rol_por_nombre():
            return f"El rol '{nombre}' ya existe."

        db = self.__conexion_bd.conexion2()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO rol (nombre, descripcion) VALUES (%s, %s)",
                (nombre, descripcion),
            )
            db.commit()
            self.id = str(cursor.lastrowid)
            return f"Rol agregado exitosamente."
        except Exception as e:
            print(f"Error al agregar rol: {e}")
            db.rollback()
            return "Error al agregar rol."
        finally:
            cursor.close()
            db.close()

    def actualizar_rol(self) -> str:
        rol_id = self.id.strip()
        nombre = self.nombre.strip()
        descripcion = self.descripcion.strip() if self.descripcion else ""

        if not rol_id or not nombre:
            return "ID y nombre del rol son obligatorios."

        if len(nombre) > 50:
            return "El nombre del rol no puede exceder los 50 caracteres."

        if len(descripcion) > 255:
            return "La descripción del rol no puede exceder los 255 caracteres."

        if not self.verificar_rol_por_id():
            return f"El rol con ID {rol_id} no existe."

        # Verificar si el nuevo nombre ya existe (excepto para el mismo rol)
        nombre_actual = self.obtener_rol_por_id()
        if nombre_actual and nombre_actual["nombre"].lower() != nombre.lower():
            if self.verificar_rol_por_nombre():
                return f"El rol '{nombre}' ya existe."

        db = self.__conexion_bd.conexion2()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE rol SET nombre = %s, descripcion = %s WHERE id = %s",
                (nombre, descripcion, rol_id),
            )
            db.commit()
            return "Rol actualizado exitosamente."
        except Exception as e:
            print(f"Error al actualizar rol: {e}")
            db.rollback()
            return "Error al actualizar rol."
        finally:
            cursor.close()
            db.close()

    def eliminar_rol(self) -> str:
        rol_id = self.id.strip()

        if not rol_id:
            return "El identificador del rol no puede estar vacío."

        # Verificar que no sea un rol protegido
        rol_actual = self.obtener_rol_por_id()
        if rol_actual:
            nombre_rol = rol_actual["nombre"].lower()
            if nombre_rol in ["admin", "cliente"]:
                return "No se puede eliminar el rol Admin o Cliente."

        if not self.verificar_rol_por_id():
            return f"El rol con identificador {rol_id} no existe."

        db = self.__conexion_bd.conexion2()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM rol WHERE id = %s", (rol_id,))
            db.commit()
            return "Rol eliminado exitosamente."
        except Exception as e:
            print(f"Error al eliminar rol: {e}")
            db.rollback()
            return "Error al eliminar rol. Verifica que no esté en uso por usuarios."
        finally:
            cursor.close()
            db.close()

    def obtener_rol_por_id(self, rol_id: str = None):
        id_buscar = rol_id or self.id
        if not id_buscar:
            return None

        db = self.__conexion_bd.conexion2()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, nombre, descripcion FROM rol WHERE id = %s LIMIT 1",
                (id_buscar,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()

    def obtener_id_por_nombre(self, nombre: str = None) -> str | None:
        nombre_buscar = nombre or self.nombre
        if not nombre_buscar:
            return None

        db = self.__conexion_bd.conexion2()
        if not db:
            return None

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT id FROM rol WHERE nombre = %s LIMIT 1",
                (nombre_buscar,),
            )
            row = cursor.fetchone()
            return str(row[0]) if row else None
        finally:
            cursor.close()
            db.close()