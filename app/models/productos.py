from __future__ import annotations
from app.models.database import conectar


class ClaseProducto(conectar):
    """Modelo para la tabla Clase_producto"""
    
    def __init__(self, id_clase: str = "", nombre: str = ""):
        self.id_clase = id_clase
        self.nombre = nombre

    def _siguiente_id(self) -> str:
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        cursor = db.cursor()
        try:
            cursor.execute("SELECT COALESCE(MAX(CAST(ID_Clase AS UNSIGNED)), 0) + 1 FROM Clase_producto")
            row = cursor.fetchone()
            return str(int(row[0] or 0))
        finally:
            cursor.close()
            db.close()

    def listar(self):
        db = self.conexion1()
        if not db:
            return []
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT ID_Clase AS id, Nombre_Clase AS nombre
                FROM Clase_producto
                ORDER BY CAST(ID_Clase AS UNSIGNED) ASC
            """)
            return cursor.fetchall() or []
        finally:
            cursor.close()
            db.close()

    def crear(self) -> str:
        if not self.nombre:
            raise ValueError("El nombre de la clase es obligatorio.")
        
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            new_id = self._siguiente_id()
            cursor.execute(
                "INSERT INTO Clase_producto (ID_Clase, Nombre_Clase) VALUES (%s, %s)",
                (new_id, self.nombre)
            )
            db.commit()
            return new_id
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def actualizar(self) -> bool:
        if not self.id_clase or not self.nombre:
            raise ValueError("ID y nombre son requeridos.")
        
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE Clase_producto SET Nombre_Clase = %s WHERE ID_Clase = %s",
                (self.nombre, self.id_clase)
            )
            db.commit()
            return cursor.rowcount > 0
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def eliminar(self) -> bool:
        if not self.id_clase:
            raise ValueError("ID es requerido.")
        
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM Clase_producto WHERE ID_Clase = %s", (self.id_clase,))
            db.commit()
            return cursor.rowcount > 0
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()


class MarcaProducto(conectar):
    """Modelo para la tabla Marca_producto"""
    
    def __init__(self, id_marca: str = "", nombre: str = "", id_clase: str | None = None):
        self.id_marca = id_marca
        self.nombre = nombre
        self.id_clase = id_clase

    def _siguiente_id(self) -> str:
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        cursor = db.cursor()
        try:
            cursor.execute("SELECT COALESCE(MAX(CAST(ID_marca AS UNSIGNED)), 0) + 1 FROM Marca_producto")
            row = cursor.fetchone()
            return str(int(row[0] or 0))
        finally:
            cursor.close()
            db.close()

    def listar(self, id_clase: str | None = None):
        db = self.conexion1()
        if not db:
            return []
        cursor = db.cursor(dictionary=True)
        try:
            if id_clase:
                cursor.execute("""
                    SELECT DISTINCT ma.ID_marca AS id, ma.Nombre_marca AS nombre
                    FROM Marca_producto ma
                    JOIN Producto p ON p.ID_marca = ma.ID_marca
                    WHERE p.ID_Clase = %s
                    ORDER BY CAST(ma.ID_marca AS UNSIGNED) ASC
                """, (id_clase,))
            else:
                cursor.execute("""
                    SELECT ID_marca AS id, Nombre_marca AS nombre
                    FROM Marca_producto
                    ORDER BY CAST(ID_marca AS UNSIGNED) ASC
                """)
            return cursor.fetchall() or []
        finally:
            cursor.close()
            db.close()

    def crear(self) -> str:
        if not self.nombre:
            raise ValueError("El nombre de la marca es obligatorio.")
        
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            new_id = self._siguiente_id()
            cursor.execute(
                "INSERT INTO Marca_producto (ID_marca, Nombre_marca) VALUES (%s, %s)",
                (new_id, self.nombre)
            )
            db.commit()
            return new_id
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def actualizar(self) -> bool:
        if not self.id_marca or not self.nombre:
            raise ValueError("ID y nombre son requeridos.")
        
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE Marca_producto SET Nombre_marca = %s WHERE ID_marca = %s",
                (self.nombre, self.id_marca)
            )
            db.commit()
            return cursor.rowcount > 0
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def eliminar(self) -> bool:
        if not self.id_marca:
            raise ValueError("ID es requerido.")
        
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM Marca_producto WHERE ID_marca = %s", (self.id_marca,))
            db.commit()
            return cursor.rowcount > 0
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()


class Producto(conectar):
    """Modelo para la tabla Producto"""
    
    def __init__(self, id_producto: str = "", id_clase: str = "", id_marca: str = "", 
                 nombre: str = "", descripcion: str | None = None):
        self.id_producto = id_producto
        self.id_clase = id_clase
        self.id_marca = id_marca
        self.nombre = nombre
        self.descripcion = descripcion

    def _siguiente_id(self) -> str:
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        cursor = db.cursor()
        try:
            cursor.execute("SELECT COALESCE(MAX(CAST(ID_producto AS UNSIGNED)), 0) + 1 FROM Producto")
            row = cursor.fetchone()
            return str(int(row[0] or 0))
        finally:
            cursor.close()
            db.close()

    def _siguiente_id_inventario(self) -> str:
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        cursor = db.cursor()
        try:
            cursor.execute("SELECT COALESCE(MAX(CAST(ID_inventario AS UNSIGNED)), 0) + 1 FROM Inventario")
            row = cursor.fetchone()
            return str(int(row[0] or 0))
        finally:
            cursor.close()
            db.close()

    def listar(self, id_marca: str | None = None, id_clase: str | None = None, q: str | None = None):
        db = self.conexion1()
        if not db:
            return []
        cursor = db.cursor(dictionary=True)
        try:
            where = []
            params = []
            if id_marca:
                where.append("p.ID_marca = %s")
                params.append(id_marca)
            if id_clase:
                where.append("p.ID_Clase = %s")
                params.append(id_clase)
            if q:
                where.append("p.Nombre_producto LIKE %s")
                params.append(f"%{q}%")

            where_sql = f"WHERE {' AND '.join(where)}" if where else ""

            cursor.execute(f"""
                SELECT
                    p.ID_producto AS id,
                    p.ID_marca AS id_marca,
                    p.ID_Clase AS id_clase,
                    p.Nombre_producto AS nombre,
                    p.Descripcion AS descripcion,
                    ma.Nombre_marca AS marca_nombre,
                    cl.Nombre_Clase AS clase_nombre
                FROM Producto p
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                {where_sql}
                ORDER BY CAST(cl.ID_Clase AS UNSIGNED) ASC, CAST(ma.ID_marca AS UNSIGNED) ASC, p.Nombre_producto ASC
            """, tuple(params))
            return cursor.fetchall() or []
        finally:
            cursor.close()
            db.close()

    def crear(self) -> str:
        if not self.id_clase or not self.id_marca or not self.nombre:
            raise ValueError("Clase, marca y nombre son obligatorios.")
        
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            new_id = self._siguiente_id()
            cursor.execute("""
                INSERT INTO Producto (ID_producto, ID_Clase, ID_marca, Nombre_producto, Descripcion)
                VALUES (%s, %s, %s, %s, %s)
            """, (new_id, self.id_clase, self.id_marca, self.nombre, self.descripcion))

            # Crear inventario básico con existencia 0
            id_inventario = self._siguiente_id_inventario()
            cursor.execute("""
                INSERT INTO Inventario (ID_inventario, ID_producto, Existencia, Costo_venta, Numero_inventario)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_inventario, new_id, 0, 0, None))

            db.commit()
            return new_id
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def actualizar(self) -> bool:
        if not self.id_producto or not self.id_clase or not self.id_marca or not self.nombre:
            raise ValueError("ID, clase, marca y nombre son requeridos.")
        
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE Producto
                SET ID_Clase = %s, ID_marca = %s, Nombre_producto = %s, Descripcion = %s
                WHERE ID_producto = %s
            """, (self.id_clase, self.id_marca, self.nombre, self.descripcion, self.id_producto))
            db.commit()
            return cursor.rowcount > 0
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def eliminar(self) -> bool:
        if not self.id_producto:
            raise ValueError("ID es requerido.")
        
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            # Eliminar relaciones primero (FK)
            cursor.execute("DELETE FROM Inventario WHERE ID_producto = %s", (self.id_producto,))
            cursor.execute("DELETE FROM Suministra WHERE ID_producto = %s", (self.id_producto,))
            cursor.execute("DELETE FROM Producto WHERE ID_producto = %s", (self.id_producto,))
            db.commit()
            return cursor.rowcount > 0
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def obtener_por_id(self, id_producto: str):
        db = self.conexion1()
        if not db:
            return None
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    p.ID_producto AS id,
                    p.ID_marca AS id_marca,
                    p.ID_Clase AS id_clase,
                    p.Nombre_producto AS nombre,
                    p.Descripcion AS descripcion,
                    ma.Nombre_marca AS marca_nombre,
                    cl.Nombre_Clase AS clase_nombre
                FROM Producto p
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                WHERE p.ID_producto = %s
            """, (id_producto,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()