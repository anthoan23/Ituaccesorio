from __future__ import annotations
from app.models.database import conectar
from app.models.bitacora import Bitacora
from typing import List, Dict, Any


class PersonalDeliveryModel:
    """Modelo para gestionar el personal de delivery"""
    
    def __init__(self, cedula: str = None, nombre: str = None, apellido: str = None, usuario_id: str = None):
        self.cedula = cedula
        self.nombre = nombre
        self.apellido = apellido
        self.usuario_id = usuario_id
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
    
    def agregar_personal(self) -> str:
        """Agrega un nuevo delivery"""
        if not self.cedula:
            return "La cédula es obligatoria."
        if not self.nombre:
            return "El nombre es obligatorio."
        if not self.apellido:
            return "El apellido es obligatorio."
        
        if not self.cedula.isdigit():
            return "La cédula debe contener solo números."
        
        if len(self.cedula) > 15:
            return "La cédula no puede exceder 15 caracteres."
        
        if len(self.nombre) > 40:
            return "El nombre no puede exceder 40 caracteres."
        
        if len(self.apellido) > 40:
            return "El apellido no puede exceder 40 caracteres."
        
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
        if not self.cedula:
            return "La cédula es obligatoria."
        if not self.nombre:
            return "El nombre es obligatorio."
        if not self.apellido:
            return "El apellido es obligatorio."
        
        if not self.verificar_personal_existe():
            return f"No existe un delivery con cédula {self.cedula}."
        
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
        if not self.cedula:
            return "La cédula es obligatoria."
        
        if not self.verificar_personal_existe():
            return f"No existe un delivery con cédula {self.cedula}."
        
        # Obtener nombre antes de eliminar
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