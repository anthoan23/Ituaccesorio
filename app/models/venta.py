from __future__ import annotations
from app.models.database import conectar
from app.models.bitacora import Bitacora
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
import uuid


class VentaModel:
    """Modelo para operaciones de ventas y facturación"""
    
    def __init__(self, factura_id: str = None, cliente_id: str = None, 
                 empleado_id: str = None, items: List[Dict[str, Any]] = None,
                 metodo_pago: str = None, estado_pago: str = "Pendiente",
                 datos_pago: Dict[str, Any] = None, usuario_id: str = None):
        self.factura_id = factura_id
        self.cliente_id = cliente_id
        self.empleado_id = empleado_id
        self.items = items or []
        self.metodo_pago = metodo_pago
        self.estado_pago = estado_pago
        self.datos_pago = datos_pago or {}
        self.usuario_id = usuario_id
        self.__conexion_bd = conectar()
    
    def _generar_id_factura(self) -> str:
        fecha = datetime.now().strftime("%Y%m")
        random_part = str(uuid.uuid4().hex[:6]).upper()
        return f"FAC-{fecha}-{random_part}"
    
    def _obtener_moneda_segun_metodo(self) -> str:
        if self.metodo_pago in ("pago_movil", "efectivo_bs"):
            return "VES"
        elif self.metodo_pago == "binance":
            return "USDT"
        else:
            return "USD"
    
    def crear_venta_desde_carrito(self) -> str:
        if not self.cliente_id:
            raise ValueError("Cliente no especificado")
        
        db = self.__conexion_bd.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos")
        
        factura_id = self._generar_id_factura()
        fecha_actual = datetime.now()
        moneda = self._obtener_moneda_segun_metodo()
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO Venta (ID_factura, ID_empleado, ID_cliente, Moneda, Fecha_venta)
                VALUES (%s, %s, %s, %s, %s)
            """, (factura_id, None, self.cliente_id, moneda, fecha_actual))
            
            for item in self.items:
                inventario_id = str(item.get("producto_id", item.get("id", "")))
                cantidad = int(item.get("cantidad", 0))
                
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
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Crear venta",
                    descripcion=f"Se creó la venta {factura_id} para cliente: {self.cliente_id} - Método: {self.metodo_pago}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Ventas"
                )
                bitacora.registrar()
            
            self.factura_id = factura_id
            return factura_id
            
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
    
    def guardar_registro_pago(self) -> None:
        if not self.factura_id:
            raise ValueError("Factura ID no especificada")
        
        db = self.__conexion_bd.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos")
        
        cursor = db.cursor()
        try:
            fecha_actual = datetime.now()
            moneda = self._obtener_moneda_segun_metodo()
            
            referencia = self.datos_pago.get("referencia", "")
            monto = self.datos_pago.get("monto", None)
            capture_image = self.datos_pago.get("capture", "")
            fecha_pago_cliente = self.datos_pago.get("fecha_pago", None)
            
            fecha_pago = fecha_pago_cliente if fecha_pago_cliente else fecha_actual
            
            cursor.execute("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'Metodo_pago' AND TABLE_SCHEMA = DATABASE()
            """)
            columnas = [row[0] for row in cursor.fetchall()]
            
            campos = ["ID_factura", "Moneda", "Fecha_pago"]
            valores = [self.factura_id, moneda, fecha_pago]
            
            if "Metodo" in columnas:
                campos.append("Metodo")
                valores.append(self.metodo_pago)
            
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
                valores.append(self.estado_pago)
            
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
            
            cursor.execute(query, valores)
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Registrar pago",
                    descripcion=f"Se registró pago para factura: {self.factura_id} - Método: {self.metodo_pago} - Referencia: {referencia}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Ventas"
                )
                bitacora.registrar()
            
        except Exception as e:
            db.rollback()
            print(f"Error en guardar_registro_pago: {e}")
            raise
        finally:
            cursor.close()
            db.close()
    
    def obtener_ventas_hoy(self) -> dict:
        db = self.__conexion_bd.conexion1()
        if not db:
            return {"total_ventas": 0, "cantidad_ventas": 0, "moneda": "USD"}
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as cantidad_ventas,
                    COALESCE(SUM(v.Monto), 0) as total_ventas,
                    v.Moneda
                FROM Venta v
                WHERE DATE(v.Fecha_venta) = CURDATE()
                GROUP BY v.Moneda
                ORDER BY v.Moneda DESC
                LIMIT 1
            """)
            resultado = cursor.fetchone()
            
            if resultado:
                return {
                    "total_ventas": float(resultado.get("total_ventas", 0)),
                    "cantidad_ventas": resultado.get("cantidad_ventas", 0),
                    "moneda": resultado.get("Moneda", "USD")
                }
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as cantidad_ventas,
                    COALESCE(SUM(mp.Monto), 0) as total_ventas,
                    mp.Moneda
                FROM Metodo_pago mp
                WHERE DATE(mp.Fecha_pago) = CURDATE()
                GROUP BY mp.Moneda
                ORDER BY mp.Moneda DESC
                LIMIT 1
            """)
            resultado = cursor.fetchone()
            
            if resultado:
                return {
                    "total_ventas": float(resultado.get("total_ventas", 0)),
                    "cantidad_ventas": resultado.get("cantidad_ventas", 0),
                    "moneda": resultado.get("Moneda", "USD")
                }
            
            return {"total_ventas": 0, "cantidad_ventas": 0, "moneda": "USD"}
        except Exception as e:
            print(f"Error en obtener_ventas_hoy: {e}")
            return {"total_ventas": 0, "cantidad_ventas": 0, "moneda": "USD"}
        finally:
            cursor.close()
            db.close()