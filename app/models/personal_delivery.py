from __future__ import annotations
from app.models.database import conectar
from app.models.bitacora import Bitacora
from app.utils.validators import validar_numero, validar_texto
from typing import List, Dict, Any, Optional


class PersonalDeliveryModel:
    """Modelo para gestionar el personal de delivery"""

    def __init__(self, cedula: str = None, nombre: str = None, apellido: str = None, usuario_id: str = None):
        self.cedula = cedula
        self.nombre = nombre
        self.apellido = apellido
        self.usuario_id = usuario_id
        self.__conexion_bd = conectar()

    # ==================== VALIDACIONES ====================

    def _validar_datos(self, requiere_existencia: bool = False) -> Optional[str]:
        """Valida cédula, nombre y apellido contra el esquema."""
        cedula = str(self.cedula).strip() if self.cedula is not None else ""
        nombre = str(self.nombre).strip() if self.nombre is not None else ""
        apellido = str(self.apellido).strip() if self.apellido is not None else ""

        if not cedula:
            return "La cédula es obligatoria."
        # Personal_delivery.Cedula_delivery varchar(15)
        error = validar_numero(cedula, 6, 15, "Cédula")
        if error:
            return error
        self.cedula = cedula

        if not nombre:
            return "El nombre es obligatorio."
        # Personal_delivery.Nombre_delivery varchar(40)
        error = validar_texto(nombre, 1, 40, "Nombre")
        if error:
            return error
        self.nombre = nombre

        if not apellido:
            return "El apellido es obligatorio."
        # Personal_delivery.Apellido_delivery varchar(40)
        error = validar_texto(apellido, 1, 40, "Apellido")
        if error:
            return error
        self.apellido = apellido

        if requiere_existencia and not self.verificar_personal_existe():
            return f"No existe un delivery con cédula {self.cedula}."

        return None

    # ==================== CONSULTAS ====================

    def listar_personal(self) -> List[Dict[str, Any]]:
        """Lista todo el personal de delivery"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    Cedula_delivery AS cedula,
                    Nombre_delivery AS nombre,
                    Apellido_delivery AS apellido,
                    CONCAT(Nombre_delivery, ' ', Apellido_delivery) AS nombre_completo
                FROM Personal_delivery
                ORDER BY Nombre_delivery ASC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en listar_personal: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def obtener_personal_por_cedula(self, cedula: str = None) -> Dict[str, Any] | None:
        """Obtiene un delivery por su cédula"""
        ced = cedula or self.cedula
        if not ced:
            return None

        db = self.__conexion_bd.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    Cedula_delivery AS cedula,
                    Nombre_delivery AS nombre,
                    Apellido_delivery AS apellido,
                    CONCAT(Nombre_delivery, ' ', Apellido_delivery) AS nombre_completo
                FROM Personal_delivery
                WHERE Cedula_delivery = %s
            """, (ced,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()

    def verificar_personal_existe(self, cedula: str = None) -> bool:
        """Verifica si un delivery existe"""
        ced = cedula or self.cedula
        if not ced:
            return False

        db = self.__conexion_bd.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM Personal_delivery WHERE Cedula_delivery = %s LIMIT 1",
                (ced,)
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    # ==================== MUTACIONES ====================

    def agregar_personal(self) -> str:
        """Agrega un nuevo delivery"""
        error = self._validar_datos(requiere_existencia=False)
        if error:
            return error

        if self.verificar_personal_existe():
            return f"Ya existe un delivery con cédula {self.cedula}."

        db = self.__conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO Personal_delivery (Cedula_delivery, Nombre_delivery, Apellido_delivery)
                VALUES (%s, %s, %s)
            """, (self.cedula, self.nombre, self.apellido))
            db.commit()

            if self.usuario_id:
                Bitacora(
                    accion="Registrar delivery",
                    descripcion=f"Se registró al delivery: {self.nombre} {self.apellido} - Cédula: {self.cedula}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Entregas"
                ).registrar()

            return "Delivery registrado exitosamente."
        except Exception as e:
            db.rollback()
            print(f"Error al agregar personal: {e}")
            return f"Error al registrar: {e}"
        finally:
            cursor.close()
            db.close()

    def actualizar_personal(self) -> str:
        """Actualiza un delivery existente"""
        error = self._validar_datos(requiere_existencia=True)
        if error:
            return error

        db = self.__conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE Personal_delivery
                SET Nombre_delivery = %s, Apellido_delivery = %s
                WHERE Cedula_delivery = %s
            """, (self.nombre, self.apellido, self.cedula))
            db.commit()

            if self.usuario_id:
                Bitacora(
                    accion="Actualizar delivery",
                    descripcion=f"Se actualizó al delivery con cédula: {self.cedula}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Entregas"
                ).registrar()

            return "Delivery actualizado exitosamente."
        except Exception as e:
            db.rollback()
            print(f"Error al actualizar personal: {e}")
            return f"Error al actualizar: {e}"
        finally:
            cursor.close()
            db.close()

    def eliminar_personal(self) -> str:
        """Elimina un delivery"""
        cedula = str(self.cedula).strip() if self.cedula is not None else ""
        if not cedula:
            return "La cédula es obligatoria."
        # Personal_delivery.Cedula_delivery varchar(15)
        error = validar_numero(cedula, 6, 15, "Cédula")
        if error:
            return error
        self.cedula = cedula

        if not self.verificar_personal_existe():
            return f"No existe un delivery con cédula {self.cedula}."

        personal_info = self.obtener_personal_por_cedula()
        nombre_completo = f"{personal_info.get('nombre', '')} {personal_info.get('apellido', '')}" if personal_info else self.cedula

        db = self.__conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM Entrega WHERE Cedula_delivery = %s LIMIT 1",
                (self.cedula,)
            )
            if cursor.fetchone():
                return "No se puede eliminar el delivery porque tiene entregas asociadas."

            cursor.execute(
                "DELETE FROM Personal_delivery WHERE Cedula_delivery = %s",
                (self.cedula,)
            )
            db.commit()

            if self.usuario_id:
                Bitacora(
                    accion="Eliminar delivery",
                    descripcion=f"Se eliminó al delivery con cédula: {self.cedula} - Nombre: {nombre_completo}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Entregas"
                ).registrar()

            return "Delivery eliminado exitosamente."
        except Exception as e:
            db.rollback()
            print(f"Error al eliminar personal: {e}")
            return f"Error al eliminar: {e}"
        finally:
            cursor.close()
            db.close()