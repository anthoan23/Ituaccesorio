from __future__ import annotations
from app.models.database import conectar
from app.models.productos import Producto

class Equipo(Producto):
    def __init__(self, ID_equipo: str, ID_producto: str = None, Color: str = None, Capacidad: str = None, Clave: str = None, Patron: str = None):
        self.ID_equipo = ID_equipo
        self.ID_producto = ID_producto
        self.Color = Color
        self.Capacidad = Capacidad
        self.Clave = Clave
        self.Patron = Patron
         
        self._conexion = conectar()     


    def Consultar_equipo_por_id(self) -> dict:

        id_equipo = self.ID_equipo
       
        if not id_equipo:
            return {"success": False, "message": "El ID del equipo es obligatorio."}
        
        if not str(id_equipo).isdigit():
            return {"success": False, "message": "El ID del equipo debe ser un número entero."}

        db = self._conexion.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    ID_equipo,
                    Color,
                    Capacidad,
                    Clave,
                    Patron
                FROM equipo
                WHERE ID_equipo = %s
                limit 1
                """,
                (str(id_equipo),)
            )
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al consultar el equipo: {e}")
            return None
        finally:
            cursor.close()
            db.close()

    def registrar_equipo(self) -> str:
        id_equipo = (self.ID_equipo or "").strip()
        id_producto = (self.ID_producto or "").strip() or None
        color = (self.Color or "").strip()
        capacidad = (self.Capacidad or "").strip()
        clave = (self.Clave or "").strip() if self.Clave is not None else None
        patron = (self.Patron or "").strip() if self.Patron is not None else None
       
       # Comienzan las validaciones

        if not id_equipo:
            return "El ID del equipo es obligatorio."
        
        if not id_equipo.isdigit():
            return "El ID del equipo debe ser un número entero."
        
        if len(id_equipo) > 15:
            return "El ID del equipo no puede tener más de 15 dígitos."
    
        if not color:
            return "El color del equipo es obligatorio."
        
        if len(color) > 30:
            return "El color del equipo no puede tener más de 30 caracteres."
        
        if not capacidad:
            return "La capacidad del equipo es obligatoria."
        
        db = self._conexion.conexion1()
        if not db:
            return "Error al conectar con la base de datos."
        
        cursor = db.cursor()
        try:
            cursor.execute("SELECT ID_equipo FROM Equipo WHERE ID_equipo = %s", (id_equipo,))
            if cursor.fetchone():
                return f"El IMEI del equipo '{id_equipo}' ya existe. Por favor verifica de nuevo el IMEI."
            
            cursor.execute(
                "INSERT INTO Equipo (ID_equipo, ID_producto, Color, Capacidad, Clave, Patron) VALUES (%s, %s, %s, %s, %s, %s)",
                (id_equipo, id_producto, color, capacidad, clave, patron)
            )
            db.commit()
            return f"El equipo con ID {id_equipo} se registró exitosamente."
        except Exception as e:
            db.rollback()
            return f"Error al registrar el equipo: {e}"
        finally:
            cursor.close()
            db.close()

    def registrar_equipo_minimo(self) -> str:
        id_equipo = (self.ID_equipo or "").strip()
        id_producto = (self.ID_producto or "").strip() or None
        color = (self.Color or "").strip() if self.Color is not None else None
        capacidad = (self.Capacidad or "").strip() if self.Capacidad is not None else None
        clave = (self.Clave or "").strip() if self.Clave is not None else None
        patron = (self.Patron or "").strip() if self.Patron is not None else None

        if not id_equipo:
            return "El ID del equipo es obligatorio."
        
        if not id_equipo.isdigit():
            return "El ID del equipo debe ser un número entero."
        
        if len(id_equipo) > 15:
            return "El ID del equipo no puede tener más de 15 dígitos."

        db = self._conexion.conexion1()
        if not db:
            return "Error al conectar con la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute("SELECT ID_equipo FROM Equipo WHERE ID_equipo = %s", (id_equipo,))
            if cursor.fetchone():
                return "exists"

            cursor.execute(
                "INSERT INTO Equipo (ID_equipo, ID_producto, Color, Capacidad, Clave, Patron) VALUES (%s, %s, %s, %s, %s, %s)",
                (id_equipo, id_producto, color, capacidad, clave, patron)
            )
            db.commit()
            return f"El equipo con ID {id_equipo} se registró exitosamente."
        except Exception as e:
            db.rollback()
            return f"Error al registrar el equipo: {e}"
        finally:
            cursor.close()
            db.close()
        
    def actualizar_producto_equipo(self) -> str:
        id_equipo = (self.ID_equipo or "").strip()
        id_producto = (self.ID_producto or "").strip()

        if not id_equipo:
            return "El ID del equipo es obligatorio."
        if not id_producto:
            return "El ID del producto es obligatorio para actualizar el equipo."

        db = self._conexion.conexion1()
        if not db:
            return "Error al conectar con la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE Equipo SET ID_producto = %s WHERE ID_equipo = %s",
                (id_producto, id_equipo)
            )
            db.commit()
            if cursor.rowcount == 0:
                return f"No se encontró el equipo con ID {id_equipo}."
            return f"El equipo con ID {id_equipo} se actualizó con el modelo {id_producto}."
        except Exception as e:
            db.rollback()
            return f"Error al actualizar el equipo: {e}"
        finally:
            cursor.close()
            db.close()
    
    def actualizar_equipo(self) -> str:
        id_equipo = self.ID_equipo.strip()
        color = self.Color.strip()
        capacidad = self.Capacidad.strip()
        clave = self.Clave.strip()
        patron = self.Patron.strip()

        if not id_equipo:
            return "El ID del equipo es obligatorio."
        
        if not id_equipo.isdigit():
            return "El ID del equipo debe ser un número entero."
        
        if len(id_equipo) > 15:
            return "El ID del equipo no puede tener más de 15 dígitos."
    
        if not color:
            return "El color del equipo es obligatorio."
        
        if len(color) >30:
            return "El color del equipo no puede tener más de 30 caracteres."
        
        if not capacidad:
            return "La capacidad del equipo es obligatoria."
        
        db = self._conexion.conexion1()
        if not db:
            return "Error al conectar con la base de datos."
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE equipo SET Color = %s, Capacidad = %s, Clave = %s, Patron = %s WHERE ID_equipo = %s",
                (color, capacidad, clave, patron, id_equipo)
            )
            db.commit()
            if cursor.rowcount == 0:
                return f"No se encontró un equipo con ID {id_equipo} para actualizar."
            return f"El equipo con ID {id_equipo} se actualizó exitosamente."
        except Exception as e:
            db.rollback()
            return f"Error al actualizar el equipo: {e}"
        finally:
            cursor.close()
            db.close()
    
    def eliminar_equipo(self) -> str:
        
        id_equipo = self.ID_equipo.strip()

        if not id_equipo:
            return "El ID del equipo es obligatorio."
        
        if not id_equipo.isdigit():
            return "El ID del equipo debe ser un número entero."
        
        if len(id_equipo) > 15:
            return "El ID del equipo no puede tener más de 15 dígitos."
        
        if not self.verificar_equipo_por_id():
            return f"No se encontró un equipo con ID {id_equipo} para eliminar."
        
        db = self._conexion.conexion1()
        if not db:
            return "Error al conectar con la base de datos."
        
        cursor = db.cursor()
        try:
            sql = "DELETE FROM equipo WHERE ID_equipo = %s"
            cursor.execute(sql, (id_equipo,))
            db.commit()
            mensaje = f"El equipo con ID {id_equipo} se eliminó exitosamente."
            return mensaje
        except Exception as e:
            print(f"Error al eliminar el equipo: {e}")
            db.rollback()
            if hasattr(e, 'errno') and e.errno == 1451:
                mensaje = f"No se puede eliminar el equipo con ID {id_equipo} porque está en uso por órdenes de servicio."
                return mensaje
            mensaje = "Error al eliminar el equipo. Verifica que no esté en uso por órdenes de servicio."
            return mensaje
        finally:
            cursor.close()
            db.close()