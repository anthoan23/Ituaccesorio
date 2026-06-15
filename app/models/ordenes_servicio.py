from __future__ import annotations
from app.models.database import conectar
from datetime import date
from app.models.empleados import empleado


class Orden_servicio():
    def __init__(self, ID_orden_servicio: int = None, Estado_orden_servicio: str = None, Descripcion_reparacion: str = None, Costo_reparacion: float = None, Nota_orden_servicio: str = None, Fecha_entrada = None, Fecha_salida = None, ID_foto_orden_servicio: str = None, Foto_orden_servicio: str = None, ID_empleado: int = None, lista_repuestos=None):
        self.ID_orden_servicio = ID_orden_servicio
        self.Estado_orden_servicio = Estado_orden_servicio
        self.Descripcion_reparacion = Descripcion_reparacion
        self.Costo_reparacion = Costo_reparacion
        self.Nota_orden_servicio = Nota_orden_servicio
        self.ID_empleado = ID_empleado
        self.Fecha_entrada = Fecha_entrada
        self.Fecha_salida = Fecha_salida
        self.ID_foto_orden_servicio = ID_foto_orden_servicio
        self.Foto_orden_servicio = Foto_orden_servicio
        self.lista_repuestos = lista_repuestos

        self._conexion = conectar()

    def listar_Orden_servicio(self):
        db = self._conexion.conexion1()
        if not db:
            mensaje = "Error al conectar con la base de datos."
            return mensaje
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    os.ID_orden_servicio AS id_orden,
                    os.Estado_orden_servicio AS estado,
                    os.Descripcion_reparacion AS descripcion,
                    os.Costo_reparacion AS costo,
                    os.Nota_orden_servicio AS nota,
                    os.Fecha_entrada AS fecha_e,
                    os.Fecha_salida AS fecha_s
                FROM Orden_servicio os
                JOIN Equipo e ON os.ID_equipo = e.ID_equipo
                JOIN Fotos_orden_servicio fot ON os.ID_orden_servicio = fot.ID_orden_servicio
                ORDER BY os.ID_orden_servicio DESC
                """
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar órdenes de servicio: {e}")
            return []
        finally:
            cursor.close()
            db.close()


    def listar_ordenes_taller(self):
        db = self._conexion.conexion1()
        if not db:
            mensaje = "Error al conectar con la base de datos."
            return mensaje
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    os.ID_orden_servicio AS id_orden,
                    os.Estado_orden_servicio AS estado,
                    os.ID_cliente as id_cliente,
                    CASE 
                        WHEN pn.ID_cliente IS NOT NULL THEN CONCAT(pn.Nombre_cliente, ' ', pn.Apellido_cliente)
                        WHEN cj.ID_cliente IS NOT NULL THEN cj.Razon_social
                        ELSE 'Cliente no especificado'
                    END AS nombre_cliente,
                    p.Nombre_producto AS modelo,
                    os.Descripcion_reparacion AS descripcion,       
                    os.Fecha_entrada AS fecha_e      
                FROM Orden_servicio os
                INNER JOIN Equipo e ON os.ID_equipo = e.ID_equipo
                INNER JOIN Cliente c ON os.ID_cliente = c.ID_cliente
                LEFT JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente_juridico cj ON c.ID_cliente = cj.ID_cliente
                INNER JOIN Producto p ON e.ID_producto = p.ID_producto
                WHERE os.Estado_orden_servicio IN ('Pendiente', 'En Proceso')
                ORDER BY os.ID_orden_servicio DESC;
                """
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar órdenes de taller: {e}")
            return []
        finally:
            cursor.close()
            db.close()

        
    def listar_ordenes_tecnico(self):
        empleado_id = self.ID_empleado
        db = self._conexion.conexion1()
        if not db:
            mensaje = "Error al conectar con la base de datos."
            return mensaje
        
        cursor = db.cursor(dictionary=True)
        try:
            sql ="""
                SELECT 
                o.ID_orden_servicio AS id_orden,                 
                p.Nombre_producto AS modelo,
                o.Descripcion_reparacion AS descripcion,       
                o.Fecha_entrada AS fecha_e 

                FROM Orden_servicio o 
                INNER JOIN Equipo e ON o.ID_equipo = e.ID_equipo
                INNER JOIN Producto p ON e.ID_producto = p.ID_producto
                INNER JOIN Interaccion i ON o.ID_orden_servicio = i.ID_orden_servicio
                where o.Estado_orden_servicio = 'Asignada' And i.Accion =  'Asignada' and i.ID_empleado = %s

                """
            cursor.execute(sql, (empleado_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar órdenes de taller: {e}")
            return []
        finally:
            cursor.close()
            db.close()


    def consultar_orden(self,):
        id_orden = self.ID_orden_servicio
        db = self._conexion.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            sql =""" SELECT o.*, 
                p.Nombre_producto AS Modelo, 
                o.Estado_orden_servicio AS Estado,
                CASE 
                        WHEN pn.ID_cliente IS NOT NULL THEN CONCAT(pn.Nombre_cliente, ' ', pn.Apellido_cliente)
                        WHEN cj.ID_cliente IS NOT NULL THEN cj.Razon_social
                        ELSE 'Cliente no especificado'
                    END AS nombre_cliente,
                o.Descripcion_reparacion AS Descripcion,
                o.Nota_orden_servicio AS Nota
                FROM Orden_servicio o JOIN Equipo e ON o.ID_equipo = e.ID_equipo 
                JOIN Cliente c ON o.ID_cliente = c.ID_cliente
                JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente_juridico cj ON c.ID_cliente = cj.ID_cliente
                WHERE o.ID_orden_servicio = %s"""

            
            cursor.execute(sql, (id_orden,))
            orden = cursor.fetchone()
        
            return orden
        
        finally:
            cursor.close()
            db.close()

    def empleados_Asignadas(self, id_orden: int):
        db = self._conexion.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                "SELECT i.Accion, e.* "
                "FROM Interaccion i JOIN Empleado e ON i.ID_empleado = e.ID_empleado "
                "WHERE i.ID_orden_servicio = %s"
            )
            cursor.execute(sql, (id_orden,))
            empleados = cursor.fetchall()
        
            return empleados
        
        finally:
            cursor.close()
            db.close()

    def consultar_fotos_orden(self,):
        id_orden = self.ID_orden_servicio
        db = self._conexion.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                "SELECT * FROM Fotos_orden_servicio "
                "WHERE ID_orden_servicio = %s"
            )
            cursor.execute(sql, (id_orden,))
            fotos = cursor.fetchall()
        
            return fotos
        
        finally:
            cursor.close()
            db.close()

    
    def verificar_foto_existe_por_ruta(self) -> bool:
        ruta_foto = self.Foto_orden_servicio.strip()
     
        """Verifica si una foto existe por su ruta o nombre de archivo"""
        db = self._conexion.conexion1()
        if not db:
         return False

        cursor = db.cursor()
        try:
            cursor.execute(
            "SELECT 1 FROM Fotos_orden_servicio WHERE Ruta_foto = %s LIMIT 1",
            (ruta_foto.strip(),),
        )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()



    def agregar_foto_orden_servicio(self) -> str:
        id_foto = self.ID_foto_orden_servicio.strip()
        ruta_foto = self.Foto_orden_servicio.strip()

        if len(id_foto) > 10:
            return "El ID de la foto no puede tener más de 10 caracteres."
        
        if len(ruta_foto) > 255:
            return "La ruta de la foto no puede tener más de 255 caracteres."
        
        if self.verificar_foto_existe_por_ruta():
            mensaje = f"La foto '{ruta_foto}' ya existe."
            return mensaje

        db = self._conexion.conexion()
        if not db:
            mesaje = "Error al conectar con la base de datos."
            return mesaje
        
        cursor = db.cursor()
        try:
            sql = 'CALL Agregar_foto(%s, %s)' 
            cursor.execute(sql, (ruta_foto))
            while cursor.nextset():
                pass
            db.commit()
            mensaje = f"Foto agregada exitosamente."
            return mensaje
        except Exception as e:
            print(f"Error al agregar la foto: {e}")
            db.rollback()
            mensaje = "Error al agregar la foto."
            return mensaje

        finally:
            cursor.close()
            db.close()    
           
    def eliminar_foto_orden_servicio(self) -> str:
        id_foto = self.ID_foto_orden_servicio.strip()

        if not id_foto:
            mensaje = "El ID de la foto es obligatorio."
            return mensaje
        
        if not self.verificar_foto_existe_por_id():
            mensaje = f"No se encontró una foto con ID {id_foto} para eliminar."
            return mensaje
        
        db = self._conexion.conexion()
        if not db:
            mensaje = "Error al conectar con la base de datos."
            return mensaje
        
        cursor = db.cursor()
        try:
            sql = "DELETE FROM Fotos_orden_servicio WHERE ID_foto_orden_servicio = %s"
            cursor.execute(sql, (id_foto,))
            db.commit()
            mensaje = f"La foto con ID {id_foto} se eliminó exitosamente."
            return mensaje
        except Exception as e:
            print(f"Error al eliminar la foto: {e}")
            db.rollback()
            mensaje = "Error al eliminar la foto."
            return mensaje
        finally:
            cursor.close()
            db.close()

    def asignar_orden_empleado(self):
        db = self._conexion.conexion1()
        if not db:
            return False
        
        cursor = db.cursor()
        try:
            sql = "CALL sp_asignar_orden_servicio(%s, %s);"
            cursor.execute(sql, (self.ID_orden_servicio, self.ID_empleado))
            
            # CONSUMIR TODOS LOS RESULTADOS PENDIENTES
            # Esto es crucial para evitar el error "Commands out of sync"
            while cursor.nextset():
                # Consumir cualquier resultado pendiente
                try:
                    cursor.fetchall()
                except:
                    pass
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error al asignar la orden al empleado: {e}")
            return False
        finally:
            cursor.close()
            db.close()

    def liberar_orden_empleado(self):
        db = self._conexion.conexion1()
        if not db:
            return False
        
        cursor = db.cursor()
        try:
            sql = "CALL sp_liberar_orden_servicio(%s, %s);"
            cursor.execute(sql, (self.ID_orden_servicio, self.ID_empleado))
            
            # CONSUMIR TODOS LOS RESULTADOS PENDIENTES
            while cursor.nextset():
                try:
                    cursor.fetchall()
                except:
                    pass
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error al liberar la orden del empleado: {e}")
            return False
        finally:
            cursor.close()
            db.close()

    def registrar_reparacion(self):
        db = self._conexion.conexion1()
        if not db:
            return {"error": "Error de conexión a la base de datos"}
        
        cursor = db.cursor(dictionary=True)
        try:
            # Ejecutar el procedimiento almacenado
            sql = "CALL sp_registrar_reparacion(%s, %s, %s, %s);"
            cursor.execute(sql, (
                self.ID_orden_servicio,
                self.ID_empleado,
                self.Descripcion_reparacion,
                self.lista_repuestos  # Debe venir como JSON string
            ))
            
            # Obtener el resultado (SELECT final del procedimiento)
            resultado = cursor.fetchone()
            
            # CONSUMIR TODOS LOS RESULTADOS PENDIENTES (importante!)
            while cursor.nextset():
                try:
                    cursor.fetchall()
                except:
                    pass
            
            db.commit()
            
            # Verificar si el resultado es exitoso
            if resultado and isinstance(resultado, dict):
                # Si el procedimiento retorna un mensaje en alguna clave
                mensaje = resultado.get('mensaje') or resultado.get('Mensaje') or resultado.get('resultado')
                if mensaje and "exitosamente" in str(mensaje).lower():
                    return {"success": True, "mensaje": mensaje, "data": resultado}
                else:
                    return {"error": mensaje if mensaje else "Error desconocido", "data": resultado}
            else:
                return {"success": True, "mensaje": "Reparación registrada exitosamente"}
                
        except Exception as e:
            db.rollback()
            print(f"Error al registrar la reparación: {e}")
            return {"error": f"Error en la base de datos: {str(e)}"}
        finally:
            cursor.close()
            db.close()


    def registrar_orden(self):
        id_cliente = self.ID_cliente.strip()
        id_equipo = self.ID_equipo
        Estado_orden_servicio = 'pendiente'
        descripcion = self.Descripcion_reparacion
        fecha_entrada = self.Fecha_entrada
        fecha_salida = self.Fecha_salida
        nota = self.Nota_orden_servicio
        fecha_actual = date.today()

        if not id_cliente or not id_equipo or not descripcion or not fecha_entrada:
            return "Los campos ID_cliente, ID_equipo, Descripcion_reparacion y Fecha_entrada son obligatorios."

        if len(descripcion) > 1000:
            return "La descripción de la reparación no puede exceder los 1000 caracteres."

        if id_cliente.isdigit():
            return "El ID del cliente debe ser solo numeros."

        if len(id_cliente) > 8:
            return "El ID del cliente no puede tener más de 8 caracteres."
    
        if fecha_salida and fecha_salida < fecha_entrada:
            return "La fecha de salida no puede ser anterior a la fecha de entrada."
   
        if fecha_entrada < fecha_actual:
            return "La fecha de entrada no puede ser anterior a la fecha actual."
        
        db = self._conexion._bd.conexion1()
        if not db:
            return "Error al conectar con la base de datos."
            
        cursor = db.cursor()
        try:
            cursor.execute(
            """
             INSERT INTO orden_servicio (
             ID_cliente, ID_equipo,
             Estado_orden_servicio,Descripcion_reparacion, 
             Fecha_entrada, Fecha_salida, Nota_orden_servicio) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
             (id_cliente, id_equipo, Estado_orden_servicio, descripcion, fecha_entrada, fecha_salida, nota)
            )
            db.commit()
            return "Orden de servicio registrada exitosamente."
        except Exception as e:
            db.rollback()
            print(f"Error al registrar la orden de servicio: {e}")
            return "Error al registrar la orden de servicio."
        finally:
            cursor.close()
            db.close()


    def ordenes_asignadas_tecnico(self):

        db = self._conexion._bd.conexion1()
        if not db:
            return "Error al conectar con la base de datos."
            
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                """
                SELECT 
                Ordene_servicio.ID_orden_servicio AS id_orden,
                Orden_servicio.Estado_orden_servicio AS estado,
                Orden_servicio.Descripcion AS descripcion,
                Orden_servicio.Costo_reparacion AS costo,
                Orden_servicio.Nota_orden_servicio AS nota,
                Orden_servicio.Fecha_entrada AS fecha_e,
                Orden_servicio.Fecha_salida AS fecha_s,
                JOIN Equipo ON Orden_servicio.ID_equipo = Equipo.ID_equipo
                JOIN Cliente ON Orden_servicio.ID_cliente = Cliente.ID_cliente
                WHERE Orden_servicio.Estado_orden_servicio = 'Asignada' AND Interaccion.Accion = 'Asignada' AND Interaccion.ID_empleado = %s
                
                """
            )
            cursor.execute(sql, (self.ID_empleado,))
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()


    def registrar_interaccion(self):
        id_orden = self.ID_orden_servicio
        id_empleado = self.ID_empleado
        accion = 'Asignada'


        db = self._conexion._bd.conexion1()
        if not db:
            return "Error al conectar con la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT IGNORE INTO interaccion (ID_orden_servicio, ID_empleado, Accion) VALUES (%s, %s, %s)",
                (id_orden, id_empleado, accion),
            )
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            db.rollback()
            print(f"Error al registrar interacción: {e}")
            return False
        finally:
            cursor.close()
            db.close()




    def verificar_asignacion(self):
        id_orden = self.ID_orden_servicio
        id_empleado = self.ID_empleado

        db = self._conexion._bd.conexion1()
        if not db:
            return "Error al conectar con la base de datos."
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                """ 
                SELECT 
                Ordene_servicio.ID_orden_servicio AS id_orden,
                Interaccion.ID_empleado AS id_empleado,
                Ordene_servicio.Estado_orden_servicio AS estado,
                Interaccion.Accion AS accion
                FROM Ordene_servicio 
                INNER JOIN Interaccion ON Ordene_servicio.ID_orden_servicio = Interaccion.ID_orden_servicio
                WHERE Ordene_servicio.ID_orden_servicio = %s
                AND Interaccion.ID_empleado = %s 
                AND Ordene_servicio.Estado_orden_servicio = 'Asignada' 
                AND Interaccion.Accion = 'Asignada'
               """  
            )
            
            cursor.execute(sql, (id_orden, id_empleado))
            asignacion = cursor.fetchone()

            return asignacion
            
        except Exception as e:
            print(f"Error al verificar asignación: {e}")
            return None
            
        finally:
            cursor.close()
            db.close()



    def asignar_orden_empleado(self):
        id_orden: int = self.ID_orden_servicio
        id_empleado: int = self.ID_empleado

        asignada = self.verificar_asignacion()

        if asignada:
            print(f"La orden {id_orden} ya está asignada al empleado {id_empleado}.")
            return False

        db = self._conexion._bd.conexion1()
        if not db:
            return "Error al conectar con la base de datos."
        
        cursor = db.cursor()
        try:
            db.start_transaction()

            # 2. INSERT en la tabla interaccion
            sql_interaccion = (
                "INSERT INTO interaccion (ID_orden_servicio, ID_empleado, Accion) "
                "VALUES (%s, %s, 'Asignada')"
            )
            cursor.execute(sql_interaccion, (id_orden, id_empleado))

            # 3. UPDATE en la tabla orden_e
            sql_orden = (
                "UPDATE Orden_servicio "
                "SET Estado_orden_servicio = 'Asignada' "
                "WHERE ID_orden_servicio = %s"
            )
            cursor.execute(sql_orden, (id_orden,))

            
            db.commit()
            print("Asignación realizada con éxito.")
            return True
        
        except Exception as e:
        
            db.rollback()
            print(f"Error al procesar la asignación: {e}")
            return False
        
        finally:
            cursor.close()
            db.close()


    def actualizar_revision_cotizacion(self):
        id_orden = self.ID_orden_servicio
        revision = self.Descripcion_reparacion
        costo = self.Costo_reparacion
    
        """Actualiza la revisión y/o el costo de reparación de una orden.

        Si no se pasan parámetros, usa los atributos de la instancia.
        Devuelve True si se actualizó al menos una fila, False en caso contrario.
        """
        if id_orden is None:
            id_orden = self.ID_orden_servicio

        if revision is None:
            revision = self.Descripcion_reparacion

        if costo is None:
            costo = self.Costo_reparacion

        if revision is None and costo is None:
            return False

        db = self._conexion.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            fields = []
            params = []
            if revision is not None:
                fields.append("Revision = %s")
                params.append(revision)
            if costo is not None:
                fields.append("Costo_reparacion = %s")
                params.append(costo)

            params.append(id_orden)
            sql = f"UPDATE Orden_servicio SET {', '.join(fields)} WHERE ID_orden_servicio = %s"
            cursor.execute(sql, tuple(params))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            db.rollback()
            print(f"Error al actualizar revisión: {e}")
            return False
        finally:
            cursor.close()
            db.close()