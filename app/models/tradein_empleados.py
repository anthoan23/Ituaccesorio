from __future__ import annotations
from app.models.database import conectar
from app.models.bitacora import Bitacora
from app.models.equipo import Equipo
from datetime import datetime
from typing import List, Dict, Any, Optional
import json


class TradeInEmpleados:
    """Modelo para la gestión de Trade-In por parte de empleados"""
    
    def __init__(self, trade_in_id: str = None, empleado_id: str = None, 
                 cliente_id: str = None, id_producto: str = None, 
                 id_equipo: str = None, valor_pagado: float = None,
                 usuario_id: str = None, color: str = None, 
                 capacidad: str = None, clave: str = None, patron: str = None,
                 observaciones: str = None):
        self.trade_in_id = trade_in_id
        self.empleado_id = empleado_id
        self.cliente_id = cliente_id
        self.id_producto = id_producto
        self.id_equipo = id_equipo
        self.valor_pagado = valor_pagado
        self.usuario_id = usuario_id
        self.color = color
        self.capacidad = capacidad
        self.clave = clave
        self.patron = patron
        self.observaciones = observaciones
        self.__conexion_bd = conectar()
    
    def _conexion(self):
        return self.__conexion_bd.conexion1()
    
    def _generar_id_trade_in(self) -> str:
        """Genera un nuevo ID para Trade_in (formato TRD000001)"""
        db = self._conexion()
        if not db:
            return "TRD000001"
        
        cursor = db.cursor()
        try:
            cursor.execute("SELECT MAX(ID_Trade_in) FROM Trade_in")
            row = cursor.fetchone()
            ultimo_id = row[0] if row and row[0] else None
            
            if ultimo_id:
                try:
                    num_str = ultimo_id[3:]
                    num = int(num_str)
                    siguiente = num + 1
                except (ValueError, IndexError):
                    siguiente = 1
            else:
                siguiente = 1
            
            return f"TRD{str(siguiente).zfill(6)}"
        except Exception as e:
            print(f"Error generando ID trade-in: {e}")
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
                    num_str = ultimo_id[3:]
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

    def _generar_id_test(self) -> str:
        """Genera ID para Test (formato TST000001)"""
        db = self._conexion()
        if not db:
            return "TST000001"
        
        cursor = db.cursor()
        try:
            cursor.execute("SELECT MAX(ID_test) FROM Test")
            row = cursor.fetchone()
            ultimo_id = row[0] if row and row[0] else None
            
            if ultimo_id:
                try:
                    num_str = ultimo_id[3:]
                    num = int(num_str)
                    siguiente = num + 1
                except (ValueError, IndexError):
                    siguiente = 1
            else:
                siguiente = 1
            
            return f"TST{str(siguiente).zfill(6)}"
        except Exception as e:
            print(f"Error generando ID test: {e}")
            return f"TST{datetime.now().strftime('%Y%m%d%H%M%S')}"
        finally:
            cursor.close()
            db.close()
    
    # ==================== REGISTRAR NUEVO TRADE-IN ====================
    
    def registrar_trade_in(self, fotos: List[str] = None, tests: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Registra un nuevo equipo recibido en trade-in con sus tests"""
        if not self.cliente_id:
            return {"success": False, "error": "Debe seleccionar un cliente"}
        if not self.id_producto:
            return {"success": False, "error": "Debe seleccionar un producto/modelo"}
        if not self.id_equipo:
            return {"success": False, "error": "Debe ingresar el IMEI/ID del equipo"}
        if not self.valor_pagado:
            return {"success": False, "error": "Debe ingresar el valor pagado"}
        
        # Validar que el IMEI no tenga espacios
        if ' ' in self.id_equipo:
            return {"success": False, "error": "El IMEI no debe contener espacios"}
        
        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error de conexión a la base de datos"}
        
        cursor = db.cursor()
        try:
            # 1. Verificar si el equipo ya existe por IMEI
            cursor.execute("SELECT ID_equipo, ID_producto FROM Equipo WHERE ID_equipo = %s", (self.id_equipo,))
            equipo_existente = cursor.fetchone()
            
            if equipo_existente:
                # El equipo ya existe - actualizar datos si es necesario
                equipo_id = self.id_equipo
                equipo_producto_id = equipo_existente[1] if len(equipo_existente) > 1 else None
                
                if equipo_producto_id != self.id_producto:
                    equipo = Equipo(
                        ID_equipo=self.id_equipo,
                        ID_producto=self.id_producto,
                        Color=self.color,
                        Capacidad=self.capacidad,
                        Clave=self.clave,
                        Patron=self.patron
                    )
                    resultado = equipo.actualizar_equipo()
                    if "Error" in resultado and "no se encontró" not in resultado:
                        print(f"Advertencia al actualizar equipo: {resultado}")
                else:
                    if self.color or self.capacidad or self.clave or self.patron:
                        equipo = Equipo(
                            ID_equipo=self.id_equipo,
                            ID_producto=None,
                            Color=self.color,
                            Capacidad=self.capacidad,
                            Clave=self.clave,
                            Patron=self.patron
                        )
                        resultado = equipo.actualizar_equipo()
                        if "Error" in resultado and "no se encontró" not in resultado:
                            print(f"Advertencia al actualizar equipo: {resultado}")
            else:
                # 2. Crear NUEVO equipo con el producto asociado
                equipo = Equipo(
                    ID_equipo=self.id_equipo,
                    ID_producto=self.id_producto,
                    Color=self.color,
                    Capacidad=self.capacidad,
                    Clave=self.clave,
                    Patron=self.patron
                )
                resultado = equipo.registrar_equipo()
                if "Error" in resultado:
                    return {"success": False, "error": resultado}
            
            # 3. Generar ID y registrar trade-in
            self.trade_in_id = self._generar_id_trade_in()
            fecha_actual = datetime.now()
            
            cursor.execute("""
                INSERT INTO Trade_in (ID_Trade_in, ID_empleado, ID_cliente, ID_equipo, Numero_utilizado, Fecha_realizado, cotizacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                self.trade_in_id, 
                self.empleado_id, 
                self.cliente_id, 
                self.id_equipo,
                0, 
                fecha_actual, 
                self.valor_pagado
            ))
            
            # 4. Guardar fotos
            if fotos:
                for foto_url in fotos:
                    id_foto = self._generar_id_foto_trade_in()
                    cursor.execute("""
                        INSERT INTO Fotos_trade_in (ID_foto_trade_in, ID_Trade_in, Foto_trade_in)
                        VALUES (%s, %s, %s)
                    """, (id_foto, self.trade_in_id, foto_url))
            
            # 5. Guardar tests
            if tests:
                for test in tests:
                    nombre = test.get("nombre", "")
                    resultado = test.get("resultado", "")
                    
                    if nombre:
                        test_id = self._generar_id_test()
                        cursor.execute("""
                            INSERT INTO Test (ID_test, Numero_test, Nombre_test, Resultado_test)
                            VALUES (%s, %s, %s, %s)
                        """, (test_id, 1, nombre, resultado))
                        
                        cursor.execute("""
                            INSERT INTO Test_realizados_trade_in (ID_Trade_in, ID_test)
                            VALUES (%s, %s)
                        """, (self.trade_in_id, test_id))
            
            db.commit()
            
            # Registrar en bitácora
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Registrar Trade-in",
                    descripcion=f"Se registró nuevo trade-in ID: {self.trade_in_id} - Cliente: {self.cliente_id} - Equipo: {self.id_equipo} - Producto: {self.id_producto} - Valor: {self.valor_pagado} - Tests: {len(tests) if tests else 0}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Trade-in"
                )
                bitacora.registrar()
            
            return {
                "success": True,
                "message": "Trade-in registrado correctamente",
                "trade_in_id": self.trade_in_id,
                "equipo_id": self.id_equipo,
                "tests_registrados": len(tests) if tests else 0
            }
            
        except Exception as e:
            db.rollback()
            print(f"Error en registrar_trade_in: {e}")
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
            db.close()
    
    # ==================== ACTUALIZAR TRADE-IN ====================
    
    def actualizar_trade_in(self, fotos: List[str] = None, tests: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Actualiza un trade-in existente"""
        if not self.trade_in_id:
            return {"success": False, "error": "ID de trade-in no especificado"}
        
        if ' ' in self.id_equipo:
            return {"success": False, "error": "El IMEI no debe contener espacios"}
        
        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error de conexión a la base de datos"}
        
        cursor = db.cursor()
        try:
            # 1. Verificar si el equipo existe y actualizar
            cursor.execute("SELECT ID_equipo FROM Equipo WHERE ID_equipo = %s", (self.id_equipo,))
            equipo_existente = cursor.fetchone()
            
            if equipo_existente:
                equipo = Equipo(
                    ID_equipo=self.id_equipo,
                    ID_producto=self.id_producto,
                    Color=self.color,
                    Capacidad=self.capacidad,
                    Clave=self.clave,
                    Patron=self.patron
                )
                resultado = equipo.actualizar_equipo()
                if "Error" in resultado and "no se encontró" not in resultado:
                    print(f"Advertencia al actualizar equipo: {resultado}")
            else:
                equipo = Equipo(
                    ID_equipo=self.id_equipo,
                    ID_producto=self.id_producto,
                    Color=self.color,
                    Capacidad=self.capacidad,
                    Clave=self.clave,
                    Patron=self.patron
                )
                resultado = equipo.registrar_equipo()
                if "Error" in resultado:
                    return {"success": False, "error": resultado}
            
            # 2. Actualizar el trade-in
            cursor.execute("""
                UPDATE Trade_in 
                SET ID_empleado = %s, 
                    ID_cliente = %s, 
                    ID_equipo = %s, 
                    cotizacion = %s
                WHERE ID_Trade_in = %s
            """, (
                self.empleado_id, 
                self.cliente_id, 
                self.id_equipo,
                self.valor_pagado,
                self.trade_in_id
            ))
            
            # 3. Actualizar fotos
            cursor.execute("DELETE FROM Fotos_trade_in WHERE ID_Trade_in = %s", (self.trade_in_id,))
            if fotos:
                for foto_url in fotos:
                    id_foto = self._generar_id_foto_trade_in()
                    cursor.execute("""
                        INSERT INTO Fotos_trade_in (ID_foto_trade_in, ID_Trade_in, Foto_trade_in)
                        VALUES (%s, %s, %s)
                    """, (id_foto, self.trade_in_id, foto_url))
            
            # 4. Actualizar tests
            if tests is not None:
                # Eliminar tests existentes
                cursor.execute("""
                    DELETE tr FROM Test_realizados_trade_in tr
                    INNER JOIN Test t ON tr.ID_test = t.ID_test
                    WHERE tr.ID_Trade_in = %s
                """, (self.trade_in_id,))
                
                # Registrar nuevos tests
                for test in tests:
                    nombre = test.get("nombre", "")
                    resultado = test.get("resultado", "")
                    
                    if nombre:
                        test_id = self._generar_id_test()
                        cursor.execute("""
                            INSERT INTO Test (ID_test, Numero_test, Nombre_test, Resultado_test)
                            VALUES (%s, %s, %s, %s)
                        """, (test_id, 1, nombre, resultado))
                        
                        cursor.execute("""
                            INSERT INTO Test_realizados_trade_in (ID_Trade_in, ID_test)
                            VALUES (%s, %s)
                        """, (self.trade_in_id, test_id))
            
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Modificar Trade-in",
                    descripcion=f"Se modificó el trade-in ID: {self.trade_in_id}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Trade-in"
                )
                bitacora.registrar()
            
            return {
                "success": True,
                "message": "Trade-in actualizado correctamente",
                "trade_in_id": self.trade_in_id
            }
            
        except Exception as e:
            db.rollback()
            print(f"Error en actualizar_trade_in: {e}")
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
            db.close()
    
    # ==================== ELIMINAR TRADE-IN ====================
    
    def eliminar_trade_in(self) -> Dict[str, Any]:
        """Elimina un trade-in y sus relaciones"""
        if not self.trade_in_id:
            return {"success": False, "error": "ID de trade-in no especificado"}
        
        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error de conexión"}
        
        cursor = db.cursor()
        try:
            # Eliminar fotos asociadas
            cursor.execute("DELETE FROM Fotos_trade_in WHERE ID_Trade_in = %s", (self.trade_in_id,))
            
            # Eliminar tests asociados
            cursor.execute("""
                DELETE tr FROM Test_realizados_trade_in tr
                INNER JOIN Test t ON tr.ID_test = t.ID_test
                WHERE tr.ID_Trade_in = %s
            """, (self.trade_in_id,))
            
            # Eliminar el trade-in
            cursor.execute("DELETE FROM Trade_in WHERE ID_Trade_in = %s", (self.trade_in_id,))
            
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Eliminar Trade-in",
                    descripcion=f"Se eliminó el trade-in ID: {self.trade_in_id}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Trade-in"
                )
                bitacora.registrar()
            
            return {"success": True, "message": "Trade-in eliminado correctamente"}
        except Exception as e:
            db.rollback()
            print(f"Error en eliminar_trade_in: {e}")
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
                    -- Datos del equipo
                    e.Color,
                    e.Capacidad,
                    e.Clave,
                    e.Patron,
                    -- Datos del producto
                    p.ID_producto AS producto_id,
                    p.Nombre_producto AS producto_nombre,
                    p.Descripcion AS producto_descripcion,
                    -- Datos de clase y marca
                    cl.Nombre_Clase AS clase,
                    m.Nombre_marca AS marca,
                    m.ID_marca AS id_marca,
                    cl.ID_Clase AS id_clase,
                    -- Datos del cliente
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    c.Celular_cliente AS cliente_celular,
                    c.Correo_cliente AS cliente_correo,
                    c.Direccion_cliente AS cliente_direccion,
                    -- Datos del empleado
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
                ORDER BY t.Fecha_realizado DESC
            """)
            resultados = cursor.fetchall()
            
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
    
    def obtener_trade_ins_por_cliente(self) -> List[Dict[str, Any]]:
        """Obtiene el historial de trade-ins de un cliente específico"""
        if not self.cliente_id:
            return []
        
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
                    e.Color,
                    e.Capacidad,
                    m.Nombre_marca AS marca,
                    cl.Nombre_Clase AS clase
                FROM Trade_in t
                LEFT JOIN Equipo e ON t.ID_equipo = e.ID_equipo
                LEFT JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto m ON p.ID_marca = m.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                WHERE t.ID_cliente = %s
                ORDER BY t.Fecha_realizado DESC
            """, (self.cliente_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en obtener_trade_ins_por_cliente: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    # ==================== OBTENER DETALLES ====================
    
    def obtener_detalle_trade_in(self) -> Dict[str, Any]:
        """Obtiene el detalle completo de un trade-in"""
        if not self.trade_in_id:
            return {}
        
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
                    -- Datos del equipo
                    e.ID_equipo AS imei,
                    e.Color,
                    e.Capacidad,
                    e.Clave,
                    e.Patron,
                    -- Datos del producto
                    p.ID_producto AS producto_id,
                    p.Nombre_producto AS producto_nombre,
                    p.Descripcion AS producto_descripcion,
                    -- Datos de clase y marca
                    cl.Nombre_Clase AS clase,
                    m.Nombre_marca AS marca,
                    -- Datos del cliente
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    c.Celular_cliente AS cliente_celular,
                    c.Correo_cliente AS cliente_correo,
                    c.Direccion_cliente AS cliente_direccion,
                    -- Datos del empleado
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
            """, (self.trade_in_id,))
            return cursor.fetchone() or {}
        except Exception as e:
            print(f"Error en obtener_detalle_trade_in: {e}")
            return {}
        finally:
            cursor.close()
            db.close()
    
    def obtener_fotos_trade_in(self, trade_in_id: str = None) -> List[Dict[str, Any]]:
        """Obtiene las fotos asociadas a un trade-in"""
        trade_id = trade_in_id or self.trade_in_id
        if not trade_id:
            return []
        
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
            """, (trade_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en obtener_fotos_trade_in: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def obtener_tests_trade_in(self, trade_in_id: str = None) -> List[Dict[str, Any]]:
        """Obtiene los tests realizados para un trade-in"""
        trade_id = trade_in_id or self.trade_in_id
        if not trade_id:
            return []
        
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
            """, (trade_id,))
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
            cursor.execute("SELECT COUNT(*) AS total FROM Trade_in")
            total = cursor.fetchone() or {}
            
            cursor.execute("SELECT COALESCE(SUM(cotizacion), 0) AS valor_total FROM Trade_in")
            valor_total = cursor.fetchone() or {}
            
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
        """Obtiene productos disponibles para registrar en trade-in (solo iPhones)"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
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
                  AND (m.ID_marca = '1' OR m.Nombre_marca LIKE '%Iphone%' OR m.Nombre_marca LIKE '%Apple%')
                ORDER BY p.Nombre_producto
            """)
            return cursor.fetchall()
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
    
    def verificar_equipo_existente(self) -> Optional[Dict[str, Any]]:
        """Verifica si un equipo ya existe por su ID (IMEI) y trae sus datos"""
        if not self.id_equipo:
            return None
        
        db = self._conexion()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    e.ID_equipo,
                    e.ID_producto,
                    e.Color,
                    e.Capacidad,
                    e.Clave,
                    e.Patron,
                    p.Nombre_producto AS producto_nombre,
                    p.ID_producto AS producto_id,
                    m.Nombre_marca AS marca,
                    cl.Nombre_Clase AS clase
                FROM Equipo e
                LEFT JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto m ON p.ID_marca = m.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                WHERE e.ID_equipo = %s
            """, (self.id_equipo,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error en verificar_equipo_existente: {e}")
            return None
        finally:
            cursor.close()
            db.close()