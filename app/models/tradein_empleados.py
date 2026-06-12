from __future__ import annotations
from app.models.database import conectar
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional


class TradeInEmpleados:
    """Modelo para la gestión de Trade-In por parte de empleados"""
    
    # Catálogo de fallas para evaluación
    CATALOGO_FALLAS = [
        {"id": "pantalla", "nombre": "Pantalla dañada", "deduccion_base": 50},
        {"id": "bateria", "nombre": "Batería dañada", "deduccion_base": 30},
        {"id": "camara", "nombre": "Cámara dañada", "deduccion_base": 40},
        {"id": "botones", "nombre": "Botones dañados", "deduccion_base": 20},
        {"id": "carga", "nombre": "Puerto de carga dañado", "deduccion_base": 25},
        {"id": "audio", "nombre": "Audio/Micrófono dañado", "deduccion_base": 35},
        {"id": "sensor", "nombre": "Sensores dañados", "deduccion_base": 15},
        {"id": "caja", "nombre": "Sin caja original", "deduccion_base": 10},
        {"id": "accesorios", "nombre": "Sin accesorios", "deduccion_base": 15},
        {"id": "imei", "nombre": "IMEI bloqueado", "deduccion_base": 100},
        {"id": "agua", "nombre": "Daño por agua", "deduccion_base": 80},
    ]
    
    def __init__(self):
        self.__conexion_bd = conectar()
    
    def _conexion(self):
        """Retorna la conexión a la base de datos de negocio (ituaccesoriobd)"""
        return self.__conexion_bd.conexion1()
    
    def obtener_trade_ins_pendientes(self) -> List[Dict[str, Any]]:
        """Obtiene todos los trade-ins pendientes de evaluación"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    t.ID_Trade_in AS id,
                    t.ID_empleado AS empleado_id,
                    t.ID_cliente AS cliente_id,
                    t.ID_inventario AS inventario_id,
                    t.ID_equipo AS equipo_id,
                    t.Numero_utilizado,
                    t.Fecha_realizado AS fecha,
                    t.cotizacion,
                    e.ID_equipo,
                    e.IMEI,
                    e.Color,
                    e.Capacidad,
                    p.Nombre_producto AS producto_nombre,
                    p.Descripcion AS producto_descripcion,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    c.Celular_cliente AS cliente_celular,
                    c.Correo_cliente AS cliente_correo,
                    cl.Nombre_Clase AS clase,
                    m.Nombre_marca AS marca,
                    'pendiente' AS estado,
                    NULL AS fecha_evaluacion,
                    NULL AS evaluado_por,
                    NULL AS nota_evaluacion,
                    NULL AS valor_final
                FROM Trade_in t
                LEFT JOIN Equipo e ON t.ID_equipo = e.ID_equipo
                LEFT JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Cliente c ON t.ID_cliente = c.ID_cliente
                LEFT JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                LEFT JOIN Marca_producto m ON p.ID_marca = m.ID_marca
                WHERE t.cotizacion IS NULL OR t.cotizacion = 0
                ORDER BY t.Fecha_realizado DESC
            """)
            resultados = cursor.fetchall()
            
            # Agregar información de fotos
            for trade in resultados:
                trade["fotos"] = self.obtener_fotos_trade_in(trade["id"])
            
            return resultados
        except Exception as e:
            print(f"Error en obtener_trade_ins_pendientes: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def obtener_trade_ins_evaluados(self) -> List[Dict[str, Any]]:
        """Obtiene los trade-ins ya evaluados"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    t.ID_Trade_in AS id,
                    t.ID_empleado AS empleado_id,
                    t.ID_cliente AS cliente_id,
                    t.ID_inventario AS inventario_id,
                    t.ID_equipo AS equipo_id,
                    t.Numero_utilizado,
                    t.Fecha_realizado AS fecha,
                    t.cotizacion,
                    e.ID_equipo,
                    e.IMEI,
                    e.Color,
                    e.Capacidad,
                    p.Nombre_producto AS producto_nombre,
                    p.Descripcion AS producto_descripcion,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    c.Celular_cliente AS cliente_celular,
                    c.Correo_cliente AS cliente_correo,
                    cl.Nombre_Clase AS clase,
                    m.Nombre_marca AS marca,
                    'evaluado' AS estado,
                    t.Fecha_realizado AS fecha_evaluacion,
                    t.ID_empleado AS evaluado_por
                FROM Trade_in t
                LEFT JOIN Equipo e ON t.ID_equipo = e.ID_equipo
                LEFT JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Cliente c ON t.ID_cliente = c.ID_cliente
                LEFT JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                LEFT JOIN Marca_producto m ON p.ID_marca = m.ID_marca
                WHERE t.cotizacion IS NOT NULL AND t.cotizacion > 0
                ORDER BY t.Fecha_realizado DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en obtener_trade_ins_evaluados: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def obtener_detalle_trade_in(self, trade_in_id: str) -> Dict[str, Any]:
        """Obtiene el detalle completo de un trade-in específico"""
        db = self._conexion()
        if not db:
            return {}
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    t.ID_Trade_in AS id,
                    t.ID_empleado AS empleado_id,
                    t.ID_cliente AS cliente_id,
                    t.ID_inventario AS inventario_id,
                    t.ID_equipo AS equipo_id,
                    t.Numero_utilizado,
                    t.Fecha_realizado AS fecha,
                    t.cotizacion,
                    e.ID_equipo,
                    e.IMEI,
                    e.Color,
                    e.Capacidad,
                    e.Clave,
                    e.Patron,
                    p.Nombre_producto AS producto_nombre,
                    p.Descripcion AS producto_descripcion,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    c.Celular_cliente AS cliente_celular,
                    c.Correo_cliente AS cliente_correo,
                    c.Direccion_cliente AS cliente_direccion,
                    cl.Nombre_Clase AS clase,
                    m.Nombre_marca AS marca,
                    emp.Nombre_empleado AS empleado_nombre,
                    emp.Apellido_empleado AS empleado_apellido
                FROM Trade_in t
                LEFT JOIN Equipo e ON t.ID_equipo = e.ID_equipo
                LEFT JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Cliente c ON t.ID_cliente = c.ID_cliente
                LEFT JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                LEFT JOIN Marca_producto m ON p.ID_marca = m.ID_marca
                LEFT JOIN Empleado emp ON t.ID_empleado = emp.ID_empleado
                WHERE t.ID_Trade_in = %s
            """, (trade_in_id,))
            return cursor.fetchone() or {}
        except Exception as e:
            print(f"Error en obtener_detalle_trade_in: {e}")
            return {}
        finally:
            cursor.close()
            db.close()
    
    def obtener_fotos_trade_in(self, trade_in_id: str) -> List[Dict[str, Any]]:
        """Obtiene las fotos asociadas a un trade-in"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT ID_foto_trade_in AS id, Foto_trade_in AS url
                FROM Fotos_trade_in
                WHERE ID_Trade_in = %s
            """, (trade_in_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en obtener_fotos_trade_in: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def obtener_tests_trade_in(self, trade_in_id: str) -> List[Dict[str, Any]]:
        """Obtiene los tests realizados para un trade-in"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    t.ID_test,
                    t.Numero_test,
                    t.Nombre_test,
                    t.Resultado_test
                FROM Test_realizados_trade_in tr
                INNER JOIN Test t ON tr.ID_test = t.ID_test
                WHERE tr.ID_Trade_in = %s
                ORDER BY t.Numero_test, t.ID_test
            """, (trade_in_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en obtener_tests_trade_in: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def evaluar_trade_in(self, trade_in_id: str, valor: float, empleado_id: str, fallas: List[str] = None, observaciones: str = "") -> Dict[str, Any]:
        """Evalúa un trade-in asignando un valor de cotización"""
        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error de conexión"}
        
        cursor = db.cursor()
        try:
            # Actualizar cotización
            cursor.execute("""
                UPDATE Trade_in 
                SET cotizacion = %s
                WHERE ID_Trade_in = %s
            """, (valor, trade_in_id))
            
            # Registrar fallas en tabla de pruebas si se proporcionaron
            if fallas:
                # Obtener el último número de test
                cursor.execute("SELECT MAX(Numero_test) FROM Test")
                result = cursor.fetchone()
                next_num = (result[0] or 0) + 1
                
                # Insertar cada falla como un test
                for falla in fallas:
                    # Generar ID único para test
                    cursor.execute("SELECT MAX(ID_test) FROM Test")
                    last_id = cursor.fetchone()
                    last_num = int(last_id[0][3:]) if last_id and last_id[0] else 0
                    test_id = f"TST{str(last_num + 1).zfill(6)}"
                    
                    cursor.execute("""
                        INSERT INTO Test (ID_test, Numero_test, Nombre_test, Resultado_test)
                        VALUES (%s, %s, %s, %s)
                    """, (test_id, next_num, falla, "Fallo detectado"))
                    
                    # Relacionar con trade-in
                    cursor.execute("""
                        INSERT INTO Test_realizados_trade_in (ID_Trade_in, ID_test)
                        VALUES (%s, %s)
                    """, (trade_in_id, test_id))
            
            db.commit()
            return {"success": True, "message": "Trade-in evaluado correctamente"}
        except Exception as e:
            db.rollback()
            print(f"Error en evaluar_trade_in: {e}")
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
            db.close()
    
    def obtener_historial_trade_in_cliente(self, cliente_id: str) -> List[Dict[str, Any]]:
        """Obtiene el historial de trade-ins de un cliente"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    t.ID_Trade_in AS id,
                    t.Fecha_realizado AS fecha,
                    t.cotizacion,
                    p.Nombre_producto AS producto_nombre,
                    e.Color,
                    e.Capacidad
                FROM Trade_in t
                LEFT JOIN Equipo e ON t.ID_equipo = e.ID_equipo
                LEFT JOIN Producto p ON e.ID_producto = p.ID_producto
                WHERE t.ID_cliente = %s
                ORDER BY t.Fecha_realizado DESC
            """, (cliente_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en obtener_historial_trade_in_cliente: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de trade-ins"""
        db = self._conexion()
        if not db:
            return {}
        
        cursor = db.cursor(dictionary=True)
        try:
            # Total de trade-ins
            cursor.execute("SELECT COUNT(*) AS total FROM Trade_in")
            total = cursor.fetchone() or {}
            
            # Trade-ins pendientes (sin cotización)
            cursor.execute("SELECT COUNT(*) AS pendientes FROM Trade_in WHERE cotizacion IS NULL OR cotizacion = 0")
            pendientes = cursor.fetchone() or {}
            
            # Trade-ins evaluados
            cursor.execute("SELECT COUNT(*) AS evaluados FROM Trade_in WHERE cotizacion IS NOT NULL AND cotizacion > 0")
            evaluados = cursor.fetchone() or {}
            
            # Valor total de cotizaciones
            cursor.execute("SELECT COALESCE(SUM(cotizacion), 0) AS total_valor FROM Trade_in WHERE cotizacion IS NOT NULL")
            valor_total = cursor.fetchone() or {}
            
            return {
                "total": total.get("total", 0),
                "pendientes": pendientes.get("pendientes", 0),
                "evaluados": evaluados.get("evaluados", 0),
                "valor_total": float(valor_total.get("total_valor", 0))
            }
        except Exception as e:
            print(f"Error en obtener_estadisticas: {e}")
            return {}
        finally:
            cursor.close()
            db.close()
    
    def obtener_equipos_disponibles(self) -> List[Dict[str, Any]]:
        """Obtiene equipos disponibles para trade-in"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    i.ID_inventario AS id,
                    i.Costo_venta AS precio,
                    p.Nombre_producto AS nombre,
                    cl.Nombre_Clase AS clase,
                    m.Nombre_marca AS marca
                FROM Inventario i
                INNER JOIN Producto p ON p.ID_producto = i.ID_producto
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                LEFT JOIN Marca_producto m ON p.ID_marca = m.ID_marca
                WHERE i.Existencia > 0
                ORDER BY p.Nombre_producto ASC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en obtener_equipos_disponibles: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def obtener_catalogo_fallas(self) -> List[Dict[str, Any]]:
        """Obtiene el catálogo de fallas para evaluación"""
        return self.CATALOGO_FALLAS