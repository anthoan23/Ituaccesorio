from __future__ import annotations
from app.models.database import conectar
from datetime import date
import sys


class Orden_servicio():
    def __init__(self, ID_orden_servicio: int = None, Estado_orden_servicio: str = None, 
                 Descripcion_reparacion: str = None, Costo_reparacion: float = None, 
                 Nota_orden_servicio: str = None, Fecha_entrada = None, Fecha_salida = None, 
                 ID_foto_orden_servicio: str = None, Foto_orden_servicio: str = None, 
                 ID_empleado: int = None, lista_repuestos=None,
                 ID_cliente: str = None, ID_equipo: str = None):
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
        self.ID_cliente = ID_cliente
        self.ID_equipo = ID_equipo
        self._ultimo_error = None

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
                LEFT JOIN Fotos_orden_servicio fot ON os.ID_orden_servicio = fot.ID_orden_servicio
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

    def listado_ordenes_servicio(self, estados=None):
        """Lista órdenes de servicio, opcionalmente filtradas por lista de estados."""
        db = self._conexion.conexion1()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            sql = """
                SELECT
                    o.ID_orden_servicio AS ID_orden,
                    o.Estado_orden_servicio AS Estado,
                    o.ID_cliente AS ID_cliente,
                    COALESCE(CONCAT(pn.Nombre_cliente, ' ', pn.Apellido_cliente), cj.Razon_social, 'Cliente no especificado') AS Nombre_cliente,
                    COALESCE(p.Nombre_producto, '') AS Modelo,
                    o.Descripcion_reparacion AS Des_cliente,
                    o.Fecha_entrada AS Fecha_e,
                    e.ID_equipo AS Equipo
                FROM Orden_servicio o
                INNER JOIN Equipo e ON o.ID_equipo = e.ID_equipo
                LEFT JOIN Cliente c ON o.ID_cliente = c.ID_cliente
                LEFT JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente_juridico cj ON c.ID_cliente = cj.ID_cliente
                LEFT JOIN Producto p ON e.ID_producto = p.ID_producto
            """
            if estados:
                placeholders = ",".join(["%s"] * len(estados))
                sql = sql.strip() + f" WHERE o.Estado_orden_servicio IN ({placeholders}) ORDER BY o.ID_orden_servicio DESC"
                cursor.execute(sql, tuple(estados))
            else:
                sql = sql.strip() + " ORDER BY o.ID_orden_servicio DESC"
                cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar órdenes de servicio con filtro: {e}")
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
                (id_foto,)
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    def agregar_foto_orden_servicio(self) -> str:
        id_foto = self.ID_foto_orden_servicio
        id_orden = self.ID_orden_servicio
        ruta_foto = self.Foto_orden_servicio.strip()

        if not id_foto:
            return "El ID de la foto es obligatorio."
        
        if len(str(id_foto)) > 10:
            return "El ID de la foto no puede tener más de 10 caracteres."
        
        if len(ruta_foto) > 255:
            return "La ruta de la foto no puede tener más de 255 caracteres."
        
        if self.verificar_foto_existe_por_ruta():
            return f"La foto '{ruta_foto}' ya existe."

        db = self._conexion.conexion1()
        if not db:
            return "Error al conectar con la base de datos."
        
        cursor = db.cursor()
        try:
            sql = """INSERT INTO Fotos_orden_servicio 
                     (ID_foto_orden_servicio, ID_orden_servicio, Foto_orden_servicio) 
                     VALUES (%s, %s, %s)"""
            cursor.execute(sql, (id_foto, id_orden, ruta_foto))
            db.commit()
            return "Foto agregada exitosamente."
        except Exception as e:
            print(f"Error al agregar la foto: {e}")
            db.rollback()
            return "Error al agregar la foto."
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
        
        db = self._conexion.conexion1()
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
            self._ultimo_error = "Error al conectar con la base de datos"
            return False
        
        cursor = db.cursor()
        try:
            print(f"[DEBUG] Asignando orden {self.ID_orden_servicio} al empleado {self.ID_empleado}")
            sql = "CALL sp_asignar_orden_servicio(%s, %s);"
            cursor.execute(sql, (self.ID_orden_servicio, self.ID_empleado))
            
            # CONSUMIR TODOS LOS RESULTADOS PENDIENTES
            while cursor.nextset():
                try:
                    cursor.fetchall()
                except:
                    pass
            
            db.commit()
            print(f"[DEBUG] Orden {self.ID_orden_servicio} asignada exitosamente")
            self._ultimo_error = None
            return True
        except Exception as e:
            db.rollback()
            error_msg = str(e)
            print(f"[ERROR] Error al asignar la orden: {error_msg}")
            import traceback
            traceback.print_exc()
            self._ultimo_error = error_msg
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
            sql = "CALL sp_registrar_reparacion(%s, %s, %s, %s);"
            cursor.execute(sql, (
                self.ID_orden_servicio,
                self.ID_empleado,
                self.Descripcion_reparacion,
                self.lista_repuestos
            ))
            
            resultado = cursor.fetchone()
            
            while cursor.nextset():
                try:
                    cursor.fetchall()
                except:
                    pass
            
            db.commit()
            
            if resultado and isinstance(resultado, dict):
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
        id_cliente = (self.ID_cliente or "").strip()
        id_equipo = self.ID_equipo
        Estado_orden_servicio = 'Pendiente'
        descripcion = self.Descripcion_reparacion
        fecha_entrada = self.Fecha_entrada
        fecha_salida = self.Fecha_salida
        nota = self.Nota_orden_servicio
        fecha_actual = date.today()

        if not id_cliente or not id_equipo or not descripcion or not fecha_entrada:
            return "Los campos ID_cliente, ID_equipo, Descripcion_reparacion y Fecha_entrada son obligatorios."

        if len(descripcion) > 1000:
            return "La descripción de la reparación no puede exceder los 1000 caracteres."

        if not str(id_cliente).isdigit():
            return "El ID del cliente debe ser solo numeros."

        if len(id_cliente) > 8:
            return "El ID del cliente no puede tener más de 8 caracteres."
    
        if fecha_salida and fecha_salida < fecha_entrada:
            return "La fecha de salida no puede ser anterior a la fecha de entrada."
   
        if fecha_entrada < fecha_actual:
            return "La fecha de entrada no puede ser anterior a la fecha actual."
        
        db = self._conexion.conexion1()
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


    def crear_orden(self, id_cliente: str, id_equipo: str, id_modelo: str = None,
                    descripcion: str = None, nota=None, modelo_custom=None):
        
        # =============================================
        # LOGS EXTENSIVOS PARA DOCKER
        # =============================================
        print("=" * 60, flush=True)
        print("INICIANDO crear_orden()", flush=True)
        print(f"id_cliente: {id_cliente} (type: {type(id_cliente)})", flush=True)
        print(f"id_equipo: {id_equipo} (type: {type(id_equipo)})", flush=True)
        print(f"id_modelo: {id_modelo} (type: {type(id_modelo)})", flush=True)
        print(f"descripcion: {descripcion} (type: {type(descripcion)})", flush=True)
        print(f"nota: {nota} (type: {type(nota)})", flush=True)
        print(f"modelo_custom: {modelo_custom} (type: {type(modelo_custom)})", flush=True)
        print(f"self.ID_empleado: {self.ID_empleado}", flush=True)
        print("=" * 60, flush=True)
        
        # Validaciones
        if not id_cliente or not id_equipo or not descripcion:
            print(f"[ERROR crear_orden] Faltan campos obligatorios", flush=True)
            return None

        if not id_modelo and not modelo_custom:
            print("[ERROR crear_orden] No hay modelo ni modelo personalizado", flush=True)
            return None

        if not str(id_cliente).isdigit():
            print(f"[ERROR crear_orden] ID cliente no es dígito: {id_cliente}", flush=True)
            return None
        
        if id_modelo and not str(id_modelo).isdigit():
            print(f"[ERROR crear_orden] ID modelo no es dígito: {id_modelo}", flush=True)
            return None

        # Obtener el ID del empleado desde la instancia
        id_empleado = self.ID_empleado
        
        db = self._conexion.conexion1()
        if not db:
            print("[ERROR crear_orden] No se pudo conectar a la base de datos", flush=True)
            return None

        cursor = db.cursor()
        try:
            # Preparar datos - CONVERTIR A TIPOS ESPERADOS POR EL PROCEDIMIENTO
            # El procedimiento espera: (VARCHAR(10), VARCHAR(15), VARCHAR(300), VARCHAR(300), INT)
            id_cliente_str = str(id_cliente).strip()
            id_equipo_str = str(id_equipo).strip()
            descripcion_str = str(descripcion).strip() if descripcion else ""
            nota_str = str(nota).strip() if nota else ""
            id_empleado_int = int(id_empleado)
            
            print(f"[INFO] Llamando a sp_crear_orden_servicio", flush=True)
            print(f"  id_cliente: {id_cliente_str} (type: {type(id_cliente_str)})", flush=True)
            print(f"  id_equipo: {id_equipo_str} (type: {type(id_equipo_str)})", flush=True)
            print(f"  descripcion: {descripcion_str} (type: {type(descripcion_str)})", flush=True)
            print(f"  nota: {nota_str} (type: {type(nota_str)})", flush=True)
            print(f"  id_empleado: {id_empleado_int} (type: {type(id_empleado_int)})", flush=True)
            
            # Llamar al procedimiento almacenado - USAR execute en lugar de callproc
            # Esto es más compatible y da mejor control de errores
            sql = """
                CALL sp_crear_orden_servicio(%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                id_cliente_str,
                id_equipo_str,
                descripcion_str,
                nota_str,
                id_empleado_int
            ))
            
            # OBTENER EL RESULTADO
            # Con execute, los resultados vienen en múltiples conjuntos
            result = None
            id_interaccion = None
            
            # Primer conjunto de resultados (el SELECT final del procedure)
            result_set = cursor.fetchone()
            if result_set:
                # El procedure retorna: ID_orden_servicio, ID_interaccion, Mensaje
                # Dependiendo de cómo esté definido, podría ser una tupla o diccionario
                if isinstance(result_set, tuple):
                    if len(result_set) >= 2:
                        result = result_set[0]
                        id_interaccion = result_set[1]
                    else:
                        result = result_set[0]
                else:
                    # Si es diccionario
                    result = result_set.get('ID_orden_servicio')
                    id_interaccion = result_set.get('ID_interaccion')
                
                print(f"[DEBUG] Resultado del procedure: {result_set}", flush=True)
                print(f"[DEBUG] ID_interaccion generado: {id_interaccion}", flush=True)
            
            # Consumir todos los resultados adicionales para evitar errores
            while cursor.nextset():
                try:
                    cursor.fetchall()
                except:
                    pass
            
            db.commit()
            
            if result:
                id_orden = result
                print(f"[OK] Orden creada exitosamente con procedure:", flush=True)
                print(f"  ID_orden_servicio: {id_orden}", flush=True)
                print(f"  ID_interaccion: {id_interaccion}", flush=True)
                return id_orden
            else:
                print("[ERROR] No se obtuvo resultado del procedimiento", flush=True)
                return None
                
        except Exception as e:
            db.rollback()
            print(f"[ERROR] Excepción al crear la orden con procedure: {e}", flush=True)
            import traceback
            traceback.print_exc(file=sys.stdout)
            print(f"[ERROR] Tipo de error: {type(e).__name__}", flush=True)
            print(f"[ERROR] Detalles del error: {str(e)}", flush=True)
            
            # Intentar obtener más información del error
            if hasattr(e, 'args') and len(e.args) > 0:
                print(f"[ERROR] Args: {e.args}", flush=True)
            
            return None
        finally:
            cursor.close()
            db.close()


    def ordenes_asignadas_tecnico(self):
        db = self._conexion.conexion1()
        if not db:
            return "Error al conectar con la base de datos."
            
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                """
                SELECT 
                    o.ID_orden_servicio AS ID_orden,
                    o.Estado_orden_servicio AS Estado,
                    o.Descripcion_reparacion AS descripcion,
                    o.Costo_reparacion AS costo,
                    o.Nota_orden_servicio AS nota,
                    o.Fecha_entrada AS fecha_e,
                    o.Fecha_salida AS fecha_s,
                    p.Nombre_producto AS modelo,
                    COALESCE(CONCAT(pn.Nombre_cliente, ' ', pn.Apellido_cliente), cj.Razon_social, 'Cliente no especificado') AS Nombre_cliente
                FROM Orden_servicio o
                INNER JOIN Equipo e ON o.ID_equipo = e.ID_equipo
                INNER JOIN Producto p ON e.ID_producto = p.ID_producto
                INNER JOIN Cliente c ON o.ID_cliente = c.ID_cliente
                LEFT JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente_juridico cj ON c.ID_cliente = cj.ID_cliente
                INNER JOIN Interaccion i ON o.ID_orden_servicio = i.ID_orden_servicio
                WHERE o.Estado_orden_servicio = 'Asignada' 
                AND i.Accion = 'Asignada' 
                AND i.ID_empleado = %s
                ORDER BY o.ID_orden_servicio DESC
                """
            )
            cursor.execute(sql, (self.ID_empleado,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en ordenes_asignadas_tecnico: {e}")
            return []
        finally:
            cursor.close()
            db.close()


    def registrar_interaccion(self, id_orden=None, id_empleado=None, accion=None):
        """Registra una interacción de una orden con un empleado.
        
        Si no se pasan parámetros, usa los atributos de la instancia.
        """
        id_orden = id_orden or self.ID_orden_servicio
        id_empleado = id_empleado or self.ID_empleado
        accion = accion or 'Asignada'

        if not id_orden or not id_empleado or not accion:
            return False

        db = self._conexion.conexion1()
        if not db:
            return "Error al conectar con la base de datos."

        cursor = db.cursor()
        try:
            # Generar ID de interacción
            cursor.execute("SELECT MAX(ID_interaccion) FROM Interaccion")
            row = cursor.fetchone()
            ultimo_id = row[0] if row else None
            if not ultimo_id:
                nuevo_id = "INT000001"
            else:
                num = int(ultimo_id[3:]) + 1
                nuevo_id = f"INT{num:06d}"
            
            cursor.execute(
                "INSERT INTO interaccion (ID_interaccion, ID_orden_servicio, ID_empleado, Accion) VALUES (%s, %s, %s, %s)",
                (nuevo_id, id_orden, id_empleado, accion),
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

        db = self._conexion.conexion1()
        if not db:
            return "Error al conectar con la base de datos."
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                """ 
                SELECT 
                    o.ID_orden_servicio AS id_orden,
                    i.ID_empleado AS id_empleado,
                    o.Estado_orden_servicio AS estado,
                    i.Accion AS accion
                FROM Orden_servicio o 
                INNER JOIN Interaccion i ON o.ID_orden_servicio = i.ID_orden_servicio
                WHERE o.ID_orden_servicio = %s
                AND i.ID_empleado = %s 
                AND o.Estado_orden_servicio = 'Asignada' 
                AND i.Accion = 'Asignada'
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


    def actualizar_revision_cotizacion(self):
        id_orden = self.ID_orden_servicio
        revision = self.Descripcion_reparacion
        costo = self.Costo_reparacion
    
        """Actualiza la revisión y/o el costo de reparación de una orden."""
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
                fields.append("Descripcion_reparacion = %s")
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

    def eliminar_orden(self, id_orden):
        """Elimina la orden (primero las dependencias si no hay ON DELETE CASCADE)."""
        db = self._conexion.conexion1()
        if not db:
            return False
        cursor = db.cursor()
        try:
            sql = "DELETE FROM Orden_servicio WHERE ID_orden_servicio = %s"
            cursor.execute(sql, (id_orden,))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            db.rollback()
            print(f"Error en eliminar_orden: {e}")
            return False
        finally:
            cursor.close()
            db.close()

    # =============================================
    # MÉTODOS AGREGADOS PARA EL FUNCIONAMIENTO DEL BLUEPRINT
    # =============================================

    def detalles_orden(self, id_orden: str) -> dict:
        """Obtiene los detalles completos de una orden de servicio"""
        db = self._conexion.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    o.ID_orden_servicio AS ID_orden,
                    o.Estado_orden_servicio AS Estado,
                    o.ID_cliente AS ID_cliente,
                    COALESCE(CONCAT(pn.Nombre_cliente, ' ', pn.Apellido_cliente), cj.Razon_social, 'Cliente no especificado') AS Nombre_cliente,
                    COALESCE(p.Nombre_producto, '') AS Modelo,
                    o.Descripcion_reparacion AS Des_cliente,
                    o.Costo_reparacion AS Costo_reparacion,
                    o.Nota_orden_servicio AS Nota,
                    o.Fecha_entrada AS Fecha_e,
                    o.Fecha_salida AS Fecha_s,
                    e.ID_equipo AS Equipo,
                    e.Color,
                    e.Capacidad
                FROM Orden_servicio o
                INNER JOIN Equipo e ON o.ID_equipo = e.ID_equipo
                LEFT JOIN Cliente c ON o.ID_cliente = c.ID_cliente
                LEFT JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente_juridico cj ON c.ID_cliente = cj.ID_cliente
                LEFT JOIN Producto p ON e.ID_producto = p.ID_producto
                WHERE o.ID_orden_servicio = %s
            """, (id_orden,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error en detalles_orden: {e}")
            return None
        finally:
            cursor.close()
            db.close()

    def fotos_orden(self, id_orden: str) -> list:
        """Obtiene las fotos de una orden de servicio"""
        db = self._conexion.conexion1()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT ID_foto_orden_servicio, Foto_orden_servicio AS Foto_e
                FROM Fotos_orden_servicio
                WHERE ID_orden_servicio = %s
            """, (id_orden,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en fotos_orden: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def empleados_asignados(self, id_orden: str) -> list:
        """Obtiene los empleados que han interactuado con la orden"""
        db = self._conexion.conexion1()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    i.Accion,
                    i.ID_empleado AS ID_em,
                    e.Nombre_empleado AS Nombre_em,
                    e.Apellido_empleado AS Apellido_em
                FROM Interaccion i
                INNER JOIN Empleado e ON i.ID_empleado = e.ID_empleado
                WHERE i.ID_orden_servicio = %s
                ORDER BY i.ID_interaccion DESC
            """, (id_orden,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en empleados_asignados: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def actualizar_estado(self, id_orden: str, nuevo_estado: str) -> bool:
        """Actualiza el estado de una orden de servicio"""
        if not id_orden or not nuevo_estado:
            return False

        db = self._conexion.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE Orden_servicio 
                SET Estado_orden_servicio = %s 
                WHERE ID_orden_servicio = %s
            """, (nuevo_estado, id_orden))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            db.rollback()
            print(f"Error en actualizar_estado: {e}")
            return False
        finally:
            cursor.close()
            db.close()