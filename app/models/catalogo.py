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
        """Lista productos del catálogo con filtros opcionales"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            where = ["e.Existencia > 0"]
            params = []
            
            if self.clase_id:
                clase_id_str = str(self.clase_id).strip()
                if clase_id_str:
                    where.append("p.ID_Clase = %s")
                    params.append(clase_id_str)
            
            if self.marca_id:
                marca_id_str = str(self.marca_id).strip()
                if marca_id_str:
                    where.append("p.ID_marca = %s")
                    params.append(marca_id_str)
            
            if self.q:
                q_str = str(self.q).strip()
                if q_str:
                    if len(q_str) < 2:
                        pass  
                    elif len(q_str) > 100:
                        pass  
                    else:
                        # Escapar caracteres especiales para LIKE
                        termino_seguro = q_str.replace('%', '\\%').replace('_', '\\_')
                        where.append("(p.Nombre_producto LIKE %s OR ma.Nombre_marca LIKE %s)")
                        params.append(f"%{termino_seguro}%")
                        params.append(f"%{termino_seguro}%")
            
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
        except Exception as e:
            print(f"Error en listar_productos_catalogo: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def obtener_producto(self) -> Optional[Dict[str, Any]]:
        """Obtiene un producto específico por su inventario_id"""
        if not self.inventario_id:
            return None
        
        inventario_id_str = str(self.inventario_id).strip()
        
        if not inventario_id_str:
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
            """, (inventario_id_str,))
            
            row = cursor.fetchone()
            if row and isinstance(row.get("precio_usd"), Decimal):
                row["precio_usd"] = float(row["precio_usd"])
            return row
        finally:
            cursor.close()
            db.close()
    
    def listar_clases(self) -> List[Dict[str, Any]]:
        """Lista todas las clases de productos disponibles"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT ID_Clase AS id, Nombre_Clase AS nombre 
                FROM Clase_producto 
                WHERE ID_Clase IS NOT NULL
                ORDER BY Nombre_Clase
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()
    
    def listar_marcas(self) -> List[Dict[str, Any]]:
        """Lista todas las marcas de productos disponibles"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT ID_marca AS id, Nombre_marca AS nombre 
                FROM Marca_producto 
                WHERE ID_marca IS NOT NULL
                ORDER BY Nombre_marca
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()
    
    def productos_mas_vendidos(self, limite: int = 5) -> List[Dict[str, Any]]:
        """Obtiene los productos más vendidos"""
        # Validación estilo cargo
        try:
            limite_int = int(limite)
            if limite_int <= 0:
                limite_int = 5
            if limite_int > 50:
                limite_int = 50
        except (ValueError, TypeError):
            limite_int = 5
        
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
            """, (limite_int,))
            
            rows = cursor.fetchall()
            for r in rows:
                if isinstance(r.get("precio_usd"), Decimal):
                    r["precio_usd"] = float(r["precio_usd"])
            return rows
        finally:
            cursor.close()
            db.close()