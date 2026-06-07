from __future__ import annotations
from app.models.database import conectar
from typing import List, Dict, Any

class ValidacionPagosModel:
    """Modelo para validación de pagos"""
    
    def __init__(self):
        self.__conexion_bd = conectar()
    
    def obtener_pagos_pendientes(self) -> List[Dict[str, Any]]:
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
                    v.Fecha_venta,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    COALESCE(c.Celular_cliente, '') AS cliente_celular,
                    mp.Moneda AS moneda_pago,
                    mp.Fecha_pago,
                    mp.Capture AS datos_pago
                FROM Venta v
                LEFT JOIN Metodo_pago mp ON v.ID_factura = mp.ID_factura
                LEFT JOIN Persona_natural pn ON v.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente c ON v.ID_cliente = c.ID_cliente
                WHERE mp.ID_factura IS NOT NULL
                  AND v.Moneda != 'USD'
                ORDER BY v.Fecha_venta DESC
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()
    
    def obtener_pagos_aprobados(self) -> List[Dict[str, Any]]:
        return []
    
    def obtener_pagos_rechazados(self) -> List[Dict[str, Any]]:
        return []
    
    def aprobar_pago(self, factura_id: str, empleado_id: str) -> None:
        pass
    
    def rechazar_pago(self, factura_id: str, empleado_id: str, motivo: str) -> None:
        pass