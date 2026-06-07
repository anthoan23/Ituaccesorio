from __future__ import annotations
from app.models.database import conectar
from typing import List, Dict, Any


class PersonalDeliveryModel:
    """Modelo para gestionar el personal de delivery"""
    
    def __init__(self):
        self.__conexion_bd = conectar()
    
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
    
    def obtener_personal_por_cedula(self, cedula: str) -> Dict[str, Any] | None:
        """Obtiene un delivery por su cédula"""
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
            """, (cedula,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()
    
    def verificar_personal_existe(self, cedula: str) -> bool:
        """Verifica si un delivery existe"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return False
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM Personal_delivery WHERE Cedula_delivery = %s LIMIT 1",
                (cedula,)
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()
    
    def agregar_personal(self, cedula: str, nombre: str, apellido: str) -> str:
        """Agrega un nuevo delivery"""
        cedula = cedula.strip()
        nombre = nombre.strip()
        apellido = apellido.strip()
        
        if not cedula:
            return "La cédula es obligatoria."
        if not nombre:
            return "El nombre es obligatorio."
        if not apellido:
            return "El apellido es obligatorio."
        
        if not cedula.isdigit():
            return "La cédula debe contener solo números."
        
        if len(cedula) > 15:
            return "La cédula no puede exceder 15 caracteres."
        
        if len(nombre) > 40:
            return "El nombre no puede exceder 40 caracteres."
        
        if len(apellido) > 40:
            return "El apellido no puede exceder 40 caracteres."
        
        if self.verificar_personal_existe(cedula):
            return f"Ya existe un delivery con cédula {cedula}."
        
        db = self.__conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO Personal_delivery (Cedula_delivery, Nombre_delivery, Apellido_delivery)
                VALUES (%s, %s, %s)
            """, (cedula, nombre, apellido))
            db.commit()
            return "Delivery registrado exitosamente."
        except Exception as e:
            db.rollback()
            print(f"Error al agregar personal: {e}")
            return f"Error al registrar: {e}"
        finally:
            cursor.close()
            db.close()
    
    def actualizar_personal(self, cedula: str, nombre: str, apellido: str) -> str:
        """Actualiza un delivery existente"""
        cedula = cedula.strip()
        nombre = nombre.strip()
        apellido = apellido.strip()
        
        if not cedula:
            return "La cédula es obligatoria."
        if not nombre:
            return "El nombre es obligatorio."
        if not apellido:
            return "El apellido es obligatorio."
        
        if not self.verificar_personal_existe(cedula):
            return f"No existe un delivery con cédula {cedula}."
        
        db = self.__conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE Personal_delivery 
                SET Nombre_delivery = %s, Apellido_delivery = %s
                WHERE Cedula_delivery = %s
            """, (nombre, apellido, cedula))
            db.commit()
            return "Delivery actualizado exitosamente."
        except Exception as e:
            db.rollback()
            print(f"Error al actualizar personal: {e}")
            return f"Error al actualizar: {e}"
        finally:
            cursor.close()
            db.close()
    
    def eliminar_personal(self, cedula: str) -> str:
        """Elimina un delivery"""
        cedula = cedula.strip()
        
        if not cedula:
            return "La cédula es obligatoria."
        
        if not self.verificar_personal_existe(cedula):
            return f"No existe un delivery con cédula {cedula}."
        
        db = self.__conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."
        
        cursor = db.cursor()
        try:
            # Verificar si tiene entregas asociadas
            cursor.execute(
                "SELECT 1 FROM Entrega WHERE Cedula_delivery = %s LIMIT 1",
                (cedula,)
            )
            if cursor.fetchone():
                return "No se puede eliminar el delivery porque tiene entregas asociadas."
            
            cursor.execute(
                "DELETE FROM Personal_delivery WHERE Cedula_delivery = %s",
                (cedula,)
            )
            db.commit()
            return "Delivery eliminado exitosamente."
        except Exception as e:
            db.rollback()
            print(f"Error al eliminar personal: {e}")
            return f"Error al eliminar: {e}"
        finally:
            cursor.close()
            db.close()