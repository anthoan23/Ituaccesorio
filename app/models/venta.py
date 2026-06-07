from __future__ import annotations
from app.models.database import conectar
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
import uuid

class VentaModel:
    """Modelo para operaciones de ventas y facturación"""
    
    def __init__(self):
        self.__conexion_bd = conectar()
    
    def _generar_id_factura(self) -> str:
        fecha = datetime.now().strftime("%Y-%m")
        random_part = str(uuid.uuid4().hex[:6]).upper()
        return f"FAC-{fecha}-{random_part}"
    
    def _obtener_moneda_segun_metodo(self, metodo_pago: str) -> str:
        if metodo_pago in ("pago_movil", "efectivo_bs"):
            return "VES"
        elif metodo_pago == "binance":
            return "USDT"
        else:
            return "USD"
    
    def crear_venta_desde_carrito(
        self,
        cliente_id: str,
        items: List[Dict[str, Any]],
        metodo_pago: str,
        estado_pago: str = "Pendiente"
    ) -> str:
        db = self.__conexion_bd.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos")
        
        factura_id = self._generar_id_factura()
        fecha_actual = datetime.now()
        moneda = self._obtener_moneda_segun_metodo(metodo_pago)
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO Venta (ID_factura, ID_empleado, ID_cliente, Moneda, Fecha_venta)
                VALUES (%s, %s, %s, %s, %s)
            """, (factura_id, None, cliente_id, moneda, fecha_actual))
            
            for item in items:
                inventario_id = item["producto_id"]
                cantidad = int(item["cantidad"])
                
                if cantidad <= 0:
                    continue
                
                cursor.execute(
                    "SELECT Existencia FROM Inventario WHERE ID_inventario = %s",
                    (inventario_id,)
                )
                row = cursor.fetchone()
                existencia = int(row[0] or 0) if row else 0
                
                if existencia < cantidad:
                    raise ValueError(f"Stock insuficiente para el producto {inventario_id}")
                
                cursor.execute("""
                    INSERT INTO Detalle_venta (ID_inventario, ID_factura, Cantidad_articulo)
                    VALUES (%s, %s, %s)
                """, (inventario_id, factura_id, cantidad))
                
                cursor.execute("""
                    UPDATE Inventario 
                    SET Existencia = Existencia - %s 
                    WHERE ID_inventario = %s
                """, (cantidad, inventario_id))
            
            db.commit()
            return factura_id
            
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
    
    def crear_venta_local(
        self,
        cliente_id: str,
        empleado_id: str,
        items: List[Dict[str, Any]],
        metodo_pago: str
    ) -> str:
        db = self.__conexion_bd.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos")
        
        factura_id = self._generar_id_factura()
        fecha_actual = datetime.now()
        moneda = self._obtener_moneda_segun_metodo(metodo_pago)
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO Venta (ID_factura, ID_empleado, ID_cliente, Moneda, Fecha_venta)
                VALUES (%s, %s, %s, %s, %s)
            """, (factura_id, empleado_id, cliente_id, moneda, fecha_actual))
            
            for item in items:
                inventario_id = item["producto_id"]
                cantidad = int(item["cantidad"])
                
                if cantidad <= 0:
                    continue
                
                cursor.execute(
                    "SELECT Existencia FROM Inventario WHERE ID_inventario = %s",
                    (inventario_id,)
                )
                row = cursor.fetchone()
                existencia = int(row[0] or 0) if row else 0
                
                if existencia < cantidad:
                    raise ValueError(f"Stock insuficiente para el producto {inventario_id}")
                
                cursor.execute("""
                    INSERT INTO Detalle_venta (ID_inventario, ID_factura, Cantidad_articulo)
                    VALUES (%s, %s, %s)
                """, (inventario_id, factura_id, cantidad))
                
                cursor.execute("""
                    UPDATE Inventario 
                    SET Existencia = Existencia - %s 
                    WHERE ID_inventario = %s
                """, (cantidad, inventario_id))
            
            db.commit()
            return factura_id
            
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
    
    def guardar_registro_pago(self, factura_id: str, metodo_pago: str, datos_pago: Dict[str, Any]) -> None:
        db = self.__conexion_bd.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos")
        
        cursor = db.cursor()
        try:
            fecha_actual = datetime.now()
            moneda = self._obtener_moneda_segun_metodo(metodo_pago)
            
            import json
            capture_data = {
                "metodo": metodo_pago,
                "datos": datos_pago,
                "fecha_registro": fecha_actual.isoformat()
            }
            capture_str = json.dumps(capture_data, ensure_ascii=False)[:255]
            
            cursor.execute("""
                INSERT INTO Metodo_pago (ID_factura, Moneda, Fecha_pago, Capture)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    Moneda = VALUES(Moneda),
                    Fecha_pago = VALUES(Fecha_pago),
                    Capture = VALUES(Capture)
            """, (factura_id, moneda, fecha_actual, capture_str))
            
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()