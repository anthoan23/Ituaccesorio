from __future__ import annotations

import json
from app.models.database import conectar
from app.models.bitacora import Bitacora


class Tests():
    def __init__(self, ID_test=None, Numero_test=None, lista_tests=None, 
                 id_personal=None, capacidad=None, clave=None, patron=None, 
                 ID_orden=None, ID_empleado=None, usuario_id: str = None):
        self.ID_test = ID_test
        self.Numero_test = Numero_test
        self.lista_tests = lista_tests
        self.id_personal = id_personal
        self.capacidad = capacidad
        self.clave = clave
        self.patron = patron
        self.ID_orden = ID_orden
        self.ID_empleado = ID_empleado
        self.usuario_id = usuario_id  # Usuario que realiza la acción

        self._conexion = conectar()

    def buscar_test(self):
        id_orden = self.ID_orden
        db = self._conexion.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                "SELECT o.ID_orden, t.*, oe.Costo_reparacion "
                "FROM revision_orden o JOIN test t ON o.ID_test = t.ID_test "
                "JOIN orden_e oe ON o.ID_orden = oe.ID_orden_e WHERE o.ID_orden = %s"
            )
            cursor.execute(sql, (id_orden,))
            ordenes = cursor.fetchall()
        
            return ordenes
        
        finally:
            cursor.close()
            db.close()

    def listas_tests(self):
        db = self._conexion.conexion1()
        if not db:
            return None
        
        ID_orden = self.ID_orden
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = """
                    SELECT 
                        t.Numero_test,
                        COUNT(*) as cantidad
                    FROM Interaccion i 
                    JOIN Test_realizados_interaccion ti ON i.ID_interaccion = ti.ID_interaccion
                    JOIN Test t ON ti.ID_test = t.ID_test
                    WHERE i.ID_orden_servicio = %s
                    GROUP BY t.Numero_test
                    ORDER BY t.Numero_test ASC
                """
            cursor.execute(sql, (ID_orden,))
            tests = cursor.fetchall()
        
            return tests
        
        finally:
            cursor.close()
            db.close()

    def consultar_test(self):
        db = self._conexion.conexion1()
        if not db:
            return None
        
        # 1. Agregamos buffered=True para evitar bloqueos por resultados pendientes
        cursor = db.cursor(dictionary=True, buffered=True)
        try:
            sql = """SELECT 
                    t.Nombre_test as test,
                    t.Resultado_test
                    FROM Interaccion i 
                    JOIN Test_realizados_interaccion ti ON i.ID_interaccion = ti.ID_interaccion
                    JOIN Test t ON ti.ID_test = t.ID_test
                    where i.ID_orden_servicio = %s and t.Numero_test = %s"""
            cursor.execute(sql, (self.ID_orden, self.Numero_test))
            
            # 2. CORREGIDO: Cambiamos fetchone() por fetchall() para traer la lista completa
            test = cursor.fetchall() 
        
            return test
        
        finally:
            cursor.close()
            db.close()
    
    """ EDUIN NO TOQUES MI CODIGOOOOOOOOOOOO"""
    def registrar_revision_test(self) -> str:
        
        id_orden = self.ID_orden
        id_empleado = self.ID_empleado

        try:
            json_tests_string = json.dumps(self.lista_tests, ensure_ascii=False)
        except Exception as e:
            print(f"Error al serializar el lote de tests a JSON: {e}")
            return "El formato de la lista de pruebas es incorrecto."

        # 3. Establecer conexión con la Base de Datos
        db = self._conexion.conexion1()
        if not db:
            return "Error al conectar con la base de datos."
        
        cursor = db.cursor()
        try:
            # 4. Preparar la llamada al procedimiento exacto
            sql = 'CALL sp_registrar_revision_test(%s, %s, %s, %s)'
            valores = (id_orden, id_empleado, self.Numero_test, json_tests_string)
            
            cursor.execute(sql, valores)
            
            # Limpiar los conjuntos de resultados que genera el Procedure (MySQL exige vaciar los buffers)
            while cursor.nextset():
                pass
                
            db.commit()
            
            # Registrar en bitácora
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Registrar revisión técnica",
                    descripcion=f"Se registró revisión técnica para orden: {id_orden} - Test #{self.Numero_test}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Taller"
                )
                bitacora.registrar()
            
            return "Revisión técnica y pruebas registradas exitosamente."
            
        except Exception as e:
            print(f"Error al registrar la revisión técnica: {e}")
            db.rollback()
            return "Error interno al procesar el registro de las pruebas."
            
        finally:
            cursor.close()
            db.close()







# =============================================
# MÉTODO AGREGADO PARA EL FUNCIONAMIENTO DEL BLUEPRINT DE ÓRDENES DE SERVICIO
# =============================================

#NO BORRAR ESTO MMGVO ESTO LO ESTOY USANDO EN EL CONTROLADOR DE ORDENES DE SERVICIO

    def buscar_test_por_orden(self, id_orden: str) -> list:
        """Busca los tests asociados a una orden de servicio (para el detalle de la orden)"""
        if not id_orden:
            return []
        
        db = self._conexion.conexion1()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    t.Numero_test AS Num_test,
                    t.Nombre_test,
                    t.Resultado_test AS Observaciones,
                    t.ID_test
                FROM Test t
                INNER JOIN Test_realizados_interaccion tri ON t.ID_test = tri.ID_test
                INNER JOIN Interaccion i ON tri.ID_interaccion = i.ID_interaccion
                WHERE i.ID_orden_servicio = %s
                ORDER BY t.Numero_test DESC, t.ID_test
            """, (id_orden,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en buscar_test_por_orden: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def registrar_test(self, valores: tuple, id_orden: str) -> bool:
        """
        Registra un test individual en la base de datos.
        Este método es llamado desde el Blueprint de órdenes de servicio.
        
        valores: tupla con (ID_empleado, Num_test, Btn_power, Btn_vol, Cornetas, ...)
        id_orden: ID de la orden de servicio
        """
        db = self._conexion.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            # Extraer el ID del empleado y número de test
            empleado_id = valores[0]
            num_test = valores[1] if len(valores) > 1 and valores[1] is not None else 1
            
            # Generar ID para el test
            cursor.execute("SELECT MAX(ID_test) FROM Test")
            row = cursor.fetchone()
            ultimo_id = row[0] if row else None
            if not ultimo_id:
                nuevo_id = "TST000001"
            else:
                try:
                    num = int(ultimo_id[3:]) + 1
                except:
                    num = 1
                nuevo_id = f"TST{num:06d}"
            
            # Construir la lista de tests a partir de los valores
            # Los campos después del índice 1 son los resultados de los tests
            nombres_tests = [
                'Btn_power', 'Btn_vol', 'Cornetas', 'Mica', 'LCD', 'Tactil', 'Wifi',
                'Puerto_carga', 'Cam_pos', 'Cam_del', 'Microfono', 'Flash', 'Btn_sil',
                'Auricular', 'Senal', 'Sensor_proximidad', 'Face_id', 'Bluetooth'
            ]
            
            observaciones = None
            lista_tests = []
            
            # Recorrer los valores a partir del índice 2 (después de ID_em y Num_test)
            for i, nombre in enumerate(nombres_tests):
                idx = i + 2  # +2 porque los primeros 2 son ID_em y Num_test
                if idx < len(valores) and valores[idx] is not None:
                    resultado = "Funciona" if int(valores[idx]) == 1 else "No funciona"
                    lista_tests.append({
                        "nombre": nombre,
                        "resultado": resultado
                    })
            
            # Buscar observaciones (está al final de los valores)
            # Los valores tienen longitud fija, buscamos el campo Observaciones
            observaciones_idx = len(valores) - 1
            if observaciones_idx < len(valores) and valores[observaciones_idx]:
                observaciones = str(valores[observaciones_idx])
                lista_tests.append({
                    "nombre": "Observaciones",
                    "resultado": observaciones
                })
            
            # Si no hay tests que registrar, retornamos False
            if not lista_tests:
                print("No hay tests para registrar")
                return False
            
            # Insertar cada test individual en la tabla Test
            for test_item in lista_tests:
                cursor.execute("""
                    INSERT INTO Test (ID_test, Numero_test, Nombre_test, Resultado_test)
                    VALUES (%s, %s, %s, %s)
                """, (nuevo_id, num_test, test_item['nombre'][:30], test_item['resultado'][:300]))
                nuevo_id = f"TST{int(nuevo_id[3:]) + 1:06d}"
            
            # Obtener o crear interacción
            cursor.execute("""
                SELECT ID_interaccion FROM Interaccion 
                WHERE ID_orden_servicio = %s AND Accion = 'Revisión' 
                ORDER BY ID_interaccion DESC LIMIT 1
            """, (id_orden,))
            interaccion = cursor.fetchone()
            
            if not interaccion:
                # Crear nueva interacción
                cursor.execute("SELECT MAX(ID_interaccion) FROM Interaccion")
                row = cursor.fetchone()
                ultimo_int = row[0] if row else None
                if not ultimo_int:
                    nuevo_int = "INT000001"
                else:
                    try:
                        num = int(ultimo_int[3:]) + 1
                    except:
                        num = 1
                    nuevo_int = f"INT{num:06d}"
                
                cursor.execute("""
                    INSERT INTO Interaccion (ID_interaccion, ID_orden_servicio, ID_empleado, Accion)
                    VALUES (%s, %s, %s, 'Revisión')
                """, (nuevo_int, id_orden, empleado_id))
                interaccion_id = nuevo_int
            else:
                interaccion_id = interaccion[0]
            
            # Obtener los IDs de los tests recién insertados para la relación
            cursor.execute("""
                SELECT ID_test FROM Test 
                WHERE Numero_test = %s 
                ORDER BY ID_test DESC
                LIMIT %s
            """, (num_test, len(lista_tests)))
            tests_ids = cursor.fetchall()
            
            # Relacionar cada test con la interacción
            for test_id_row in tests_ids:
                cursor.execute("""
                    INSERT INTO Test_realizados_interaccion (ID_interaccion, ID_test)
                    VALUES (%s, %s)
                """, (interaccion_id, test_id_row[0]))
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error en registrar_test: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            cursor.close()
            db.close()