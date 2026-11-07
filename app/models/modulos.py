from __future__ import annotations

from app.models.database import conectar
from app.models.bitacora import Bitacora
from app.utils.validators import (
    validar_numero,
    validar_solo_letras_numeros,
    validar_sin_caracteres_especiales,
)


class Modulo:
    def __init__(self, id: str = "", nombre: str = "", descripcion: str = "", usuario_id: str = None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.usuario_id = usuario_id
        self.__conexion_bd = conectar()

    # ==================== VALIDACIONES ====================

    def _validar_datos(self, requiere_id: bool = False) -> str | None:
        if requiere_id:
            modulo_id = str(self.id).strip() if self.id is not None else ""
            if not modulo_id:
                return "El ID del módulo es obligatorio."
            # modulo.id int AUTO_INCREMENT
            error = validar_numero(modulo_id, 1, 10, "Módulo")
            if error:
                return error
            self.id = modulo_id

        nombre = str(self.nombre).strip() if self.nombre is not None else ""
        # modulo.nombre varchar(50) UNIQUE
        error = validar_solo_letras_numeros(nombre, 1, 50, "Nombre", permitir_espacios=False)
        if error:
            return error
        self.nombre = nombre

        descripcion = str(self.descripcion).strip() if self.descripcion else ""
        if descripcion:
            # modulo.descripcion text; 255 es política de UI
            error = validar_sin_caracteres_especiales(descripcion, 1, 255, "Descripción", permitir_espacios=True)
            if error:
                return error
        self.descripcion = descripcion

        return None

    # ==================== CONSULTAS ====================

    def listar_modulos(self):
        db = self.__conexion_bd.conexion2()
        if not db:
            return None
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, nombre, descripcion FROM modulo ORDER BY nombre")
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
            cursor.execute("SELECT 1 FROM modulo WHERE id = %s LIMIT 1", (self.id,))
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
            cursor.execute("SELECT 1 FROM modulo WHERE nombre = %s LIMIT 1", (self.nombre,))
            return cursor.fetchone() is not None
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

    # ==================== MUTACIONES ====================

    def agregar_modulo(self) -> str:
        error = self._validar_datos(requiere_id=False)
        if error:
            return error

        if self.verificar_modulo_por_nombre():
            return f"El módulo '{self.nombre}' ya existe."

        db = self.__conexion_bd.conexion2()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO modulo (nombre, descripcion) VALUES (%s, %s)",
                (self.nombre, self.descripcion or None),
            )
            db.commit()
            self.id = str(cursor.lastrowid)

            if self.usuario_id:
                Bitacora(
                    accion="Crear módulo",
                    descripcion=f"Se creó el módulo: {self.nombre}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Usuarios"
                ).registrar()

            return "Módulo agregado exitosamente."
        except Exception as e:
            print(f"Error al agregar módulo: {e}")
            db.rollback()
            return "Error al agregar módulo."
        finally:
            cursor.close()
            db.close()

    def actualizar_modulo(self) -> str:
        error = self._validar_datos(requiere_id=True)
        if error:
            return error

        if not self.verificar_modulo_por_id():
            return f"El módulo con ID {self.id} no existe."

        nombre_actual = self.obtener_modulo_por_id()
        if nombre_actual and nombre_actual["nombre"].lower() != self.nombre.lower():
            if self.verificar_modulo_por_nombre():
                return f"El módulo '{self.nombre}' ya existe."

        db = self.__conexion_bd.conexion2()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE modulo SET nombre = %s, descripcion = %s WHERE id = %s",
                (self.nombre, self.descripcion or None, self.id),
            )
            db.commit()

            if self.usuario_id:
                Bitacora(
                    accion="Actualizar módulo",
                    descripcion=f"Se actualizó el módulo ID: {self.id} - Nuevo nombre: {self.nombre}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Usuarios"
                ).registrar()

            return "Módulo actualizado exitosamente."
        except Exception as e:
            print(f"Error al actualizar módulo: {e}")
            db.rollback()
            return "Error al actualizar módulo."
        finally:
            cursor.close()
            db.close()

    def eliminar_modulo(self) -> str:
        modulo_id = str(self.id).strip() if self.id else ""
        if not modulo_id:
            return "El identificador del módulo no puede estar vacío."

        # modulo.id int
        error = validar_numero(modulo_id, 1, 10, "Módulo")
        if error:
            return error
        self.id = modulo_id

        if not self.verificar_modulo_por_id():
            return f"El módulo con identificador {modulo_id} no existe."

        db = self.__conexion_bd.conexion2()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM modulo WHERE id = %s", (modulo_id,))
            db.commit()

            if self.usuario_id:
                Bitacora(
                    accion="Eliminar módulo",
                    descripcion=f"Se eliminó el módulo ID: {modulo_id}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Usuarios"
                ).registrar()

            return "Módulo eliminado exitosamente."
        except Exception as e:
            print(f"Error al eliminar módulo: {e}")
            db.rollback()
            return "Error al eliminar módulo. Verifica que no esté en uso por permisos."
        finally:
            cursor.close()
            db.close()