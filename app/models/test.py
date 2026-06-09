from __future__ import annotations

from flask import json

from app.models.database import conectar

class Tests():
    def __init__(self, ID_test=None, Numero_test= None, lista_tests=None, id_personal=None, capacidad=None, clave=None, patron=None, ID_orden=None, ID_empleado=None):
        self.ID_test = ID_test
        self.Numero_test = Numero_test
        self.lista_tests = lista_tests
        self.id_personal = id_personal
        self.capacidad = capacidad
        self.clave = clave
        self.patron = patron
        self.ID_orden = ID_orden
        self.ID_empleado = ID_empleado


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
            sql = """SELECT 
                        t.Numero_test,
                        COUNT(*) as cantidad
                    FROM Interaccion i 
                    JOIN Test_realizados_interaccion ti ON i.ID_interaccion = ti.ID_interaccion
                    JOIN Test t ON ti.ID_test = t.ID_test
                    WHERE i.Accion = 'Revisión' 
                    AND i.ID_orden_servicio = %s
                    GROUP BY t.Numero_test"""
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
    
   
    def registrar_revision_test(self ) -> str:
        
        # 1. Obtener y limpiar los identificadores base desde los atributos de la instancia
        id_orden = self.ID_orden.strip() 
        id_empleado = self.ID_empleado or 32014004 # Asumiendo que es un entero (INT)

        # Validaciones previas básicas
        if not id_orden or len(id_orden) > 10:
            return "El ID de la orden de servicio es inválido o excede los 10 caracteres."
        
        if not id_empleado:
            return "El ID del empleado es obligatorio."
        
        if not self.lista_tests or not isinstance(self.lista_tests, list):
            return "Debe proporcionar una lista válida con los componentes revisados."

        # 2. Convertir la lista/arreglo de Python a una cadena de texto en formato JSON estructurado
        # Esto asegura que vaya con las llaves que espera tu ciclo WHILE del procedure: $[i].nombre y $[i].resultado
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
            return "Revisión técnica y pruebas registradas exitosamente."
            
        except Exception as e:
            print(f"Error al registrar la revisión técnica: {e}")
            db.rollback()
            return "Error interno al procesar el registro de las pruebas."
            
        finally:
            cursor.close()
            db.close()


    
