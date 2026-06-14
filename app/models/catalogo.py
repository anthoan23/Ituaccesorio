from __future__ import annotations
from app.models.database import conectar
from decimal import Decimal
from typing import Optional, List, Dict, Any


class CatalogoModel:
    """Modelo para operaciones del catálogo de productos (solo lectura)"""
    
    def __init__(self, inventario_id: str = None, producto_id: str = None,
                 clase_id: str = None, marca_id: str = None, q: str = None):
        self.inventario_id = inventario_id
        self.producto_id = producto_id
        self.clase_id = clase_id
        self.marca_id = marca_id
        self.q = q
        self.__conexion_bd = conectar()
    
    def listar_productos_catalogo(self) -> List[Dict[str, Any]]:
        db = self.__conexion_bd.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            where = ["e.Existencia > 0"]
            params = []
            
            if self.clase_id:
                where.append("p.ID_Clase = %s")
                params.append(self.clase_id)
            if self.marca_id:
                where.append("p.ID_marca = %s")
                params.append(self.marca_id)
            if self.q:
                where.append("(p.Nombre_producto LIKE %s OR ma.Nombre_marca LIKE %s)")
                params.append(f"%{self.q}%")
                params.append(f"%{self.q}%")
            
            where_sql = " AND ".join(where)
            
            query = f"""
                SELECT
                    e.ID_inventario AS id,
                    p.Nombre_producto AS nombre,
                    COALESCE(ma.Nombre_marca, '') AS marca,
                    COALESCE(cl.Nombre_Clase, '') AS clase,
                    e.Costo_venta AS precio_usd,
                    e.Existencia AS stock,
                    COALESCE((
                        SELECT fi.Foto_inventario
                        FROM Fotos_inventario fi
                        WHERE fi.ID_inventario = e.ID_inventario
                        ORDER BY fi.ID_foto_inventario DESC
                        LIMIT 1
                    ), '') AS imagen,
                    p.ID_producto AS id_producto,
                    p.ID_marca AS id_marca,
                    p.ID_Clase AS id_clase,
                    COALESCE((
                        SELECT SUM(dv.Cantidad_articulo)
                        FROM Detalle_venta dv
                        WHERE dv.ID_inventario = e.ID_inventario
                    ), 0) AS veces_vendido
                FROM Existencias_productos e
                JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                WHERE {where_sql}
                ORDER BY veces_vendido DESC, cl.Nombre_Clase ASC, ma.Nombre_marca ASC, p.Nombre_producto ASC
            """
            
            cursor.execute(query, tuple(params))
            resultados = cursor.fetchall()
            
            for r in resultados:
                if isinstance(r.get("precio_usd"), Decimal):
                    r["precio_usd"] = float(r["precio_usd"])
            
            return resultados
        finally:
            cursor.close()
            db.close()
    
    def obtener_producto(self) -> Optional[Dict[str, Any]]:
        if not self.inventario_id:
            return None
        
        db = self.__conexion_bd.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    e.ID_inventario AS id,
                    p.Nombre_producto AS nombre,
                    COALESCE(ma.Nombre_marca, '') AS marca,
                    e.Costo_venta AS precio_usd,
                    e.Existencia AS stock
                FROM Existencias_productos e
                JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                WHERE e.ID_inventario = %s
            """, (self.inventario_id,))
            
            row = cursor.fetchone()
            if row and isinstance(row.get("precio_usd"), Decimal):
                row["precio_usd"] = float(row["precio_usd"])
            return row
        finally:
            cursor.close()
            db.close()
    
    def listar_clases(self) -> List[Dict[str, Any]]:
        db = self.__conexion_bd.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT ID_Clase AS id, Nombre_Clase AS nombre FROM Clase_producto ORDER BY Nombre_Clase")
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()
    
    def listar_marcas(self) -> List[Dict[str, Any]]:
        db = self.__conexion_bd.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT ID_marca AS id, Nombre_marca AS nombre FROM Marca_producto ORDER BY Nombre_marca")
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()
    
    def productos_mas_vendidos(self) -> List[Dict[str, Any]]:
        limite = 5
        db = self.__conexion_bd.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    e.ID_inventario AS id,
                    p.Nombre_producto AS nombre,
                    COALESCE(ma.Nombre_marca, '') AS marca,
                    e.Costo_venta AS precio_usd,
                    COALESCE(SUM(dv.Cantidad_articulo), 0) AS veces_vendido
                FROM Existencias_productos e
                JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Detalle_venta dv ON dv.ID_inventario = e.ID_inventario
                GROUP BY e.ID_inventario, p.Nombre_producto, ma.Nombre_marca, e.Costo_venta
                ORDER BY veces_vendido DESC
                LIMIT %s
            """, (limite,))
            
            rows = cursor.fetchall()
            for r in rows:
                if isinstance(r.get("precio_usd"), Decimal):
                    r["precio_usd"] = float(r["precio_usd"])
            return rows
        finally:
            cursor.close()
            db.close()