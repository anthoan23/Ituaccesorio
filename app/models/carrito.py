from __future__ import annotations
from app.models.database import conectar
from app.models.bitacora import Bitacora
from decimal import Decimal
from typing import List, Dict, Any


class CarritoModel:
    """Modelo para operaciones del carrito de compras"""
    
    _ESTADO_CARRITO = "carrito"
    
    def __init__(self, cliente_id: str = None, inventario_id: str = None, 
                 cantidad: int = 0, usuario_id: str = None):
        self.cliente_id = cliente_id
        self.inventario_id = inventario_id
        self.cantidad = cantidad
        self.usuario_id = usuario_id
        self.__conexion_bd = conectar()
    
    def _generar_id_lista_compra(self) -> str:
        """Genera un ID único para la lista de compra"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return "LST0000001"
        
        cursor = db.cursor()
        try:
            # Obtener el último ID numérico
            cursor.execute("""
                SELECT ID_lista_compra FROM Lista_compra 
                ORDER BY CAST(SUBSTRING(ID_lista_compra, 4) AS UNSIGNED) DESC 
                LIMIT 1
            """)
            row = cursor.fetchone()
            
            if row and row[0] and row[0].startswith('LST'):
                # Extraer el número y sumar 1
                num = int(row[0][3:]) + 1
            else:
                num = 1
            
            nuevo_id = f"LST{num:07d}"
            
            # Verificar que el ID no exista (por si acaso)
            cursor.execute("SELECT 1 FROM Lista_compra WHERE ID_lista_compra = %s", (nuevo_id,))
            if cursor.fetchone():
                # Si existe, seguir incrementando hasta encontrar uno libre
                while True:
                    num += 1
                    nuevo_id = f"LST{num:07d}"
                    cursor.execute("SELECT 1 FROM Lista_compra WHERE ID_lista_compra = %s", (nuevo_id,))
                    if not cursor.fetchone():
                        break
            
            return nuevo_id
        except Exception as e:
            print(f"Error generando ID: {e}")
            # Fallback: usar timestamp + random
            import time
            import random
            return f"LST{int(time.time())}{random.randint(10, 99)}"
        finally:
            cursor.close()
            db.close()
    
    def obtener_carrito(self) -> List[Dict[str, Any]]:
        if not self.cliente_id:
            return []
        
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
                    e.Costo_venta AS precio_usd,
                    p.Nombre_producto AS nombre,
                    COALESCE(ma.Nombre_marca, '') AS marca,
                    e.Existencia AS stock_disponible,
                    COALESCE((
                        SELECT fi.Foto_inventario
                        FROM Fotos_inventario fi
                        WHERE fi.ID_inventario = e.ID_inventario
                        ORDER BY fi.ID_foto_inventario DESC
                        LIMIT 1
                    ), '') AS imagen
                FROM Lista_compra lc
                JOIN Existencias_productos e ON lc.ID_inventario = e.ID_inventario
                JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                WHERE lc.ID_cliente = %s
                  AND (lc.Estado_lista_compra IS NULL OR lc.Estado_lista_compra = %s)
            """, (self.cliente_id, self._ESTADO_CARRITO))
            
            rows = cursor.fetchall()
            for r in rows:
                if isinstance(r.get("precio_usd"), Decimal):
                    r["precio_usd"] = float(r["precio_usd"])
            return rows
        finally:
            cursor.close()
            db.close()
    
    def agregar_al_carrito(self) -> None:
        if not self.cliente_id or not self.inventario_id:
            raise ValueError("Cliente y producto son obligatorios")
        
        if self.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que 0")
        
        db = self.__conexion_bd.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos")
        
        cursor = db.cursor()
        try:
            # Verificar stock
            cursor.execute(
                "SELECT Existencia FROM Existencias_productos WHERE ID_inventario = %s",
                (self.inventario_id,)
            )
            stock_row = cursor.fetchone()
            if not stock_row:
                raise ValueError("Producto no encontrado en inventario")
            
            stock = int(stock_row[0] or 0)
            if stock <= 0:
                raise ValueError("Producto sin stock")
            
            # Verificar si el producto ya está en el carrito
            cursor.execute("""
                SELECT ID_lista_compra, Cantidad_producto
                FROM Lista_compra
                WHERE ID_cliente = %s AND ID_inventario = %s
                  AND (Estado_lista_compra IS NULL OR Estado_lista_compra = %s)
                LIMIT 1
            """, (self.cliente_id, self.inventario_id, self._ESTADO_CARRITO))
            
            existente = cursor.fetchone()
            
            if existente:
                # Actualizar cantidad existente
                nueva_cantidad = int(existente[1] or 0) + self.cantidad
                if nueva_cantidad > stock:
                    raise ValueError("La cantidad supera el stock disponible")
                cursor.execute(
                    "UPDATE Lista_compra SET Cantidad_producto = %s WHERE ID_lista_compra = %s",
                    (nueva_cantidad, existente[0])
                )
            else:
                # Agregar nuevo producto al carrito
                if self.cantidad > stock:
                    raise ValueError("La cantidad supera el stock disponible")
                
                nuevo_id = self._generar_id_lista_compra()
                cursor.execute("""
                    INSERT INTO Lista_compra (ID_lista_compra, ID_inventario, ID_cliente, Cantidad_producto, Estado_lista_compra)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nuevo_id, self.inventario_id, self.cliente_id, self.cantidad, self._ESTADO_CARRITO))
            
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Agregar al carrito",
                    descripcion=f"Cliente ID: {self.cliente_id} agregó producto ID: {self.inventario_id} - Cantidad: {self.cantidad}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Carrito"
                )
                bitacora.registrar()
            
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
    
    def actualizar_cantidad(self) -> None:
        if not self.cliente_id or not self.inventario_id:
            return
        
        if self.cantidad <= 0:
            self.eliminar_item()
            return
        
        db = self.__conexion_bd.conexion1()
        if not db:
            return
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT Existencia FROM Existencias_productos WHERE ID_inventario = %s",
                (self.inventario_id,)
            )
            row = cursor.fetchone()
            stock = int(row[0] or 0) if row else 0
            if self.cantidad > stock:
                raise ValueError("La cantidad supera el stock disponible")
            
            cursor.execute("""
                UPDATE Lista_compra
                SET Cantidad_producto = %s
                WHERE ID_cliente = %s AND ID_inventario = %s
                  AND (Estado_lista_compra IS NULL OR Estado_lista_compra = %s)
            """, (self.cantidad, self.cliente_id, self.inventario_id, self._ESTADO_CARRITO))
            
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
    
    def eliminar_item(self) -> None:
        if not self.cliente_id or not self.inventario_id:
            return
        
        db = self.__conexion_bd.conexion1()
        if not db:
            return
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                DELETE FROM Lista_compra
                WHERE ID_cliente = %s AND ID_inventario = %s
                  AND (Estado_lista_compra IS NULL OR Estado_lista_compra = %s)
            """, (self.cliente_id, self.inventario_id, self._ESTADO_CARRITO))
            db.commit()
        except Exception:
            db.rollback()
        finally:
            cursor.close()
            db.close()
    
    def vaciar_carrito(self) -> None:
        if not self.cliente_id:
            return
        
        db = self.__conexion_bd.conexion1()
        if not db:
            return
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                DELETE FROM Lista_compra
                WHERE ID_cliente = %s
                  AND (Estado_lista_compra IS NULL OR Estado_lista_compra = %s)
            """, (self.cliente_id, self._ESTADO_CARRITO))
            db.commit()
        except Exception:
            db.rollback()
        finally:
            cursor.close()
            db.close()