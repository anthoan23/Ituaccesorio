from __future__ import annotations
from app.models.database import conectar
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional
import json


class TradeInEmpleados:
    """Modelo para la gestión de Trade-In por parte de empleados"""
    
    def __init__(self):
        self.__conexion_bd = conectar()
    
    def _conexion(self):
        """Retorna la conexión a la base de datos de negocio (ituaccesoriobd)"""
        return self.__conexion_bd.conexion1()
    
    def _generar_id_trade_in(self) -> str:
        """Genera un nuevo ID para Trade_in (formato TRD000001)"""
        db = self._conexion()
        if not db:
            return "TRD000001"
        
        cursor = db.cursor()
        try:
            # Obtener el ID más alto
            cursor.execute("SELECT MAX(ID_Trade_in) FROM Trade_in")
            row = cursor.fetchone()
            ultimo_id = row[0] if row and row[0] else None
            
            if ultimo_id:
                try:
                    num_str = ultimo_id[3:]  # Quita 'TRD'
                    num = int(num_str)
                    siguiente = num + 1
                except (ValueError, IndexError):
                    siguiente = 1
            else:
                siguiente = 1
            
            # Formatear con 6 dígitos (ej: 1 -> 000001)
            return f"TRD{str(siguiente).zfill(6)}"
        except Exception as e:
            print(f"Error generando ID trade-in: {e}")
            # Fallback: usar timestamp
            return f"TRD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        finally:
            cursor.close()
            db.close()
    
    def _generar_id_foto_trade_in(self) -> str:
        """Genera ID para Fotos_trade_in (formato FTI0000001)"""
        db = self._conexion()
        if not db:
            return "FTI0000001"
        
        cursor = db.cursor()
        try:
            cursor.execute("SELECT MAX(ID_foto_trade_in) FROM Fotos_trade_in")
            row = cursor.fetchone()
            ultimo_id = row[0] if row and row[0] else None
            
            if ultimo_id:
                try:
                    num_str = ultimo_id[3:]  # Quita 'FTI'
                    num = int(num_str)
                    siguiente = num + 1
                except (ValueError, IndexError):
                    siguiente = 1
            else:
                siguiente = 1
            
            return f"FTI{str(siguiente).zfill(7)}"
        except Exception as e:
            print(f"Error generando ID foto: {e}")
            return f"FTI{datetime.now().strftime('%Y%m%d%H%M%S')}"
        finally:
            cursor.close()
            db.close()
    
    # ==================== REGISTRAR NUEVO TRADE-IN ====================
    
    def registrar_trade_in(
        self,
        cliente_id: str,
        id_producto: str,
        valor_pagado: float,
        empleado_id: str,
        id_equipo: str,  # AHORA ES MANUAL (actúa como IMEI)
        color: str = None,
        capacidad: str = None,
        clave: str = None,
        patron: str = None,
        observaciones: str = None,
        fotos: List[str] = None
    ) -> Dict[str, Any]:
        """
        Registra un nuevo equipo recibido en trade-in
        
        Args:
            cliente_id: ID del cliente que vende el equipo
            id_producto: ID del producto/modelo (ej: '1' para iPhone 15)
            valor_pagado: Monto que pagó la tienda por el equipo
            empleado_id: Cédula del empleado que recibe
            id_equipo: ID manual del equipo (actúa como IMEI/número de serie)
            color: Color del equipo
            capacidad: Capacidad de almacenamiento
            clave: Clave numérica del equipo
            patron: Patrón de desbloqueo
            observaciones: Notas adicionales
            fotos: Lista de rutas de fotos subidas
        """
        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error de conexión a la base de datos"}
        
        cursor = db.cursor()
        try:
            # 1. Verificar si el equipo ya existe (por ID_equipo que funciona como IMEI)
            cursor.execute(
                "SELECT ID_equipo FROM Equipo WHERE ID_equipo = %s LIMIT 1",
                (id_equipo,)
            )
            row = cursor.fetchone()
            
            if row:
                # El equipo ya existe, usar el existente
                equipo_id = row[0]
            else:
                # El equipo no existe, crear nuevo con el ID proporcionado manualmente
                equipo_id = id_equipo
                cursor.execute("""
                    INSERT INTO Equipo (ID_equipo, ID_producto, Color, Capacidad, Clave, Patron)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (equipo_id, id_producto, color, capacidad, clave, patron))
            
            # 2. Crear registro de trade-in
            trade_in_id = self._generar_id_trade_in()
            fecha_actual = datetime.now()
            
            cursor.execute("""
                INSERT INTO Trade_in (ID_Trade_in, ID_empleado, ID_cliente, ID_equipo, Numero_utilizado, Fecha_realizado, cotizacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (trade_in_id, empleado_id, cliente_id, equipo_id, 0, fecha_actual, valor_pagado))
            
            # 3. Guardar fotos si las hay
            if fotos:
                for foto_url in fotos:
                    id_foto = self._generar_id_foto_trade_in()
                    cursor.execute("""
                        INSERT INTO Fotos_trade_in (ID_foto_trade_in, ID_Trade_in, Foto_trade_in)
                        VALUES (%s, %s, %s)
                    """, (id_foto, trade_in_id, foto_url))
            
            db.commit()
            
            return {
                "success": True,
                "message": f"Trade-in registrado correctamente",
                "trade_in_id": trade_in_id,
                "equipo_id": equipo_id
            }
            
        except Exception as e:
            db.rollback()
            print(f"Error en registrar_trade_in: {e}")
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
            db.close()
    
    # ==================== REGISTRAR TESTS DEL EQUIPO ====================
    
    def registrar_tests_trade_in(self, trade_in_id: str, tests: List[Dict[str, str]], empleado_id: str = None) -> Dict[str, Any]:
        """
        Registra los tests realizados al equipo trade-in
        
        Args:
            trade_in_id: ID del trade-in
            tests: Lista de diccionarios [{"nombre": "Pantalla", "resultado": "Funciona"}, ...]
            empleado_id: ID del empleado que realizó los tests (opcional)
        """
        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error de conexión"}
        
        cursor = db.cursor()
        try:
            # Obtener el último número de test para este trade-in
            cursor.execute("""
                SELECT COALESCE(MAX(t.Numero_test), 0)
                FROM Test_realizados_trade_in tr
                JOIN Test t ON tr.ID_test = t.ID_test
                WHERE tr.ID_Trade_in = %s
            """, (trade_in_id,))
            row = cursor.fetchone()
            next_num = (row[0] or 0) + 1
            
            # Registrar cada test
            tests_registrados = 0
            for test in tests:
                nombre = test.get("nombre", "")
                resultado = test.get("resultado", "")
                
                if not nombre:
                    continue
                
                # Generar ID único para test
                cursor.execute("SELECT MAX(ID_test) FROM Test")
                last_id = cursor.fetchone()
                last_num = int(last_id[0][3:]) if last_id and last_id[0] else 0
                test_id = f"TST{str(last_num + 1).zfill(6)}"
                
                cursor.execute("""
                    INSERT INTO Test (ID_test, Numero_test, Nombre_test, Resultado_test)
                    VALUES (%s, %s, %s, %s)
                """, (test_id, next_num, nombre, resultado))
                
                cursor.execute("""
                    INSERT INTO Test_realizados_trade_in (ID_Trade_in, ID_test)
                    VALUES (%s, %s)
                """, (trade_in_id, test_id))
                tests_registrados += 1
            
            db.commit()
            return {"success": True, "message": f"{tests_registrados} tests registrados correctamente", "tests": tests_registrados}
            
        except Exception as e:
            db.rollback()
            print(f"Error en registrar_tests_trade_in: {e}")
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
            db.close()
    
    # ==================== LISTAR TRADE-INS ====================
    
    def obtener_trade_ins(self) -> List[Dict[str, Any]]:
        """Obtiene todos los trade-ins registrados"""
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
                    t.ID_equipo AS equipo_id,
                    t.Numero_utilizado,
                    t.Fecha_realizado AS fecha,
                    t.cotizacion AS valor_pagado,
                    e.ID_equipo AS imei,
                    e.Color,
                    e.Capacidad,
                    p.Nombre_producto AS producto_nombre,
                    p.Descripcion AS producto_descripcion,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    c.Celular_cliente AS cliente_celular,
                    c.Correo_cliente AS cliente_correo,
                    cl.Nombre_Clase AS clase,
                    m.Nombre_marca AS marca
                FROM Trade_in t
                LEFT JOIN Equipo e ON t.ID_equipo = e.ID_equipo
                LEFT JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Cliente c ON t.ID_cliente = c.ID_cliente
                LEFT JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                LEFT JOIN Marca_producto m ON p.ID_marca = m.ID_marca
                ORDER BY t.Fecha_realizado DESC
            """)
            resultados = cursor.fetchall()
            
            # Agregar información de fotos y tests
            for trade in resultados:
                trade["fotos"] = self.obtener_fotos_trade_in(trade["id"])
                trade["tests"] = self.obtener_tests_trade_in(trade["id"])
            
            return resultados
        except Exception as e:
            print(f"Error en obtener_trade_ins: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def obtener_trade_ins_por_cliente(self, cliente_id: str) -> List[Dict[str, Any]]:
        """Obtiene el historial de trade-ins de un cliente específico"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    t.ID_Trade_in AS id,
                    t.Fecha_realizado AS fecha,
                    t.cotizacion AS valor_pagado,
                    p.Nombre_producto AS producto_nombre,
                    e.ID_equipo AS imei,
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
            print(f"Error en obtener_trade_ins_por_cliente: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    # ==================== OBTENER DETALLES ====================
    
    def obtener_detalle_trade_in(self, trade_in_id: str) -> Dict[str, Any]:
        """Obtiene el detalle completo de un trade-in"""
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
                    t.ID_equipo AS equipo_id,
                    t.Numero_utilizado,
                    t.Fecha_realizado AS fecha,
                    t.cotizacion AS valor_pagado,
                    e.ID_equipo AS imei,
                    e.Color,
                    e.Capacidad,
                    e.Clave,
                    e.Patron,
                    p.ID_producto AS producto_id,
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
                ORDER BY ID_foto_trade_in ASC
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
                    t.Nombre_test AS nombre,
                    t.Resultado_test AS resultado
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
    
    # ==================== ESTADÍSTICAS ====================
    
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
            
            # Valor total pagado
            cursor.execute("SELECT COALESCE(SUM(cotizacion), 0) AS valor_total FROM Trade_in")
            valor_total = cursor.fetchone() or {}
            
            # Total de equipos únicos
            cursor.execute("SELECT COUNT(DISTINCT ID_equipo) AS equipos FROM Trade_in")
            equipos = cursor.fetchone() or {}
            
            return {
                "total": total.get("total", 0),
                "valor_total": float(valor_total.get("valor_total", 0)),
                "equipos": equipos.get("equipos", 0)
            }
        except Exception as e:
            print(f"Error en obtener_estadisticas: {e}")
            return {}
        finally:
            cursor.close()
            db.close()
    
    # ==================== CATÁLOGOS PARA FORMULARIOS ====================
    
    def obtener_productos_disponibles(self) -> List[Dict[str, Any]]:
        """
        Obtiene productos disponibles para registrar en trade-in.
        SOLO se muestran iPhones (teléfonos de marca Apple).
        """
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            # Consulta filtrada para obtener solo iPhones (teléfonos Apple)
            cursor.execute("""
                SELECT 
                    p.ID_producto AS id,
                    p.Nombre_producto AS nombre,
                    cl.Nombre_Clase AS clase,
                    m.Nombre_marca AS marca,
                    m.ID_marca AS id_marca,
                    cl.ID_Clase AS id_clase
                FROM Producto p
                INNER JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                INNER JOIN Marca_producto m ON p.ID_marca = m.ID_marca
                WHERE cl.ID_Clase = '1' 
                  AND m.ID_marca = '1'
                  AND p.Nombre_producto NOT LIKE '%funda%'
                  AND p.Nombre_producto NOT LIKE '%cargador%'
                  AND p.Nombre_producto NOT LIKE '%pantalla%'
                  AND p.Nombre_producto NOT LIKE '%protector%'
                  AND p.Nombre_producto NOT LIKE '%mica%'
                  AND p.Nombre_producto NOT LIKE '%case%'
                  AND p.Nombre_producto NOT LIKE '%cover%'
                  AND p.Nombre_producto NOT LIKE '%cable%'
                  AND p.Nombre_producto NOT LIKE '%audifonos%'
                  AND p.Nombre_producto NOT LIKE '%airpods%'
                ORDER BY p.Nombre_producto
            """)
            resultados = cursor.fetchall()
            
            # Si no hay resultados con el filtro exacto, usar filtro más amplio
            if not resultados:
                cursor.execute("""
                    SELECT 
                        p.ID_producto AS id,
                        p.Nombre_producto AS nombre,
                        cl.Nombre_Clase AS clase,
                        m.Nombre_marca AS marca,
                        m.ID_marca AS id_marca,
                        cl.ID_Clase AS id_clase
                    FROM Producto p
                    INNER JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                    INNER JOIN Marca_producto m ON p.ID_marca = m.ID_marca
                    WHERE (cl.ID_Clase = '1' OR cl.Nombre_Clase = 'Telefono')
                      AND (m.ID_marca = '1' OR m.Nombre_marca = 'Apple')
                    ORDER BY p.Nombre_producto
                """)
                resultados = cursor.fetchall()
            
            return resultados
            
        except Exception as e:
            print(f"Error en obtener_productos_disponibles: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def obtener_clientes(self, q: str = None) -> List[Dict[str, Any]]:
        """Obtiene clientes para buscar en el registro"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            query = """
                SELECT 
                    c.ID_cliente AS id,
                    pn.Nombre_cliente AS nombre,
                    pn.Apellido_cliente AS apellido,
                    c.Celular_cliente AS celular,
                    c.Correo_cliente AS correo,
                    CONCAT(pn.Nombre_cliente, ' ', pn.Apellido_cliente) AS nombre_completo
                FROM Cliente c
                INNER JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
            """
            params = []
            
            if q:
                query += " WHERE c.ID_cliente LIKE %s OR pn.Nombre_cliente LIKE %s OR pn.Apellido_cliente LIKE %s"
                search = f"%{q}%"
                params = [search, search, search]
            
            query += " ORDER BY pn.Nombre_cliente ASC LIMIT 20"
            
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en obtener_clientes: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def verificar_equipo_existente(self, id_equipo: str) -> Optional[Dict[str, Any]]:
        """
        Verifica si un equipo ya existe por su ID (IMEI)
        Retorna la información del equipo si existe
        """
        db = self._conexion()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    e.ID_equipo,
                    e.Color,
                    e.Capacidad,
                    p.Nombre_producto AS producto_nombre,
                    p.ID_producto AS producto_id
                FROM Equipo e
                LEFT JOIN Producto p ON e.ID_producto = p.ID_producto
                WHERE e.ID_equipo = %s
            """, (id_equipo,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error en verificar_equipo_existente: {e}")
            return None
        finally:
            cursor.close()
            db.close()
    
    # ==================== ELIMINAR ====================
    
    def eliminar_trade_in(self, trade_in_id: str) -> Dict[str, Any]:
        """Elimina un trade-in"""
        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error de conexión"}
        
        cursor = db.cursor()
        try:
            # Primero eliminar fotos
            cursor.execute("DELETE FROM Fotos_trade_in WHERE ID_Trade_in = %s", (trade_in_id,))
            
            # Eliminar relaciones de tests
            cursor.execute("DELETE FROM Test_realizados_trade_in WHERE ID_Trade_in = %s", (trade_in_id,))
            
            # Eliminar trade-in
            cursor.execute("DELETE FROM Trade_in WHERE ID_Trade_in = %s", (trade_in_id,))
            
            db.commit()
            return {"success": True, "message": "Trade-in eliminado correctamente"}
        except Exception as e:
            db.rollback()
            print(f"Error en eliminar_trade_in: {e}")
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
            db.close()