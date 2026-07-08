from __future__ import annotations
from app.models.database import conectar

class James():
    def __init__(self, ID_orden: str = ""):
        self.ID_orden = ID_orden
        self.__conexion = conectar()

    def consultar_informacion_orden(self):
        db = self.__conexion.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje

        cursor = db.cursor(dictionary=True)
        try:
            # Consulta principal
            cursor.execute(
                """
                SELECT 
                    os.ID_orden_servicio AS id_orden,
                    os.Estado_orden_servicio AS estado_orden,
                    os.Descripcion_reparacion AS descripcion_reparacion,
                    os.Costo_reparacion AS costo_reparacion,
                    os.Nota_orden_servicio AS nota_orden,
                    os.Fecha_entrada AS fecha_entrada,
                    os.Fecha_salida AS fecha_salida,
                    e.ID_equipo AS id_equipo,
                    e.Color AS color_equipo,
                    e.Capacidad AS capacidad_equipo,
                    prod.ID_producto AS id_producto,
                    prod.Nombre_producto AS nombre_producto,
                    prod.Descripcion AS descripcion_producto,
                    cp.Nombre_Clase AS clase_producto,
                    mp.Nombre_marca AS marca_producto
                FROM Orden_servicio os
                INNER JOIN Cliente c ON os.ID_cliente = c.ID_cliente
                LEFT JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                INNER JOIN Equipo e ON os.ID_equipo = e.ID_equipo
                INNER JOIN Producto prod ON e.ID_producto = prod.ID_producto
                INNER JOIN Clase_producto cp ON prod.ID_Clase = cp.ID_Clase
                INNER JOIN Marca_producto mp ON prod.ID_marca = mp.ID_marca
                WHERE os.ID_orden_servicio = %s
                """,
                (self.ID_orden,)
            )
            resultado_orden = cursor.fetchone()
            
            if not resultado_orden:
                return f"No se encontró ninguna orden con ID '{self.ID_orden}'."
            
            # Consulta de interacciones y tests (CORREGIDA)
            cursor.execute(
                """
                SELECT 
                    i.ID_interaccion AS id_interaccion,
                    i.Accion AS accion_interaccion,
                    i.ID_empleado AS id_empleado_interaccion,
                    t.ID_test AS id_test,
                    t.Numero_test AS numero_test,
                    t.Nombre_test AS nombre_test,
                    t.Resultado_test AS resultado_test
                FROM Interaccion i
                LEFT JOIN Test_realizados_interaccion tri ON i.ID_interaccion = tri.ID_interaccion
                LEFT JOIN Test t ON tri.ID_test = t.ID_test
                WHERE i.ID_orden_servicio = %s
                ORDER BY i.ID_interaccion ASC
                """,
                (self.ID_orden,)
            )
            resultados_interacciones = cursor.fetchall()
            
            interacciones_agrupadas = {}
            for row in resultados_interacciones:
                id_interaccion = row['id_interaccion']
                if id_interaccion not in interacciones_agrupadas:
                    interacciones_agrupadas[id_interaccion] = {
                        'id_interaccion': id_interaccion,
                        'accion_interaccion': row['accion_interaccion'],
                        'id_empleado_interaccion': row['id_empleado_interaccion'],
                        'tests': []
                    }
                if row['id_test']:
                    interacciones_agrupadas[id_interaccion]['tests'].append({
                        'id_test': row['id_test'],
                        'numero_test': row['numero_test'],
                        'nombre_test': row['nombre_test'],
                        'resultado_test': row['resultado_test']
                    })
            
            interacciones_lista = list(interacciones_agrupadas.values())
            
            resultado_completo = {
                'orden': resultado_orden,
                'interacciones': interacciones_lista,
                'resumen': {
                    'total_interacciones': len(interacciones_lista),
                    'total_tests': sum(len(interaccion['tests']) for interaccion in interacciones_lista),
                    'estado_actual': resultado_orden['estado_orden']
                }
            }
            
            return resultado_completo
            
        except Exception as e:
            return f"Error al consultar la información: {str(e)}"
      

    def consultar_tecnicos_con_especialidades_y_ordenes(self):
        db = self.__conexion.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor(dictionary=True)
        try:
            # Consulta CORREGIDA con todas las columnas necesarias
            cursor.execute(
                """
                SELECT 
                    e.ID_empleado AS id_empleado,
                    c.Nombre_cargo AS nombre_cargo,
                    esp.Nombre_especialidad AS nombre_especialidad,
                    esp.Descripcion_especialidad as descripcion_especialidad,
                    cap.Nivel_Capacitacion AS nivel_capacitacion,
                    (
                        SELECT COUNT(DISTINCT i.ID_orden_servicio)
                        FROM Interaccion i
                        WHERE i.ID_empleado = e.ID_empleado
                          AND i.Accion = 'Asignada'
                    ) AS total_ordenes_asignadas
                FROM Empleado e
                INNER JOIN Cargo c ON e.ID_cargo = c.ID_cargo
                INNER JOIN Capacitacion cap ON e.ID_empleado = cap.ID_empleado
                INNER JOIN Especialidad esp ON cap.ID_especialidad = esp.ID_especialidad
                WHERE c.Nombre_cargo LIKE '%Técnico%' 
                ORDER BY e.ID_empleado, esp.Nombre_especialidad
                """
            )
            resultados = cursor.fetchall()
            
            if not resultados:
                return "No se encontraron técnicos registrados."
            
            tecnicos_dict = {}
            for row in resultados:
                id_emp = row['id_empleado']
                if id_emp not in tecnicos_dict:
                    tecnicos_dict[id_emp] = {
                        'id_empleado': id_emp,
                        'cargo': row['nombre_cargo'],
                        'total_ordenes_asignadas': row['total_ordenes_asignadas'],
                        'especialidades': []
                    }
                
                tecnicos_dict[id_emp]['especialidades'].append({
                    'nombre_especialidad': row['nombre_especialidad'],
                    'descripcion_especialidad': row['descripcion_especialidad'],
                    'nivel_capacitacion': row['nivel_capacitacion']
                })
            
            resultado = list(tecnicos_dict.values())
            resultado.sort(key=lambda x: x['total_ordenes_asignadas'], reverse=True)
            
            return {
                'total_tecnicos': len(resultado),
                'tecnicos': resultado
            }
            
        except Exception as e:
            return f"Error al consultar técnicos: {str(e)}"
        finally:
            cursor.close()
            db.close()