from __future__ import annotations
from app.models.database import conectar
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
import json


class ValidacionPagosModel:
    """Modelo para la validación de pagos por parte de empleados"""
    
    def __init__(self):
        self.__conexion_bd = conectar()
    
    def obtener_pagos_pendientes(self) -> List[Dict[str, Any]]:
        """Obtiene todos los pagos pendientes de verificación"""
        db = self.__conexion_bd.conexion1()
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
                    mp.Moneda AS moneda_pago,
                    mp.Fecha_pago,
                    mp.Capture AS capture_image,
                    mp.Metodo AS metodo_pago,
                    mp.Referencia,
                    mp.Monto,
                    COALESCE(mp.Estado_pago, 'pendiente') AS estado
                FROM Venta v
                INNER JOIN Metodo_pago mp ON v.ID_factura = mp.ID_factura
                LEFT JOIN Persona_natural pn ON v.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente c ON v.ID_cliente = c.ID_cliente
                WHERE COALESCE(mp.Estado_pago, 'pendiente') = 'pendiente'
                ORDER BY v.Fecha_venta DESC
            """)
            
            pagos = cursor.fetchall()
            print(f"Pagos pendientes encontrados: {len(pagos)}")
            for pago in pagos:
                print(f"Factura: {pago.get('factura_id')}, Referencia: {pago.get('Referencia')}, Monto: {pago.get('Monto')}")
            
            return pagos
        except Exception as e:
            print(f"Error en obtener_pagos_pendientes: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def obtener_pagos_aprobados(self) -> List[Dict[str, Any]]:
        """Obtiene los pagos aprobados"""
        db = self.__conexion_bd.conexion1()
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
            
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en obtener_pagos_aprobados: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def obtener_pagos_rechazados(self) -> List[Dict[str, Any]]:
        """Obtiene los pagos rechazados"""
        db = self.__conexion_bd.conexion1()
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
            
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en obtener_pagos_rechazados: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def aprobar_pago(self, factura_id: str, empleado_id: str) -> Dict[str, Any]:
        """Aprueba un pago actualizando el estado en la tabla Metodo_pago"""
        db = self.__conexion_bd.conexion1()
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
            """, (empleado_id, fecha_actual, factura_id))
            
            db.commit()
            return {"success": True, "message": "Pago aprobado correctamente"}
        except Exception as e:
            db.rollback()
            print(f"Error en aprobar_pago: {e}")
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
            db.close()
    
    def rechazar_pago(self, factura_id: str, empleado_id: str, motivo: str) -> Dict[str, Any]:
        """Rechaza un pago actualizando el estado en la tabla Metodo_pago"""
        db = self.__conexion_bd.conexion1()
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
            """, (motivo, empleado_id, fecha_actual, factura_id))
            
            db.commit()
            return {"success": True, "message": "Pago rechazado"}
        except Exception as e:
            db.rollback()
            print(f"Error en rechazar_pago: {e}")
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
            db.close()
    
    def obtener_detalle_venta(self, factura_id: str) -> List[Dict[str, Any]]:
        """Obtiene el detalle de productos de una venta"""
        db = self.__conexion_bd.conexion1()
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
                    COALESCE(ma.Nombre_marca, '') AS marca
                FROM Detalle_venta dv
                JOIN Inventario i ON dv.ID_inventario = i.ID_inventario
                JOIN Producto p ON i.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                WHERE dv.ID_factura = %s
            """, (factura_id,))
            
            items = cursor.fetchall()
            print(f"Detalle venta {factura_id}: {len(items)} items encontrados")
            
            for item in items:
                if isinstance(item.get("Costo_venta"), Decimal):
                    item["Costo_venta"] = float(item["Costo_venta"])
            
            return items
        except Exception as e:
            print(f"Error en obtener_detalle_venta: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def actualizar_fecha_pago(self, factura_id: str) -> Dict[str, Any]:
        """Actualiza la fecha de pago a la fecha actual"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return {"success": False, "error": "Error de conexión"}
        
        cursor = db.cursor()
        try:
            fecha_actual = datetime.now()
            
            cursor.execute("""
                UPDATE Metodo_pago 
                SET Fecha_pago = %s
                WHERE ID_factura = %s AND Estado_pago = 'pendiente'
            """, (fecha_actual, factura_id))
            
            db.commit()
            return {"success": True, "message": "Fecha de pago actualizada"}
        except Exception as e:
            db.rollback()
            print(f"Error en actualizar_fecha_pago: {e}")
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
            db.close()