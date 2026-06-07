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
        fecha = datetime.now().strftime("%Y%m")
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
                inventario_id = str(item["producto_id"])
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
        """Guarda el registro de pago en la tabla Metodo_pago"""
        db = self.__conexion_bd.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos")
        
        cursor = db.cursor()
        try:
            fecha_actual = datetime.now()
            moneda = self._obtener_moneda_segun_metodo(metodo_pago)
            
            # Extraer datos del pago
            referencia = datos_pago.get("referencia", "")
            monto = datos_pago.get("monto", None)
            capture_image = datos_pago.get("capture", "")
            fecha_pago_cliente = datos_pago.get("fecha_pago", None)
            
            # Si el cliente proporcionó fecha, usarla; si no, usar la actual
            fecha_pago = fecha_pago_cliente if fecha_pago_cliente else fecha_actual
            
            print(f"Guardando pago - Factura: {factura_id}")
            print(f"Referencia: {referencia}")
            print(f"Monto: {monto}")
            print(f"Metodo: {metodo_pago}")
            
            # Verificar qué columnas existen en la tabla
            cursor.execute("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'Metodo_pago' AND TABLE_SCHEMA = DATABASE()
            """)
            columnas = [row[0] for row in cursor.fetchall()]
            print(f"Columnas en Metodo_pago: {columnas}")
            
            # Construir consulta con todas las columnas posibles
            campos = ["ID_factura", "Moneda", "Fecha_pago"]
            valores = [factura_id, moneda, fecha_pago]
            
            if "Metodo" in columnas:
                campos.append("Metodo")
                valores.append(metodo_pago)
            
            if "Referencia" in columnas:
                campos.append("Referencia")
                valores.append(referencia)
            
            if "Monto" in columnas and monto:
                campos.append("Monto")
                valores.append(monto)
            
            if "Capture" in columnas:
                campos.append("Capture")
                valores.append(capture_image)
            
            if "Estado_pago" in columnas:
                campos.append("Estado_pago")
                valores.append('pendiente')
            
            placeholders = ", ".join(["%s"] * len(campos))
            query = f"""
                INSERT INTO Metodo_pago ({', '.join(campos)}) 
                VALUES ({placeholders})
                ON DUPLICATE KEY UPDATE
                    Moneda = VALUES(Moneda),
                    Fecha_pago = VALUES(Fecha_pago),
                    Metodo = VALUES(Metodo),
                    Referencia = VALUES(Referencia),
                    Monto = VALUES(Monto),
                    Capture = VALUES(Capture),
                    Estado_pago = COALESCE(Estado_pago, 'pendiente')
            """
            
            print(f"Query: {query}")
            print(f"Valores: {valores}")
            
            cursor.execute(query, valores)
            db.commit()
            print(f"Registro de pago guardado para factura: {factura_id}")
        except Exception as e:
            db.rollback()
            print(f"Error en guardar_registro_pago: {e}")
            raise
        finally:
            cursor.close()
            db.close()