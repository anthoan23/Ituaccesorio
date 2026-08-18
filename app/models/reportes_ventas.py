from __future__ import annotations
from app.models.database import conectar
from app.models.bitacora import Bitacora
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
import uuid


class ReportesVentasModel:
    """Modelo para reportes de ventas y ventas locales"""
    
    def __init__(self, factura_id: str = None, cliente_id: str = None,
                 items: List[Dict[str, Any]] = None, metodo_pago: str = None,
                 empleado_id: str = None, usuario_id: str = None):
        self.factura_id = factura_id
        self.cliente_id = cliente_id
        self.items = items or []
        self.metodo_pago = metodo_pago
        self.empleado_id = empleado_id
        self.usuario_id = usuario_id
        self.__conexion_bd = conectar()
    
    def _conexion(self):
        return self.__conexion_bd.conexion1()
    
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
        db = self._conexion()
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
        db = self._conexion()
        if not db:
            return False, 0
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT Existencia FROM Existencias_productos WHERE ID_inventario = %s",
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
    
    def obtener_reportes_ventas(self, filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene ventas para reportes con filtros avanzados"""
        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error al conectar", "ventas": [], "total": 0}
        
        cursor = db.cursor(dictionary=True)
        try:
            where_conditions = ["1=1"]
            params = []
            
            if filtros.get("q"):
                search = f"%{filtros['q']}%"
                where_conditions.append("(v.ID_factura LIKE %s OR pn.Nombre_cliente LIKE %s OR pn.Apellido_cliente LIKE %s)")
                params.extend([search, search, search])
            
            if filtros.get("estado"):
                where_conditions.append("mp.Estado_pago = %s")
                params.append(filtros["estado"])
            
            if filtros.get("metodo_pago"):
                where_conditions.append("mp.Metodo = %s")
                params.append(filtros["metodo_pago"])
            
            if filtros.get("moneda"):
                where_conditions.append("v.Moneda = %s")
                params.append(filtros["moneda"])
            
            if filtros.get("fecha_desde"):
                where_conditions.append("DATE(v.Fecha_venta) >= %s")
                params.append(filtros["fecha_desde"])
            
            if filtros.get("fecha_hasta"):
                where_conditions.append("DATE(v.Fecha_venta) <= %s")
                params.append(filtros["fecha_hasta"])
            
            if filtros.get("monto_min") is not None:
                where_conditions.append("mp.Monto >= %s")
                params.append(filtros["monto_min"])
            
            if filtros.get("monto_max") is not None:
                where_conditions.append("mp.Monto <= %s")
                params.append(filtros["monto_max"])
            
            where_sql = " AND ".join(where_conditions)
            
            cursor.execute(f"""
                SELECT 
                    v.ID_factura AS factura_id,
                    v.ID_cliente AS cliente_id,
                    v.Moneda AS venta_moneda,
                    v.Fecha_venta AS fecha_venta,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    COALESCE(c.Celular_cliente, '') AS cliente_celular,
                    COALESCE(c.Correo_cliente, '') AS cliente_correo,
                    mp.Fecha_pago,
                    mp.Metodo AS metodo_pago,
                    mp.Referencia,
                    mp.Monto AS monto_pagado,
                    mp.Estado_pago AS estado,
                    mp.Aprobado_por,
                    mp.Fecha_aprobacion,
                    mp.Rechazado_por,
                    mp.Fecha_rechazo,
                    mp.Motivo_rechazo,
                    mp.Capture AS capture_image,
                    CASE 
                        WHEN mp.Referencia LIKE 'LOCAL-%' THEN 'Local'
                        ELSE 'Online'
                    END AS tipo_venta
                FROM Venta v
                INNER JOIN Metodo_pago mp ON v.ID_factura = mp.ID_factura
                LEFT JOIN Persona_natural pn ON v.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente c ON v.ID_cliente = c.ID_cliente
                WHERE {where_sql}
                ORDER BY v.Fecha_venta DESC
            """, tuple(params))
            
            ventas = cursor.fetchall()
            
            total_monto = 0
            pendientes = 0
            aprobados = 0
            rechazados = 0
            locales = 0
            online = 0
            
            for venta in ventas:
                if venta.get("monto_pagado") and isinstance(venta["monto_pagado"], Decimal):
                    venta["monto_pagado"] = float(venta["monto_pagado"])
                total_monto += venta.get("monto_pagado", 0) or 0
                
                estado = venta.get("estado", "")
                if estado == "pendiente":
                    pendientes += 1
                elif estado == "aprobado":
                    aprobados += 1
                elif estado == "rechazado":
                    rechazados += 1
                
                if venta.get("tipo_venta") == "Local":
                    locales += 1
                else:
                    online += 1
            
            return {
                "success": True,
                "ventas": ventas,
                "total": len(ventas),
                "total_monto": total_monto,
                "pendientes": pendientes,
                "aprobados": aprobados,
                "rechazados": rechazados,
                "locales": locales,
                "online": online
            }
        except Exception as e:
            print(f"Error en obtener_reportes_ventas: {e}")
            return {"success": False, "error": str(e), "ventas": [], "total": 0}
        finally:
            cursor.close()
            db.close()
    
    def obtener_detalle_venta_completo(self) -> Dict[str, Any]:
        """Obtiene el detalle completo de una venta incluyendo datos del cliente"""
        if not self.factura_id:
            return {"success": False, "error": "Factura no especificada"}
        
        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error al conectar"}
        
        cursor = db.cursor(dictionary=True)
        try:
            # Información de la venta
            cursor.execute("""
                SELECT 
                    v.ID_factura AS factura_id,
                    v.ID_cliente AS cliente_id,
                    v.Moneda,
                    v.Fecha_venta,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    c.Celular_cliente,
                    c.Correo_cliente,
                    c.Direccion_cliente,
                    mp.Metodo AS metodo_pago,
                    mp.Referencia,
                    mp.Monto AS monto_total,
                    mp.Estado_pago AS estado,
                    mp.Fecha_pago,
                    mp.Capture AS capture_image,
                    mp.Aprobado_por,
                    mp.Fecha_aprobacion,
                    mp.Rechazado_por,
                    mp.Fecha_rechazo,
                    mp.Motivo_rechazo,
                    CASE 
                        WHEN mp.Referencia LIKE 'LOCAL-%' THEN 'Local'
                        ELSE 'Online'
                    END AS tipo_venta
                FROM Venta v
                INNER JOIN Metodo_pago mp ON v.ID_factura = mp.ID_factura
                LEFT JOIN Persona_natural pn ON v.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente c ON v.ID_cliente = c.ID_cliente
                WHERE v.ID_factura = %s
                LIMIT 1
            """, (self.factura_id,))
            
            venta = cursor.fetchone()
            if not venta:
                return {"success": False, "error": "Venta no encontrada"}
            
            # Convertir Decimal a float
            if venta.get("monto_total") and isinstance(venta["monto_total"], Decimal):
                venta["monto_total"] = float(venta["monto_total"])
            
            # Productos de la venta
            cursor.execute("""
                SELECT 
                    dv.ID_inventario,
                    dv.Cantidad_articulo,
                    e.Costo_venta AS precio_unitario,
                    p.Nombre_producto,
                    COALESCE(ma.Nombre_marca, '') AS marca,
                    COALESCE(cl.Nombre_Clase, '') AS clase
                FROM Detalle_venta dv
                JOIN Existencias_productos e ON dv.ID_inventario = e.ID_inventario
                JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                WHERE dv.ID_factura = %s
            """, (self.factura_id,))
            
            productos = cursor.fetchall()
            total_venta = 0
            
            for p in productos:
                if p.get("precio_unitario") and isinstance(p["precio_unitario"], Decimal):
                    p["precio_unitario"] = float(p["precio_unitario"])
                p["subtotal"] = p["precio_unitario"] * p["Cantidad_articulo"]
                total_venta += p["subtotal"]
            
            return {
                "success": True,
                "venta": venta,
                "productos": productos,
                "total_venta": total_venta
            }
        except Exception as e:
            print(f"Error en obtener_detalle_venta_completo: {e}")
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
            db.close()
    
    def obtener_ventas_locales(self, busqueda: str = "", fecha: str = None) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de ventas locales.
        Una venta es local cuando su referencia comienza con 'LOCAL-'
        """
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            where_conditions = ["mp.Referencia LIKE 'LOCAL-%'"]
            params = []
            
            if busqueda:
                search = f"%{busqueda}%"
                where_conditions.append(
                    "(v.ID_factura LIKE %s OR pn.Nombre_cliente LIKE %s OR pn.Apellido_cliente LIKE %s OR mp.Referencia LIKE %s)"
                )
                params.extend([search, search, search, search])
            
            if fecha:
                where_conditions.append("DATE(v.Fecha_venta) = %s")
                params.append(fecha)
            
            where_sql = " AND ".join(where_conditions)
            
            cursor.execute(f"""
                SELECT 
                    v.ID_factura AS factura_id,
                    v.ID_cliente AS cliente_id,
                    v.Moneda,
                    v.Fecha_venta AS fecha_venta,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    COALESCE(cj.Razon_social, '') AS razon_social,
                    mp.Metodo AS metodo_pago,
                    mp.Referencia,
                    mp.Monto AS monto,
                    mp.Estado_pago AS estado,
                    mp.Fecha_pago,
                    'Local' AS tipo_venta
                FROM Venta v
                INNER JOIN Metodo_pago mp ON v.ID_factura = mp.ID_factura
                LEFT JOIN Persona_natural pn ON v.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente_juridico cj ON v.ID_cliente = cj.ID_cliente
                WHERE {where_sql}
                ORDER BY v.Fecha_venta DESC
                LIMIT 100
            """, tuple(params))
            
            ventas = cursor.fetchall()
            for v in ventas:
                if v.get("monto") and isinstance(v["monto"], Decimal):
                    v["monto"] = float(v["monto"])
            
            return ventas
        except Exception as e:
            print(f"Error en obtener_ventas_locales: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def registrar_venta_local(self) -> str:
        """Registra una venta local (en tienda física)"""
        if not self.cliente_id or not str(self.cliente_id).strip():
            raise ValueError("El ID del cliente no puede estar vacío.")
        
        cliente_id_str = str(self.cliente_id).strip()
        
        if not cliente_id_str.isdigit():
            raise ValueError("El ID del cliente debe contener solo números.")
        
        if not self.items:
            raise ValueError("La venta debe tener al menos un producto.")
        
        if not self.metodo_pago:
            raise ValueError("El método de pago es obligatorio.")
        
        if not self._verificar_cliente_existe(cliente_id_str):
            raise ValueError(f"El cliente con ID '{cliente_id_str}' no existe.")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("Error al conectar a la base de datos.")
        
        factura_id = self._generar_id_factura()
        fecha_actual = datetime.now()
        moneda = self._obtener_moneda_segun_metodo()
        
        cursor = db.cursor()
        try:
            # Crear venta
            cursor.execute("""
                INSERT INTO Venta (ID_factura, ID_empleado, ID_cliente, Moneda, Fecha_venta)
                VALUES (%s, %s, %s, %s, %s)
            """, (factura_id, self.empleado_id, cliente_id_str, moneda, fecha_actual))
            
            total_monto = 0
            
            for item in self.items:
                inventario_id = str(item.get("producto_id", ""))
                cantidad = int(item.get("cantidad", 0))
                precio = float(item.get("precio_usd", 0))
                
                if not inventario_id:
                    raise ValueError("Producto sin ID válido")
                
                if cantidad <= 0:
                    raise ValueError(f"Cantidad inválida para producto {inventario_id}")
                
                stock_valido, stock_disponible = self._verificar_stock_disponible(inventario_id, cantidad)
                if not stock_valido:
                    raise ValueError(f"Stock insuficiente para producto {inventario_id}. Disponible: {stock_disponible}")
                
                cursor.execute("""
                    INSERT INTO Detalle_venta (ID_inventario, ID_factura, Cantidad_articulo)
                    VALUES (%s, %s, %s)
                """, (inventario_id, factura_id, cantidad))
                
                cursor.execute("""
                    UPDATE Existencias_productos 
                    SET Existencia = Existencia - %s 
                    WHERE ID_inventario = %s
                """, (cantidad, inventario_id))
                
                total_monto += precio * cantidad
            
            # Registrar pago (ya aprobado porque es local)
            cursor.execute("""
                INSERT INTO Metodo_pago (
                    ID_factura, Moneda, Fecha_pago, Metodo, Referencia, 
                    Monto, Estado_pago, Aprobado_por, Fecha_aprobacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                factura_id, moneda, fecha_actual, self.metodo_pago, 
                f"LOCAL-{factura_id[-6:]}", total_monto, 'aprobado',
                self.empleado_id, fecha_actual
            ))
            
            db.commit()
            
            if self.usuario_id:
                Bitacora(
                    accion="Registrar venta local",
                    descripcion=f"Venta local registrada: {factura_id} - Cliente: {cliente_id_str} - Total: {total_monto} {moneda}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Reportes Ventas"
                ).registrar()
            
            return factura_id
            
        except Exception as e:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()