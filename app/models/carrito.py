from __future__ import annotations
from app.models.database import conectar
from decimal import Decimal
from typing import List, Dict, Any

class CarritoModel:
    """Modelo para operaciones del carrito de compras"""
    
    _ESTADO_CARRITO = "carrito"
    
    def __init__(self):
        self.__conexion_bd = conectar()
    
    def _generar_id_lista_compra(self) -> str:
        db = self.__conexion_bd.conexion1()
        if not db:
            return "LST0000001"
        
        cursor = db.cursor()
        try:
            cursor.execute("SELECT MAX(ID_lista_compra) FROM Lista_compra")
            row = cursor.fetchone()
            ultimo_id = row[0] if row else None
            
            if ultimo_id:
                num = int(ultimo_id[3:]) + 1
            else:
                num = 1
            
            return f"LST{num:07d}"
        finally:
            cursor.close()
            db.close()
    
    def obtener_carrito(self, cliente_id: str) -> List[Dict[str, Any]]:
        db = self.__conexion_bd.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    lc.ID_lista_compra AS id,
                    lc.ID_inventario AS producto_id,
                    lc.Cantidad_producto AS cantidad,
                    i.Costo_venta AS precio_usd,
                    p.Nombre_producto AS nombre,
                    COALESCE(ma.Nombre_marca, '') AS marca,
                    i.Existencia AS stock_disponible
                FROM Lista_compra lc
                JOIN Inventario i ON lc.ID_inventario = i.ID_inventario
                JOIN Producto p ON i.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                WHERE lc.ID_cliente = %s
                  AND (lc.Estado_lista_compra IS NULL OR lc.Estado_lista_compra = %s)
            """, (cliente_id, self._ESTADO_CARRITO))
            
            rows = cursor.fetchall()
            for r in rows:
                if isinstance(r.get("precio_usd"), Decimal):
                    r["precio_usd"] = float(r["precio_usd"])
            return rows
        finally:
            cursor.close()
            db.close()
    
    def agregar_al_carrito(self, cliente_id: str, inventario_id: str, cantidad: int) -> None:
        db = self.__conexion_bd.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos")
        
        cursor = db.cursor()
        try:
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor que 0")
            
            cursor.execute(
                "SELECT Existencia FROM Inventario WHERE ID_inventario = %s",
                (inventario_id,)
            )
            stock_row = cursor.fetchone()
            if not stock_row:
                raise ValueError("Producto no encontrado en inventario")
            
            stock = int(stock_row[0] or 0)
            if stock <= 0:
                raise ValueError("Producto sin stock")
            
            cursor.execute("""
                SELECT ID_lista_compra, Cantidad_producto
                FROM Lista_compra
                WHERE ID_cliente = %s AND ID_inventario = %s
                  AND (Estado_lista_compra IS NULL OR Estado_lista_compra = %s)
                LIMIT 1
            """, (cliente_id, inventario_id, self._ESTADO_CARRITO))
            
            existente = cursor.fetchone()
            
            if existente:
                nueva_cantidad = int(existente[1] or 0) + cantidad
                if nueva_cantidad > stock:
                    raise ValueError("La cantidad supera el stock disponible")
                cursor.execute(
                    "UPDATE Lista_compra SET Cantidad_producto = %s WHERE ID_lista_compra = %s",
                    (nueva_cantidad, existente[0])
                )
            else:
                if cantidad > stock:
                    raise ValueError("La cantidad supera el stock disponible")
                
                nuevo_id = self._generar_id_lista_compra()
                cursor.execute("""
                    INSERT INTO Lista_compra (ID_lista_compra, ID_inventario, ID_cliente, Cantidad_producto, Estado_lista_compra)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nuevo_id, inventario_id, cliente_id, cantidad, self._ESTADO_CARRITO))
            
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
    
    def actualizar_cantidad(self, cliente_id: str, inventario_id: str, cantidad: int) -> None:
        if cantidad <= 0:
            self.eliminar_item(cliente_id, inventario_id)
            return
        
        db = self.__conexion_bd.conexion1()
        if not db:
            return
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT Existencia FROM Inventario WHERE ID_inventario = %s",
                (inventario_id,)
            )
            row = cursor.fetchone()
            stock = int(row[0] or 0) if row else 0
            if cantidad > stock:
                raise ValueError("La cantidad supera el stock disponible")
            
            cursor.execute("""
                UPDATE Lista_compra
                SET Cantidad_producto = %s
                WHERE ID_cliente = %s AND ID_inventario = %s
                  AND (Estado_lista_compra IS NULL OR Estado_lista_compra = %s)
            """, (cantidad, cliente_id, inventario_id, self._ESTADO_CARRITO))
            
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
    
    def eliminar_item(self, cliente_id: str, inventario_id: str) -> None:
        db = self.__conexion_bd.conexion1()
        if not db:
            return
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                DELETE FROM Lista_compra
                WHERE ID_cliente = %s AND ID_inventario = %s
                  AND (Estado_lista_compra IS NULL OR Estado_lista_compra = %s)
            """, (cliente_id, inventario_id, self._ESTADO_CARRITO))
            db.commit()
        except Exception:
            db.rollback()
        finally:
            cursor.close()
            db.close()
    
    def vaciar_carrito(self, cliente_id: str) -> None:
        db = self.__conexion_bd.conexion1()
        if not db:
            return
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                DELETE FROM Lista_compra
                WHERE ID_cliente = %s
                  AND (Estado_lista_compra IS NULL OR Estado_lista_compra = %s)
            """, (cliente_id, self._ESTADO_CARRITO))
            db.commit()
        except Exception:
            db.rollback()
        finally:
            cursor.close()
            db.close()