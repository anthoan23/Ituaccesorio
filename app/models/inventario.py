from __future__ import annotations
from decimal import Decimal
from app.models.database import conectar


class Inventario:
    """Modelo para la tabla Existencias_productos"""
    
    def __init__(self, id_inventario: str = "", id_producto: str = "", 
                 existencia: int = 0, costo_venta: Decimal = Decimal(0), 
                 usuario_id: str = None):
        self.id_inventario = id_inventario
        self.id_producto = id_producto
        self.existencia = existencia
        self.costo_venta = costo_venta
        self.usuario_id = usuario_id
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
        if not nombre_modelo:
            return self.listar_inventario()
        
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
                WHERE p.Nombre_producto LIKE %s
                ORDER BY cl.Nombre_Clase, ma.Nombre_marca, p.Nombre_producto
            """, (f"%{nombre_modelo}%",))
            
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

    # ============================================
    # FUNCIONES PARA EL TALLER (MANTENER)
    # ============================================
    
    def listar_inventario_taller(self):
        """Lista inventario para el módulo de taller (categoría 2)"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    e.ID_inventario,
                    p.Nombre_producto,
                    m.Nombre_marca,
                    c.Nombre_Clase,
                    e.Existencia,
                    e.Costo_venta 
                FROM Existencias_productos e
                JOIN Producto p ON e.ID_producto = p.ID_producto
                JOIN Clase_producto c ON p.ID_Clase = c.ID_Clase
                JOIN Marca_producto m ON p.ID_marca = m.ID_marca
                WHERE e.ID_categoria = 2
                ORDER BY c.Nombre_Clase, m.Nombre_marca, p.Nombre_producto
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()