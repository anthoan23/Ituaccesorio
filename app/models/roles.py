from __future__ import annotations

from app.models.database import conectar
from app.models.bitacora import Bitacora
from app.utils.validators import (
    validar_solo_letras,
    validar_numero,
    validar_sin_caracteres_especiales,
)


class Rol:
    def __init__(self, id: str = "", nombre: str = "", descripcion: str = "", usuario_id: str = None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.usuario_id = usuario_id
        self.__conexion_bd = conectar()

    # ==================== VALIDACIONES ====================

    def _validar_datos(self, requiere_id: bool = False) -> str | None:
        if requiere_id:
            rol_id = str(self.id).strip() if self.id is not None else ""
            if not rol_id:
                return "El ID del rol es obligatorio."
            # rol.id int AUTO_INCREMENT
            error = validar_numero(rol_id, 1, 10, "Rol")
            if error:
                return error
            self.id = rol_id

        nombre = str(self.nombre).strip() if self.nombre is not None else ""
        # rol.nombre varchar(50) UNIQUE
        error = validar_solo_letras(nombre, 1, 50, "Nombre", permitir_espacios=True)
        if error:
            return error
        self.nombre = nombre

        descripcion = str(self.descripcion).strip() if self.descripcion else ""
        if descripcion:
            # rol.descripcion text; 255 es política de UI
            error = validar_sin_caracteres_especiales(descripcion, 1, 255, "Descripción", permitir_espacios=True)
            if error:
                return error
        self.descripcion = descripcion

        return None

    # ==================== CONSULTAS ====================

    def listar_roles(self):
        db = self.__conexion_bd.conexion2()
        if not db:
            return None
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, nombre, descripcion FROM rol ORDER BY nombre")
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
            cursor.execute("SELECT 1 FROM rol WHERE id = %s LIMIT 1", (self.id,))
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
            cursor.execute("SELECT 1 FROM rol WHERE nombre = %s LIMIT 1", (self.nombre,))
            return cursor.fetchone() is not None
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
            cursor.execute("SELECT id FROM rol WHERE nombre = %s LIMIT 1", (nombre_buscar,))
            row = cursor.fetchone()
            return str(row[0]) if row else None
        finally:
            cursor.close()
            db.close()

    # ==================== MUTACIONES ====================

    def agregar_rol(self) -> str:
        error = self._validar_datos(requiere_id=False)
        if error:
            return error

        if self.verificar_rol_por_nombre():
            return f"El rol '{self.nombre}' ya existe."

        db = self.__conexion_bd.conexion2()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO rol (nombre, descripcion) VALUES (%s, %s)",
                (self.nombre, self.descripcion or None),
            )
            db.commit()
            self.id = str(cursor.lastrowid)

            if self.usuario_id:
                Bitacora(
                    accion="Crear rol",
                    descripcion=f"Se creó el rol: {self.nombre}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Usuarios"
                ).registrar()

            return "Rol agregado exitosamente."
        except Exception as e:
            print(f"Error al agregar rol: {e}")
            db.rollback()
            return "Error al agregar rol."
        finally:
            cursor.close()
            db.close()

    def actualizar_rol(self) -> str:
        error = self._validar_datos(requiere_id=True)
        if error:
            return error

        if not self.verificar_rol_por_id():
            return f"El rol con ID {self.id} no existe."

        nombre_actual = self.obtener_rol_por_id()
        if nombre_actual and nombre_actual["nombre"].lower() != self.nombre.lower():
            if self.verificar_rol_por_nombre():
                return f"El rol '{self.nombre}' ya existe."

        db = self.__conexion_bd.conexion2()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE rol SET nombre = %s, descripcion = %s WHERE id = %s",
                (self.nombre, self.descripcion or None, self.id),
            )
            db.commit()

            if self.usuario_id:
                Bitacora(
                    accion="Actualizar rol",
                    descripcion=f"Se actualizó el rol ID: {self.id} - Nuevo nombre: {self.nombre}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Usuarios"
                ).registrar()

            return "Rol actualizado exitosamente."
        except Exception as e:
            print(f"Error al actualizar rol: {e}")
            db.rollback()
            return "Error al actualizar rol."
        finally:
            cursor.close()
            db.close()

    def eliminar_rol(self) -> str:
        rol_id = str(self.id).strip() if self.id else ""
        if not rol_id:
            return "El identificador del rol no puede estar vacío."

        # rol.id int
        error = validar_numero(rol_id, 1, 10, "Rol")
        if error:
            return error
        self.id = rol_id

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

            if self.usuario_id:
                Bitacora(
                    accion="Eliminar rol",
                    descripcion=f"Se eliminó el rol ID: {rol_id} - Nombre: {rol_actual['nombre'] if rol_actual else ''}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Usuarios"
                ).registrar()

            return "Rol eliminado exitosamente."
        except Exception as e:
            print(f"Error al eliminar rol: {e}")
            db.rollback()
            return "Error al eliminar rol. Verifica que no esté en uso por usuarios."
        finally:
            cursor.close()
            db.close()