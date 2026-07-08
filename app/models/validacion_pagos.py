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
    
    def _verificar_factura_existe(self, factura_id: str) -> bool:
        """Verifica si la factura existe en la base de datos"""
        db = self._conexion()
        if not db:
            return False
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM Venta WHERE ID_factura = %s LIMIT 1",
                (factura_id,)
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()
    
    def _verificar_empleado_existe(self, empleado_id: str) -> bool:
        """Verifica si el empleado existe"""
        db = self._conexion()
        if not db:
            return False
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM Empleado WHERE ID_empleado = %s LIMIT 1",
                (empleado_id,)
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()
    
    def _verificar_pago_pendiente(self, factura_id: str) -> bool:
        """Verifica que el pago esté en estado pendiente"""
        db = self._conexion()
        if not db:
            return False
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT Estado_pago FROM Metodo_pago WHERE ID_factura = %s LIMIT 1",
                (factura_id,)
            )
            resultado = cursor.fetchone()
            if not resultado:
                return True  # No hay registro, se puede crear
            return resultado.get("Estado_pago") == "pendiente"
        finally:
            cursor.close()
            db.close()
    
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
                WHERE LOWER(TRIM(mp.Estado_pago)) = 'pendiente'
                ORDER BY v.Fecha_venta DESC
            """)
            
            pagos = cursor.fetchall()
            
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
                WHERE LOWER(TRIM(mp.Estado_pago)) = 'aprobado'
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
                WHERE LOWER(TRIM(mp.Estado_pago)) = 'rechazado'
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
    
    def aprobar_pago(self, factura_id: str = None, empleado_id: str = None) -> Dict[str, Any]:
        """Aprueba un pago actualizando el estado en la tabla Metodo_pago"""
        factura = factura_id or self.factura_id
        empleado = empleado_id or self.empleado_id
        
        if not factura or not factura.strip():
            return {"success": False, "error": "El ID de la factura no puede estar vacío."}
        
        if not empleado or not str(empleado).strip():
            return {"success": False, "error": "El ID del empleado no puede estar vacío."}
        
        factura = factura.strip()
        empleado = str(empleado).strip()
        
        if len(factura) > 30:
            return {"success": False, "error": "El ID de la factura no puede exceder los 30 caracteres."}
        
        if not empleado.isdigit():
            return {"success": False, "error": "El ID del empleado debe contener solo números."}
        
        if len(empleado) > 8:
            return {"success": False, "error": "El ID del empleado no puede exceder los 8 dígitos."}
        
        # Verificar existencia
        if not self._verificar_factura_existe(factura):
            return {"success": False, "error": f"La factura '{factura}' no existe."}
        
        if not self._verificar_empleado_existe(empleado):
            return {"success": False, "error": f"El empleado con ID {empleado} no existe."}
        
        if not self._verificar_pago_pendiente(factura):
            return {"success": False, "error": "El pago no está pendiente o ya fue procesado."}
        
        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error al conectar a la base de datos."}
        
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
            """, (empleado, fecha_actual, factura))
            
            db.commit()
            
            if self.usuario_id:
                Bitacora(
                    accion="Aprobar pago",
                    descripcion=f"Se aprobó el pago de la factura ID: {factura}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Validación Pagos"
                ).registrar()
            
            return {"success": True, "message": "Pago aprobado exitosamente."}
        except Exception as e:
            db.rollback()
            print(f"Error en aprobar_pago: {e}")
            return {"success": False, "error": f"Error al aprobar pago: {str(e)}"}
        finally:
            cursor.close()
            db.close()
    
    def rechazar_pago(self, factura_id: str = None, empleado_id: str = None, motivo: str = None) -> Dict[str, Any]:
        """Rechaza un pago actualizando el estado en la tabla Metodo_pago"""
        factura = factura_id or self.factura_id
        empleado = empleado_id or self.empleado_id
        
        if not factura or not factura.strip():
            return {"success": False, "error": "El ID de la factura no puede estar vacío."}
        
        if not empleado or not str(empleado).strip():
            return {"success": False, "error": "El ID del empleado no puede estar vacío."}
        
        if not motivo or not motivo.strip():
            return {"success": False, "error": "El motivo de rechazo no puede estar vacío."}
        
        factura = factura.strip()
        empleado = str(empleado).strip()
        motivo = motivo.strip()
        
        if len(factura) > 30:
            return {"success": False, "error": "El ID de la factura no puede exceder los 30 caracteres."}
        
        if not empleado.isdigit():
            return {"success": False, "error": "El ID del empleado debe contener solo números."}
        
        if len(empleado) > 8:
            return {"success": False, "error": "El ID del empleado no puede exceder los 8 dígitos."}
        
        if len(motivo) > 255:
            return {"success": False, "error": "El motivo de rechazo no puede exceder los 255 caracteres."}
        
        if len(motivo) < 5:
            return {"success": False, "error": "El motivo de rechazo debe tener al menos 5 caracteres."}
        
        # Verificar existencia
        if not self._verificar_factura_existe(factura):
            return {"success": False, "error": f"La factura '{factura}' no existe."}
        
        if not self._verificar_empleado_existe(empleado):
            return {"success": False, "error": f"El empleado con ID {empleado} no existe."}
        
        if not self._verificar_pago_pendiente(factura):
            return {"success": False, "error": "El pago no está pendiente o ya fue procesado."}
        
        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error al conectar a la base de datos."}
        
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
            """, (motivo, empleado, fecha_actual, factura))
            
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Rechazar pago",
                    descripcion=f"Se rechazó el pago de la factura ID: {factura} - Motivo: {motivo}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Validación Pagos"
                )
                bitacora.registrar()
            
            return {"success": True, "message": "Pago rechazado exitosamente."}
        except Exception as e:
            db.rollback()
            print(f"Error en rechazar_pago: {e}")
            return {"success": False, "error": f"Error al rechazar pago: {str(e)}"}
        finally:
            cursor.close()
            db.close()
    
    def obtener_detalle_venta(self, factura_id: str = None) -> List[Dict[str, Any]]:
        """Obtiene el detalle de productos de una venta"""
        factura = factura_id or self.factura_id
        
        if not factura or not factura.strip():
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
            return []
        finally:
            cursor.close()
            db.close()
    
    def obtener_reportes_pagos(self, filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene pagos para reportes con filtros avanzados"""
        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error al conectar a la base de datos.", "pagos": [], "total": 0}
        
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
            
            if filtros.get("fecha_desde"):
                where_conditions.append("DATE(v.Fecha_venta) >= %s")
                params.append(filtros["fecha_desde"])
            
            if filtros.get("fecha_hasta"):
                where_conditions.append("DATE(v.Fecha_venta) <= %s")
                params.append(filtros["fecha_hasta"])
            
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
                    mp.Capture AS capture_image
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
            for pago in pagos:
                if pago.get("monto_pagado") and isinstance(pago["monto_pagado"], Decimal):
                    pago["monto_pagado"] = float(pago["monto_pagado"])
                total_monto += pago.get("monto_pagado", 0) or 0
            
            return {
                "success": True,
                "pagos": pagos,
                "total": len(pagos),
                "total_monto": total_monto
            }
        except Exception as e:
            print(f"Error en obtener_reportes_pagos: {e}")
            return {"success": False, "error": str(e), "pagos": [], "total": 0}
        finally:
            cursor.close()
            db.close()

# Agregar al final de la clase ValidacionPagosModel en app/models/validacion_pagos.py

    def actualizar_fecha_pago(self) -> None:
        """Actualiza la fecha de pago a la fecha actual"""
        if not self.factura_id:
            return
        
        db = self._conexion()
        if not db:
            return
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE Metodo_pago 
                SET Fecha_pago = %s 
                WHERE ID_factura = %s
            """, (datetime.now(), self.factura_id))
            db.commit()
        except Exception as e:
            print(f"Error en actualizar_fecha_pago: {e}")
            db.rollback()
        finally:
            cursor.close()
            db.close()

    def obtener_reporte_detalle_ventas(self) -> Dict[str, Any]:
        """Obtiene reporte detallado de una venta"""
        detalle = self.obtener_detalle_venta()
        if detalle:
            return {"success": True, "detalle": detalle}
        return {"success": False, "error": "No se encontró detalle para la venta"}

    def obtener_metodos_pago_disponibles(self) -> List[str]:
        """Retorna lista de métodos de pago disponibles"""
        return ["pago_movil", "zelle", "binance", "efectivo_usd", "efectivo_bs"]

    def obtener_monedas_disponibles(self) -> List[str]:
        """Retorna lista de monedas disponibles"""
        return ["USD", "VES", "USDT"]