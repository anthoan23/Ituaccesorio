from __future__ import annotations
from app.models.database import conectar
from app.models.bitacora import Bitacora
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional
import json
import traceback


class ValidacionPagosModel:
    """Modelo para la validación de pagos por parte de empleados"""
    
    def __init__(self, factura_id: str = None, empleado_id: str = None, usuario_id: str = None):
        self.factura_id = factura_id
        self.empleado_id = empleado_id
        self.usuario_id = usuario_id
        self.__conexion_bd = conectar()
    
    def _conexion(self):
        return self.__conexion_bd.conexion1()
    
    def obtener_pagos_pendientes(self) -> List[Dict[str, Any]]:
        """Obtiene todos los pagos pendientes de verificación"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    v.ID_factura AS factura_id,
                    v.ID_cliente AS cliente_id,
                    v.Moneda,
                    v.Fecha_venta AS fecha_venta,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    COALESCE(c.Celular_cliente, '') AS cliente_celular,
                    COALESCE(c.Correo_cliente, '') AS cliente_correo,
                    mp.Moneda AS pago_moneda,
                    mp.Fecha_pago,
                    mp.Capture AS capture_image,
                    mp.Metodo AS metodo_pago,
                    mp.Referencia,
                    mp.Monto,
                    mp.Estado_pago AS estado
                FROM Venta v
                INNER JOIN Metodo_pago mp ON v.ID_factura = mp.ID_factura
                LEFT JOIN Persona_natural pn ON v.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente c ON v.ID_cliente = c.ID_cliente
                WHERE mp.Estado_pago = 'pendiente'
                ORDER BY v.Fecha_venta DESC
            """)
            
            pagos = cursor.fetchall()
            
            # Convertir Decimal a float para serialización JSON
            for pago in pagos:
                if pago.get("Monto") and isinstance(pago["Monto"], Decimal):
                    pago["Monto"] = float(pago["Monto"])
            
            return pagos
        except Exception as e:
            print(f"Error en obtener_pagos_pendientes: {e}")
            traceback.print_exc()
            return []
        finally:
            cursor.close()
            db.close()
    
    def obtener_pagos_aprobados(self) -> List[Dict[str, Any]]:
        """Obtiene los pagos aprobados"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    v.ID_factura AS factura_id,
                    v.ID_cliente AS cliente_id,
                    v.Moneda,
                    v.Fecha_venta AS fecha_venta,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    COALESCE(c.Celular_cliente, '') AS cliente_celular,
                    mp.Fecha_pago,
                    mp.Capture AS capture_image,
                    mp.Metodo AS metodo_pago,
                    mp.Referencia,
                    mp.Monto,
                    mp.Estado_pago AS estado,
                    mp.Aprobado_por,
                    mp.Fecha_aprobacion
                FROM Venta v
                INNER JOIN Metodo_pago mp ON v.ID_factura = mp.ID_factura
                LEFT JOIN Persona_natural pn ON v.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente c ON v.ID_cliente = c.ID_cliente
                WHERE mp.Estado_pago = 'aprobado'
                ORDER BY mp.Fecha_aprobacion DESC
            """)
            
            resultados = cursor.fetchall()
            for r in resultados:
                if r.get("Monto") and isinstance(r["Monto"], Decimal):
                    r["Monto"] = float(r["Monto"])
            
            return resultados
        except Exception as e:
            print(f"Error en obtener_pagos_aprobados: {e}")
            traceback.print_exc()
            return []
        finally:
            cursor.close()
            db.close()
    
    def obtener_pagos_rechazados(self) -> List[Dict[str, Any]]:
        """Obtiene los pagos rechazados"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    v.ID_factura AS factura_id,
                    v.ID_cliente AS cliente_id,
                    v.Moneda,
                    v.Fecha_venta AS fecha_venta,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    COALESCE(c.Celular_cliente, '') AS cliente_celular,
                    mp.Fecha_pago,
                    mp.Capture AS capture_image,
                    mp.Metodo AS metodo_pago,
                    mp.Referencia,
                    mp.Monto,
                    mp.Estado_pago AS estado,
                    mp.Motivo_rechazo,
                    mp.Rechazado_por,
                    mp.Fecha_rechazo
                FROM Venta v
                INNER JOIN Metodo_pago mp ON v.ID_factura = mp.ID_factura
                LEFT JOIN Persona_natural pn ON v.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente c ON v.ID_cliente = c.ID_cliente
                WHERE mp.Estado_pago = 'rechazado'
                ORDER BY mp.Fecha_rechazo DESC
            """)
            
            resultados = cursor.fetchall()
            for r in resultados:
                if r.get("Monto") and isinstance(r["Monto"], Decimal):
                    r["Monto"] = float(r["Monto"])
            
            return resultados
        except Exception as e:
            print(f"Error en obtener_pagos_rechazados: {e}")
            traceback.print_exc()
            return []
        finally:
            cursor.close()
            db.close()
    
    def aprobar_pago(self, factura_id: str = None) -> Dict[str, Any]:
        """Aprueba un pago actualizando el estado en la tabla Metodo_pago"""
        factura = factura_id or self.factura_id
        empleado = self.empleado_id
        
        if not factura:
            return {"success": False, "error": "ID de factura no especificado"}
        if not empleado:
            return {"success": False, "error": "Empleado no identificado"}
        
        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error de conexión"}
        
        cursor = db.cursor()
        try:
            fecha_actual = datetime.now()
            
            cursor.execute("""
                UPDATE Metodo_pago 
                SET 
                    Estado_pago = 'aprobado',
                    Aprobado_por = %s,
                    Fecha_aprobacion = %s
                WHERE ID_factura = %s
            """, (str(empleado), fecha_actual, factura))
            
            db.commit()
            
            if self.usuario_id:
                Bitacora(
                    accion="Aprobar pago",
                    descripcion=f"Se aprobó el pago de la factura ID: {factura}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Validación Pagos"
                ).registrar()
            
            return {"success": True, "message": "Pago aprobado correctamente"}
        except Exception as e:
            db.rollback()
            print(f"Error en aprobar_pago: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
            db.close()
    
    def rechazar_pago(self, factura_id: str = None, motivo: str = None) -> Dict[str, Any]:
        """Rechaza un pago actualizando el estado en la tabla Metodo_pago"""
        factura = factura_id or self.factura_id
        empleado = self.empleado_id
        
        if not factura:
            return {"success": False, "error": "ID de factura no especificado"}
        if not empleado:
            return {"success": False, "error": "Empleado no identificado"}
        if not motivo:
            return {"success": False, "error": "Motivo de rechazo no especificado"}
        
        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error de conexión"}
        
        cursor = db.cursor()
        try:
            fecha_actual = datetime.now()
            
            cursor.execute("""
                UPDATE Metodo_pago 
                SET 
                    Estado_pago = 'rechazado',
                    Motivo_rechazo = %s,
                    Rechazado_por = %s,
                    Fecha_rechazo = %s
                WHERE ID_factura = %s
            """, (motivo, str(empleado), fecha_actual, factura))
            
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Rechazar pago",
                    descripcion=f"Se rechazó el pago de la factura ID: {factura} - Motivo: {motivo}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Validación Pagos"
                )
                bitacora.registrar()
            
            return {"success": True, "message": "Pago rechazado"}
        except Exception as e:
            db.rollback()
            print(f"Error en rechazar_pago: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
            db.close()
    
    def obtener_detalle_venta(self, factura_id: str = None) -> List[Dict[str, Any]]:
        """Obtiene el detalle de productos de una venta"""
        factura = factura_id or self.factura_id
        if not factura:
            return []
        
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    dv.ID_inventario,
                    dv.Cantidad_articulo,
                    i.Costo_venta,
                    p.Nombre_producto,
                    COALESCE(ma.Nombre_marca, '') AS marca,
                    COALESCE(cl.Nombre_Clase, '') AS clase
                FROM Detalle_venta dv
                JOIN Existencias_productos i ON dv.ID_inventario = i.ID_inventario
                JOIN Producto p ON i.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                WHERE dv.ID_factura = %s
            """, (factura,))
            
            items = cursor.fetchall()
            
            for item in items:
                if isinstance(item.get("Costo_venta"), Decimal):
                    item["Costo_venta"] = float(item["Costo_venta"])
                if isinstance(item.get("Cantidad_articulo"), Decimal):
                    item["Cantidad_articulo"] = int(item["Cantidad_articulo"])
            
            return items
        except Exception as e:
            print(f"Error en obtener_detalle_venta: {e}")
            traceback.print_exc()
            return []
        finally:
            cursor.close()
            db.close()
    
    def actualizar_fecha_pago(self, factura_id: str = None) -> Dict[str, Any]:
        """Actualiza la fecha de pago a la fecha actual"""
        factura = factura_id or self.factura_id
        if not factura:
            return {"success": False, "error": "ID de factura no especificado"}
        
        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error de conexión"}
        
        cursor = db.cursor()
        try:
            fecha_actual = datetime.now()
            
            cursor.execute("""
                UPDATE Metodo_pago 
                SET Fecha_pago = %s
                WHERE ID_factura = %s AND Estado_pago = 'pendiente'
            """, (fecha_actual, factura))
            
            db.commit()
            return {"success": True, "message": "Fecha de pago actualizada"}
        except Exception as e:
            db.rollback()
            print(f"Error en actualizar_fecha_pago: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
            db.close()
    
    # ==================== MÉTODOS PARA REPORTES ====================
    
    def obtener_reportes_pagos(self, filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene pagos para reportes con filtros avanzados"""
        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error de conexión", "pagos": [], "total": 0}
        
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
            
            if filtros.get("monto_min"):
                where_conditions.append("mp.Monto >= %s")
                params.append(float(filtros["monto_min"]))
            
            if filtros.get("monto_max"):
                where_conditions.append("mp.Monto <= %s")
                params.append(float(filtros["monto_max"]))
            
            where_sql = " AND ".join(where_conditions)
            
            query = f"""
                SELECT 
                    v.ID_factura AS factura_id,
                    v.ID_cliente AS cliente_id,
                    v.Moneda AS venta_moneda,
                    v.Fecha_venta AS fecha_venta,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    COALESCE(c.Celular_cliente, '') AS cliente_celular,
                    COALESCE(c.Correo_cliente, '') AS cliente_correo,
                    c.Direccion_cliente AS cliente_direccion,
                    mp.Fecha_pago,
                    mp.Metodo AS metodo_pago,
                    mp.Referencia,
                    mp.Monto AS monto_pagado,
                    mp.Moneda AS pago_moneda,
                    mp.Estado_pago AS estado,
                    mp.Aprobado_por,
                    mp.Fecha_aprobacion,
                    mp.Rechazado_por,
                    mp.Fecha_rechazo,
                    mp.Motivo_rechazo,
                    mp.Capture AS capture_image,
                    (
                        SELECT COALESCE(SUM(dv.Cantidad_articulo), 0)
                        FROM Detalle_venta dv
                        WHERE dv.ID_factura = v.ID_factura
                    ) AS total_productos,
                    (
                        SELECT COALESCE(SUM(i.Costo_venta * dv.Cantidad_articulo), 0)
                        FROM Detalle_venta dv
                        JOIN Existencias_productos i ON dv.ID_inventario = i.ID_inventario
                        WHERE dv.ID_factura = v.ID_factura
                    ) AS total_venta
                FROM Venta v
                INNER JOIN Metodo_pago mp ON v.ID_factura = mp.ID_factura
                LEFT JOIN Persona_natural pn ON v.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente c ON v.ID_cliente = c.ID_cliente
                WHERE {where_sql}
                ORDER BY v.Fecha_venta DESC
            """
            
            cursor.execute(query, tuple(params))
            pagos = cursor.fetchall()
            
            total_monto = 0
            cantidad_pendientes = 0
            cantidad_aprobados = 0
            cantidad_rechazados = 0
            
            for pago in pagos:
                if pago.get("monto_pagado") is not None and isinstance(pago["monto_pagado"], Decimal):
                    pago["monto_pagado"] = float(pago["monto_pagado"])
                if pago.get("total_venta") is not None and isinstance(pago["total_venta"], Decimal):
                    pago["total_venta"] = float(pago["total_venta"])
                
                monto = pago.get("monto_pagado", 0) or 0
                total_monto += monto
                
                estado = pago.get("estado", "")
                if estado == "pendiente":
                    cantidad_pendientes += 1
                elif estado == "aprobado":
                    cantidad_aprobados += 1
                elif estado == "rechazado":
                    cantidad_rechazados += 1
            
            return {
                "success": True,
                "pagos": pagos,
                "total": len(pagos),
                "total_monto": total_monto,
                "pendientes": cantidad_pendientes,
                "aprobados": cantidad_aprobados,
                "rechazados": cantidad_rechazados
            }
        except Exception as e:
            print(f"Error en obtener_reportes_pagos: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e), "pagos": [], "total": 0}
        finally:
            cursor.close()
            db.close()
    
    def obtener_reporte_detalle_ventas(self, factura_id: str = None) -> Dict[str, Any]:
        """Obtiene el detalle completo de productos de una venta para reportes"""
        factura = factura_id or self.factura_id
        if not factura:
            return {"success": False, "error": "ID de factura no especificado", "productos": []}
        
        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error de conexión", "productos": []}
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    v.ID_factura AS factura_id,
                    v.Fecha_venta,
                    v.Moneda AS moneda,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    c.Celular_cliente,
                    c.Correo_cliente,
                    c.Direccion_cliente,
                    mp.Metodo AS metodo_pago,
                    mp.Referencia,
                    mp.Monto AS monto_pagado,
                    mp.Estado_pago AS estado
                FROM Venta v
                LEFT JOIN Metodo_pago mp ON v.ID_factura = mp.ID_factura
                LEFT JOIN Persona_natural pn ON v.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente c ON v.ID_cliente = c.ID_cliente
                WHERE v.ID_factura = %s
            """, (factura,))
            
            venta = cursor.fetchone()
            if not venta:
                return {"success": False, "error": "Venta no encontrada", "productos": []}
            
            if venta.get("monto_pagado") and isinstance(venta["monto_pagado"], Decimal):
                venta["monto_pagado"] = float(venta["monto_pagado"])
            
            cursor.execute("""
                SELECT 
                    dv.ID_inventario,
                    dv.Cantidad_articulo,
                    i.Costo_venta AS precio_unitario,
                    (i.Costo_venta * dv.Cantidad_articulo) AS subtotal,
                    p.Nombre_producto,
                    p.Descripcion,
                    COALESCE(ma.Nombre_marca, '') AS marca,
                    COALESCE(cl.Nombre_Clase, '') AS clase
                FROM Detalle_venta dv
                JOIN Existencias_productos i ON dv.ID_inventario = i.ID_inventario
                JOIN Producto p ON i.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                WHERE dv.ID_factura = %s
            """, (factura,))
            
            productos = cursor.fetchall()
            total_venta = 0
            total_productos = 0
            
            for p in productos:
                if isinstance(p.get("precio_unitario"), Decimal):
                    p["precio_unitario"] = float(p["precio_unitario"])
                if isinstance(p.get("subtotal"), Decimal):
                    p["subtotal"] = float(p["subtotal"])
                if isinstance(p.get("Cantidad_articulo"), Decimal):
                    p["Cantidad_articulo"] = int(p["Cantidad_articulo"])
                
                total_venta += p.get("subtotal", 0)
                total_productos += p.get("Cantidad_articulo", 0)
            
            return {
                "success": True,
                "venta": venta,
                "productos": productos,
                "total_venta": total_venta,
                "total_productos": total_productos
            }
        except Exception as e:
            print(f"Error en obtener_reporte_detalle_ventas: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e), "productos": []}
        finally:
            cursor.close()
            db.close()
    
    def obtener_metodos_pago_disponibles(self) -> List[str]:
        """Obtiene la lista de métodos de pago disponibles según la BD"""
        db = self._conexion()
        if not db:
            return ["pago_movil", "zelle", "binance", "efectivo_usd", "efectivo_bs"]
        
        cursor = db.cursor()
        try:
            cursor.execute("SELECT DISTINCT Metodo FROM Metodo_pago WHERE Metodo IS NOT NULL")
            resultados = cursor.fetchall()
            metodos = list(set([r[0] for r in resultados]))
            return metodos if metodos else ["pago_movil", "zelle", "binance", "efectivo_usd", "efectivo_bs"]
        except Exception as e:
            print(f"Error en obtener_metodos_pago_disponibles: {e}")
            return ["pago_movil", "zelle", "binance", "efectivo_usd", "efectivo_bs"]
        finally:
            cursor.close()
            db.close()
    
    def obtener_monedas_disponibles(self) -> List[str]:
        """Obtiene la lista de monedas disponibles según la BD"""
        db = self._conexion()
        if not db:
            return ["USD", "VES", "USDT"]
        
        cursor = db.cursor()
        try:
            cursor.execute("SELECT DISTINCT Moneda FROM Metodo_pago WHERE Moneda IS NOT NULL")
            resultados = cursor.fetchall()
            monedas = list(set([r[0] for r in resultados]))
            return monedas if monedas else ["USD", "VES", "USDT"]
        except Exception as e:
            print(f"Error en obtener_monedas_disponibles: {e}")
            return ["USD", "VES", "USDT"]
        finally:
            cursor.close()
            db.close()