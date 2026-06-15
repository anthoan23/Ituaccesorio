from __future__ import annotations
from app.models.database import conectar
from app.models.bitacora import Bitacora
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional
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
    
    def _verificar_cliente_existe(self, cliente_id: str) -> bool:
        """Verifica si el cliente existe en la base de datos"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return False
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM Cliente WHERE ID_cliente = %s LIMIT 1",
                (str(cliente_id),)
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()
    
    def _verificar_stock_disponible(self, inventario_id: str, cantidad: int) -> tuple[bool, int]:
        """Verifica el stock disponible de un producto"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return False, 0
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT Existencia FROM Inventario WHERE ID_inventario = %s",
                (str(inventario_id),)
            )
            row = cursor.fetchone()
            if not row:
                return False, 0
            
            stock = int(row[0] or 0)
            return stock >= cantidad, stock
        finally:
            cursor.close()
            db.close()
    
    def _verificar_producto_existe(self, inventario_id: str) -> bool:
        """Verifica si un producto existe en el inventario"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return False
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM Inventario WHERE ID_inventario = %s LIMIT 1",
                (str(inventario_id),)
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()
    
    def crear_venta_desde_carrito(self) -> str:
        """Crea una venta a partir del carrito de compras"""
        if not self.cliente_id or not str(self.cliente_id).strip():
            raise ValueError("El ID del cliente no puede estar vacío.")
        
        cliente_id_str = str(self.cliente_id).strip()
        
        if not cliente_id_str.isdigit():
            raise ValueError("El ID del cliente debe contener solo números.")
        
        if len(cliente_id_str) > 8:
            raise ValueError("El ID del cliente no puede exceder los 8 caracteres.")
        
        # Validar items
        if not self.items:
            raise ValueError("El carrito no puede estar vacío.")
        
        if not isinstance(self.items, list):
            raise ValueError("Los items deben ser una lista.")
        
        productos_vistos = set()
        
        for i, item in enumerate(self.items):
            producto_id = item.get("producto_id") or item.get("id")
            
            if not producto_id:
                raise ValueError(f"El producto en la posición {i+1} no tiene ID.")
            
            producto_id_str = str(producto_id).strip()
            
            if not producto_id_str:
                raise ValueError(f"El ID del producto en la posición {i+1} está vacío.")
            
            cantidad = item.get("cantidad", 0)
            
            try:
                cantidad_int = int(cantidad)
                if cantidad_int <= 0:
                    raise ValueError(f"La cantidad del producto '{producto_id_str}' debe ser mayor a 0.")
            except (ValueError, TypeError):
                raise ValueError(f"La cantidad del producto '{producto_id_str}' no es válida.")
            
            if producto_id_str in productos_vistos:
                raise ValueError(f"El producto '{producto_id_str}' aparece múltiples veces en el carrito.")
            productos_vistos.add(producto_id_str)
        
        if not self.metodo_pago or not self.metodo_pago.strip():
            raise ValueError("El método de pago no puede estar vacío.")
        
        metodos_validos = ["pago_movil", "zelle", "binance", "efectivo_usd", "efectivo_bs"]
        if self.metodo_pago not in metodos_validos:
            raise ValueError(f"Método de pago inválido. Opciones: {', '.join(metodos_validos)}.")
        
        # Verificar existencia del cliente
        if not self._verificar_cliente_existe(cliente_id_str):
            raise ValueError(f"El cliente con ID '{cliente_id_str}' no existe.")
        
        db = self.__conexion_bd.conexion1()
        if not db:
            raise RuntimeError("Error al conectar a la base de datos.")
        
        factura_id = self._generar_id_factura()
        fecha_actual = datetime.now()
        moneda = self._obtener_moneda_segun_metodo()
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO Venta (ID_factura, ID_empleado, ID_cliente, Moneda, Fecha_venta)
                VALUES (%s, %s, %s, %s, %s)
            """, (factura_id, self.empleado_id, cliente_id_str, moneda, fecha_actual))
            
            for item in self.items:
                inventario_id = str(item.get("producto_id", item.get("id", "")))
                cantidad = int(item.get("cantidad", 0))
                
                # Verificar stock
                stock_valido, stock_disponible = self._verificar_stock_disponible(inventario_id, cantidad)
                if not stock_valido:
                    raise ValueError(f"Stock insuficiente para el producto {inventario_id}. Disponible: {stock_disponible}")
                
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
                    descripcion=f"Se creó la venta {factura_id} para cliente: {cliente_id_str} - Método: {self.metodo_pago}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Ventas"
                )
                bitacora.registrar()
            
            self.factura_id = factura_id
            return factura_id
            
        except Exception as e:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
    
    def guardar_registro_pago(self) -> None:
        """Guarda el registro de pago de una venta"""
        if not self.factura_id or not self.factura_id.strip():
            raise ValueError("El ID de la factura no puede estar vacío.")
        
        if not self.metodo_pago or not self.metodo_pago.strip():
            raise ValueError("El método de pago no puede estar vacío.")
        
        metodos_validos = ["pago_movil", "zelle", "binance", "efectivo_usd", "efectivo_bs"]
        if self.metodo_pago not in metodos_validos:
            raise ValueError(f"Método de pago inválido. Opciones: {', '.join(metodos_validos)}.")
        
        db = self.__conexion_bd.conexion1()
        if not db:
            raise RuntimeError("Error al conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            fecha_actual = datetime.now()
            moneda = self._obtener_moneda_segun_metodo()
            
            referencia = self.datos_pago.get("referencia", "")
            monto = self.datos_pago.get("monto", None)
            capture_image = self.datos_pago.get("capture", "")
            fecha_pago_cliente = self.datos_pago.get("fecha_pago", None)
            
            # Validar monto si está presente
            if monto is not None:
                try:
                    monto_float = float(monto)
                    if monto_float <= 0:
                        raise ValueError("El monto debe ser mayor a 0.")
                except (ValueError, TypeError):
                    raise ValueError("El monto debe ser un valor numérico válido.")
            
            # Validar referencia para ciertos métodos
            if self.metodo_pago in ["pago_movil", "zelle", "binance"] and not referencia:
                raise ValueError(f"La referencia es obligatoria para el método de pago '{self.metodo_pago}'.")
            
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
            
            if "Referencia" in columnas and referencia:
                campos.append("Referencia")
                valores.append(referencia)
            
            if "Monto" in columnas and monto is not None:
                campos.append("Monto")
                valores.append(monto)
            
            if "Capture" in columnas and capture_image:
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
                    descripcion=f"Se registró pago para factura: {self.factura_id} - Método: {self.metodo_pago}",
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
        """Obtiene el resumen de ventas del día"""
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