from __future__ import annotations
from app.models.database import conectar

class Equipo:
    def __init__(self, ID_equipo: str = None, ID_producto: str = None,
                 Color: str = None, Capacidad: str = None, 
                 Clave: str = None, Patron: str = None):
        self.ID_equipo = ID_equipo
        self.ID_producto = ID_producto
        self.Color = Color
        self.Capacidad = Capacidad
        self.Clave = Clave
        self.Patron = Patron
        self._conexion = conectar()
    
    def _conexion_bd(self):
        return self._conexion.conexion1()
    
    def Consultar_equipo_por_id(self) -> dict:
        """Consulta un equipo por su ID (IMEI)"""
        if not self.ID_equipo:
            return None
        
        db = self._conexion_bd()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    e.ID_equipo,
                    e.ID_producto,
                    e.Color,
                    e.Capacidad,
                    e.Clave,
                    e.Patron,
                    p.Nombre_producto,
                    p.Descripcion,
                    cl.Nombre_Clase,
                    m.Nombre_marca
                FROM Equipo e
                LEFT JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                LEFT JOIN Marca_producto m ON p.ID_marca = m.ID_marca
                WHERE e.ID_equipo = %s
            """, (self.ID_equipo,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al consultar el equipo: {e}")
            return None
        finally:
            cursor.close()
            db.close()
    
    def registrar_equipo(self) -> str:
        """Registra un nuevo equipo en la base de datos"""
        if not self.ID_equipo:
            return "El ID del equipo es obligatorio."
        
        if not self.ID_producto:
            return "El ID del producto es obligatorio."
        
        if len(str(self.ID_equipo)) > 16:
            return "El ID del equipo no puede tener más de 15 caracteres."
        
        db = self._conexion_bd()
        if not db:
            return "Error al conectar con la base de datos."
        
        cursor = db.cursor()
        try:
            # Verificar si el equipo ya existe
            cursor.execute("SELECT ID_equipo FROM Equipo WHERE ID_equipo = %s", (self.ID_equipo,))
            if cursor.fetchone():
                return f"El equipo '{self.ID_equipo}' ya existe."
            
            # Manejar valores None para campos opcionales
            color = self.Color if self.Color else None
            if color and len(str(color)) > 30:
                return "El color no puede tener más de 30 caracteres."
            
            capacidad = self.Capacidad if self.Capacidad else None
            if capacidad and len(str(capacidad)) > 6:
                return "La capacidad no puede tener más de 6 caracteres."
            
            # Clave: convertir a int solo si es un número válido
            clave = None
            if self.Clave is not None and self.Clave != "":
                try:
                    clave = int(self.Clave)
                except (ValueError, TypeError):
                    return "La clave debe ser un número entero válido."
            
            # Patrón: se guarda como string (con guiones o sin ellos)
            patron = self.Patron if self.Patron else None
            if patron and len(str(patron)) > 17:
                return "El patrón no puede tener más de 17 caracteres."
            
            cursor.execute("""
                INSERT INTO Equipo (ID_equipo, ID_producto, Color, Capacidad, Clave, Patron)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (self.ID_equipo, self.ID_producto, color, capacidad, clave, patron))
            
            db.commit()
            return f"Equipo {self.ID_equipo} registrado exitosamente."
        except Exception as e:
            db.rollback()
            return f"Error al registrar el equipo: {e}"
        finally:
            cursor.close()
            db.close()
    
    def actualizar_equipo(self) -> str:
        """Actualiza los datos de un equipo existente"""
        if not self.ID_equipo:
            return "El ID del equipo es obligatorio."
        
        db = self._conexion_bd()
        if not db:
            return "Error al conectar con la base de datos."
        
        cursor = db.cursor()
        try:
            # Verificar si el equipo existe
            cursor.execute("SELECT ID_equipo FROM Equipo WHERE ID_equipo = %s", (self.ID_equipo,))
            if not cursor.fetchone():
                return f"No se encontró el equipo {self.ID_equipo}."
            
            # Construir dinámicamente la consulta de actualización
            updates = []
            params = []
            
            if self.ID_producto is not None:
                updates.append("ID_producto = %s")
                params.append(self.ID_producto)
            
            if self.Color is not None:
                color = self.Color if self.Color else None
                if color and len(str(color)) > 30:
                    return "El color no puede tener más de 30 caracteres."
                updates.append("Color = %s")
                params.append(color)
            
            if self.Capacidad is not None:
                capacidad = self.Capacidad if self.Capacidad else None
                if capacidad and len(str(capacidad)) > 20:
                    return "La capacidad no puede tener más de 20 caracteres."
                updates.append("Capacidad = %s")
                params.append(capacidad)
            
            if self.Clave is not None:
                clave = None
                if self.Clave != "":
                    try:
                        clave = int(self.Clave)
                    except (ValueError, TypeError):
                        return "La clave debe ser un número entero válido."
                updates.append("Clave = %s")
                params.append(clave)
            
            if self.Patron is not None:
                patron = self.Patron if self.Patron else None
                if patron and len(str(patron)) > 60:
                    return "El patrón no puede tener más de 60 caracteres."
                updates.append("Patron = %s")
                params.append(patron)
            
            if not updates:
                return "No hay datos para actualizar."
            
            params.append(self.ID_equipo)
            query = f"UPDATE Equipo SET {', '.join(updates)} WHERE ID_equipo = %s"
            
            cursor.execute(query, params)
            db.commit()
            
            return f"Equipo {self.ID_equipo} actualizado correctamente."
        except Exception as e:
            db.rollback()
            return f"Error al actualizar el equipo: {e}"
        finally:
            cursor.close()
            db.close()
    
    def eliminar_equipo(self) -> str:
        """Elimina un equipo de la base de datos"""
        if not self.ID_equipo:
            return "El ID del equipo es obligatorio."
        
        db = self._conexion_bd()
        if not db:
            return "Error al conectar con la base de datos."
        
        cursor = db.cursor()
        try:
            # Verificar si el equipo existe
            cursor.execute("SELECT ID_equipo FROM Equipo WHERE ID_equipo = %s", (self.ID_equipo,))
            if not cursor.fetchone():
                return f"No se encontró el equipo {self.ID_equipo}."
            
            # Verificar si está siendo usado en Trade_in
            cursor.execute("SELECT COUNT(*) FROM Trade_in WHERE ID_equipo = %s", (self.ID_equipo,))
            if cursor.fetchone()[0] > 0:
                return f"No se puede eliminar el equipo {self.ID_equipo} porque tiene trade-ins asociados."
            
            # Verificar si está siendo usado en Orden_servicio
            cursor.execute("SELECT COUNT(*) FROM Orden_servicio WHERE ID_equipo = %s", (self.ID_equipo,))
            if cursor.fetchone()[0] > 0:
                return f"No se puede eliminar el equipo {self.ID_equipo} porque tiene órdenes de servicio asociadas."
            
            cursor.execute("DELETE FROM Equipo WHERE ID_equipo = %s", (self.ID_equipo,))
            db.commit()
            return f"Equipo {self.ID_equipo} eliminado correctamente."
        except Exception as e:
            db.rollback()
            return f"Error al eliminar el equipo: {e}"
        finally:
            cursor.close()
            db.close()