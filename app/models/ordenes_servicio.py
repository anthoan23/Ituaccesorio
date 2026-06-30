from __future__ import annotations
from app.models.database import conectar



class Orden_servicio():
    def __init__(self, ID_orden_servicio: int = None, Estado_orden_servicio: str = None, Descripcion_reparacion: str = None, Costo_reparacion: float = None, Nota_orden_servicio: str = None, Fecha_entrada = None, Fecha_salida = None, ID_foto_orden_servicio: str = None, Foto_orden_servicio = None, ID_empleado: int = None, lista_repuestos=None):
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

    def listar_ordenes_servicio(self):
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


    def consultar_orden(self):
        id_orden = self.ID_orden_servicio
        db = self._conexion.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            # 1. Consultar la orden
            sql = """ SELECT o.*, 
                p.Nombre_producto AS Modelo, 
                o.Estado_orden_servicio AS Estado,
                CASE 
                        WHEN pn.ID_cliente IS NOT NULL THEN CONCAT(pn.Nombre_cliente, ' ', pn.Apellido_cliente)
                        WHEN cj.ID_cliente IS NOT NULL THEN cj.Razon_social
                        ELSE 'Cliente no especificado'
                    END AS nombre_cliente,
                o.Descripcion_reparacion AS Descripcion,
                o.Nota_orden_servicio AS Nota
                FROM Orden_servicio o 
                JOIN Equipo e ON o.ID_equipo = e.ID_equipo 
                JOIN Cliente c ON o.ID_cliente = c.ID_cliente
                JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente_juridico cj ON c.ID_cliente = cj.ID_cliente
                WHERE o.ID_orden_servicio = %s"""
            
            cursor.execute(sql, (id_orden,))
            orden = cursor.fetchone()
            
            # Si no se encontró la orden, retornar None
            if not orden:
                return None
            
            # 2. Consultar las fotos de la orden (usando la misma conexión)
            sql_fotos = "SELECT * FROM Fotos_orden_servicio WHERE ID_orden_servicio = %s"
            cursor.execute(sql_fotos, (id_orden,))
            fotos = cursor.fetchall()
            
            # 3. Agregar las fotos al resultado
            orden['fotos'] = fotos if fotos else []
            
            return orden
            
        except Exception as e:
            print(f"Error al consultar la orden: {e}")
            return None
        finally:
            cursor.close()
            db.close()

    def empleados_asignados(self, id_orden: int):
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


    def verificar_foto_existe_por_id(self) -> bool:
        """Verifica si una foto existe por su ID"""
        id_foto = self.ID_foto_orden_servicio
        if not id_foto:
            return False
            
        db = self._conexion.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM Fotos_orden_servicio WHERE ID_foto_orden_servicio = %s LIMIT 1",
                (id_foto.strip(),)
            )
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error al verificar foto por ID: {e}")
            return False
        finally:
            cursor.close()
            db.close()



 
           
    def eliminar_foto_orden_servicio(self) -> dict:
        """
        Elimina una foto de la base de datos y retorna la ruta para eliminar el archivo físico
        
        Returns:
            dict: {'success': bool, 'mensaje': str, 'ruta_foto': str, 'id_orden': str}
        """
        id_foto = self.ID_foto_orden_servicio
        
        if not id_foto:
            return {"success": False, "error": "ID de foto no proporcionado"}
        
        db = self._conexion.conexion1()
        if not db:
            return {"success": False, "error": "Error al conectar con la base de datos."}
        
        cursor = db.cursor(dictionary=True)
        try:
            # Obtener la ruta de la foto y el ID de orden antes de eliminar
            cursor.execute(
                "SELECT Foto_orden_servicio, ID_orden_servicio FROM Fotos_orden_servicio WHERE ID_foto_orden_servicio = %s",
                (id_foto,)
            )
            foto = cursor.fetchone()
            
            if not foto:
                return {"success": False, "error": f"No se encontró una foto con ID {id_foto}"}
            
            ruta_foto = foto.get('Foto_orden_servicio')
            id_orden = foto.get('ID_orden_servicio')
            
            # Eliminar el registro
            cursor.execute(
                "DELETE FROM Fotos_orden_servicio WHERE ID_foto_orden_servicio = %s",
                (id_foto,)
            )
            db.commit()
            
            return {
                "success": True,
                "mensaje": f"La foto con ID {id_foto} se eliminó exitosamente",
                "ruta_foto": ruta_foto,
                "id_orden": id_orden
            }
        except Exception as e:
            db.rollback()
            print(f"Error al eliminar la foto: {e}")
            return {"success": False, "error": f"Error al eliminar la foto: {str(e)}"}
        finally:
            cursor.close()
            db.close()



    def registrar_fotos(self,) -> dict:
 
        id_orden = self.ID_orden_servicio
        lista_rutas = self.Foto_orden_servicio
        
        db = self._conexion.conexion1()
        if not db:
            return {"success": False, "error": "Error al conectar con la base de datos."}
        
        cursor = db.cursor()
        try:
            # Convertir lista a JSON
            import json
            json_fotos = json.dumps(lista_rutas)
            
            # Llamar al procedimiento almacenado
            cursor.callproc('sp_registrar_fotos_orden', (id_orden, json_fotos))
            
            # Consumir resultados
            resultado = None
            for result in cursor.stored_results():
                resultado = result.fetchall()
            
            db.commit()
            
            return {
                "success": True,
                "mensaje": f"{len(lista_rutas)} fotos registradas exitosamente",
                "data": resultado
            }
        except Exception as e:
            db.rollback()
            print(f"Error al registrar fotos: {e}")
            error_msg = str(e)
            # Extraer mensaje de error del procedimiento si está disponible
            if "MESSAGE_TEXT" in error_msg:
                import re
                match = re.search(r"MESSAGE_TEXT: (.*?)(?:,|$)", error_msg)
                if match:
                    error_msg = match.group(1).strip()
            return {"success": False, "error": f"Error al registrar fotos: {error_msg}"}
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


