from __future__ import annotations
from decimal import Decimal
from app.models.database import conectar


class Inventario:
    """Modelo para la tabla Existencias_productos - SOLO LECTURA"""
    
    def __init__(self, id_inventario: str = "", id_producto: str = "", 
                 existencia: int = 0, costo_venta: Decimal = Decimal(0), 
                 usuario_id: str = None):
        self.id_inventario = id_inventario
        self.id_producto = id_producto
        self.existencia = existencia
        self.costo_venta = costo_venta
        self.usuario_id = usuario_id  # Usuario que realiza la acción
        self.__conexion_bd = conectar()

    def _conexion(self):
        return self.__conexion_bd.conexion1()

    def listar_inventario(self):
        """Lista todo el inventario con sus relaciones"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    e.ID_inventario AS id_inventario,
                    e.ID_producto AS id_producto,
                    e.Existencia AS existencia,
                    e.Costo_venta AS costo_venta,
                    p.Nombre_producto AS nombre_producto,
                    ma.Nombre_marca AS nombre_marca,
                    cl.Nombre_Clase AS nombre_clase,
                    (SELECT fi.Foto_inventario FROM Fotos_inventario fi 
                     WHERE fi.ID_inventario = e.ID_inventario 
                     ORDER BY fi.ID_foto_inventario DESC LIMIT 1) AS foto_inventario
                FROM Existencias_productos e
                JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                ORDER BY cl.Nombre_Clase, ma.Nombre_marca, p.Nombre_producto
            """)
            rows = cursor.fetchall() or []
            for row in rows:
                if isinstance(row.get("costo_venta"), Decimal):
                    row["costo_venta"] = float(row["costo_venta"])
            return rows
        finally:
            cursor.close()
            db.close()

    def listar_inventario_por_modelo(self, nombre_modelo: str = None):
        """Lista inventario filtrado por modelo"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            if nombre_modelo:
                cursor.execute("""
                    SELECT 
                        e.ID_inventario AS id_inventario,
                        e.ID_producto AS id_producto,
                        e.Existencia AS existencia,
                        e.Costo_venta AS costo_venta,
                        p.Nombre_producto AS nombre_producto,
                        ma.Nombre_marca AS nombre_marca,
                        cl.Nombre_Clase AS nombre_clase,
                        (SELECT fi.Foto_inventario FROM Fotos_inventario fi 
                         WHERE fi.ID_inventario = e.ID_inventario 
                         ORDER BY fi.ID_foto_inventario DESC LIMIT 1) AS foto_inventario
                    FROM Existencias_productos e
                    JOIN Producto p ON e.ID_producto = p.ID_producto
                    LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                    LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                    WHERE p.Nombre_producto LIKE %s
                    ORDER BY cl.Nombre_Clase, ma.Nombre_marca, p.Nombre_producto
                """, (f"%{nombre_modelo}%",))
            else:
                return self.listar_inventario()
            
            rows = cursor.fetchall() or []
            for row in rows:
                if isinstance(row.get("costo_venta"), Decimal):
                    row["costo_venta"] = float(row["costo_venta"])
            return rows
        finally:
            cursor.close()
            db.close()

    def listar_inventario_general(self):
        """Lista inventario general (sin filtros)"""
        return self.listar_inventario()

    def listar_productos_bajo_stock(self, limite: int = 10):
        """Obtiene productos con stock menor o igual al límite"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    e.ID_inventario AS id_inventario,
                    e.ID_producto AS id_producto,
                    e.Existencia AS existencia,
                    e.Costo_venta AS costo_venta,
                    p.Nombre_producto AS nombre_producto,
                    ma.Nombre_marca AS nombre_marca,
                    cl.Nombre_Clase AS nombre_clase,
                    (SELECT fi.Foto_inventario FROM Fotos_inventario fi 
                     WHERE fi.ID_inventario = e.ID_inventario 
                     ORDER BY fi.ID_foto_inventario DESC LIMIT 1) AS foto_inventario
                FROM Existencias_productos e
                JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                WHERE e.Existencia <= %s
                ORDER BY e.Existencia ASC
                LIMIT %s
            """, (limite, limite))
            rows = cursor.fetchall() or []
            for row in rows:
                if isinstance(row.get("costo_venta"), Decimal):
                    row["costo_venta"] = float(row["costo_venta"])
            return rows
        finally:
            cursor.close()
            db.close()

    def listar_productos_sin_stock(self):
        """Obtiene productos con stock igual a 0"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    e.ID_inventario AS id_inventario,
                    e.ID_producto AS id_producto,
                    e.Existencia AS existencia,
                    e.Costo_venta AS costo_venta,
                    p.Nombre_producto AS nombre_producto,
                    ma.Nombre_marca AS nombre_marca,
                    cl.Nombre_Clase AS nombre_clase,
                    (SELECT fi.Foto_inventario FROM Fotos_inventario fi 
                     WHERE fi.ID_inventario = e.ID_inventario 
                     ORDER BY fi.ID_foto_inventario DESC LIMIT 1) AS foto_inventario
                FROM Existencias_productos e
                JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                WHERE e.Existencia = 0
                ORDER BY p.Nombre_producto ASC
                LIMIT 10
            """)
            rows = cursor.fetchall() or []
            for row in rows:
                if isinstance(row.get("costo_venta"), Decimal):
                    row["costo_venta"] = float(row["costo_venta"])
            return rows
        finally:
            cursor.close()
            db.close()

    def aumentar_stock(self, cantidad: int) -> bool:
        """Aumenta el stock del inventario (usado por órdenes de compra)"""
        if not self.id_inventario:
            raise ValueError("ID del inventario es requerido")
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute("""
                UPDATE Existencias_productos 
                SET Existencia = Existencia + %s
                WHERE ID_inventario = %s
            """, (cantidad, self.id_inventario))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            if db:
                db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()


class FotosInventario:
    """Modelo para la tabla Fotos_inventario"""
    
    def __init__(self, id_foto_inventario: str = "", id_inventario: str = "", 
                 foto_inventario: str = "", usuario_id: str = None):
        self.id_foto_inventario = id_foto_inventario
        self.id_inventario = id_inventario
        self.foto_inventario = foto_inventario
        self.usuario_id = usuario_id
        self.__conexion_bd = conectar()

    def _conexion(self):
        return self.__conexion_bd.conexion1()

    def _siguiente_id(self) -> str:
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        cursor = db.cursor()
        try:
            cursor.execute("SELECT COALESCE(MAX(CAST(ID_foto_inventario AS UNSIGNED)), 0) + 1 FROM Fotos_inventario")
            row = cursor.fetchone()
            return str(int(row[0] or 0))
        finally:
            cursor.close()
            db.close()

    def listar_fotos(self):
        if not self.id_inventario:
            return []
        
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT ID_foto_inventario AS id, ID_inventario AS id_inventario, 
                       Foto_inventario AS foto
                FROM Fotos_inventario
                WHERE ID_inventario = %s
                ORDER BY ID_foto_inventario DESC
            """, (self.id_inventario,))
            return cursor.fetchall() or []
        finally:
            cursor.close()
            db.close()

    def registrar_foto(self) -> str:
        if not self.id_inventario or not self.foto_inventario:
            raise ValueError("ID de inventario y foto son requeridos")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = None
        try:
            cursor = db.cursor()
            self.id_foto_inventario = self._siguiente_id()
            cursor.execute("""
                INSERT INTO Fotos_inventario (ID_foto_inventario, ID_inventario, Foto_inventario)
                VALUES (%s, %s, %s)
            """, (self.id_foto_inventario, self.id_inventario, self.foto_inventario))
            db.commit()
            return self.id_foto_inventario
        except Exception as e:
            if db:
                db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def eliminar_foto(self) -> bool:
        if not self.id_foto_inventario:
            raise ValueError("ID de foto es requerido")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM Fotos_inventario WHERE ID_foto_inventario = %s", (self.id_foto_inventario,))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
            db.close()