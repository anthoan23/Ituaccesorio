from __future__ import annotations
from app.models.database import conectar


class Orden_servicio():
    def __init__(self, ID_orden_servicio: int = None, Estado_orden_servicio: str = None, Descripcion_reparacion: str = None, Costo_reparacion: float = None, Nota_orden_servicio: str = None, Fecha_entrada = None, Fecha_salida = None, ID_foto_orden_servicio: str = None, Foto_orden_servicio: str = None, ID_empleado: int = None):
        self.ID_orden_servicio = ID_orden_servicio
        self.Estado_orden_servicio = Estado_orden_servicio
        self.Descripcion_reparacion = Descripcion_reparacion
        self.Costo_reparacion = Costo_reparacion
        self.Nota_orden_servicio = Nota_orden_servicio
        self.ID_empleado = ID_empleado
        self.Fecha_ingreso = Fecha_entrada
        self.Fecha_salida = Fecha_salida
        self.ID_foto_orden_servicio = ID_foto_orden_servicio
        self.Foto_orden_servicio = Foto_orden_servicio

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
                    os.ID_orden_servicio AS id_orden,                 
                    p.Nombre_producto AS modelo,
                    os.Descripcion_reparacion AS descripcion,       
                    os.Fecha_entrada AS fecha_e      
                FROM Orden_servicio os
                INNER JOIN Equipo e ON os.ID_equipo = e.ID_equipo
                INNER JOIN Producto p ON e.ID_producto = p.ID_producto
                INNER JOIN Interaccion i ON os.ID_orden_servicio = i.ID_orden_servicio
                WHERE i.ID_empleado = %s AND os.Estado_orden_servicio = 'Asignada'
                ORDER BY os.ID_orden_servicio DESC;
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

"""
from __future__ import annotations

import os

from flask import current_app

from app.models.database import conectar

class OrdenServicio(conectar):

    def listado_ordenes_taller(self):
        db = self.conexion1()
        if not db:
            return None
        
        r1 = 'Pendiente'
        r2 = 'En Proceso'
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                "SELECT o.*, "
                "o.ID_orden_servicio AS ID_orden, "
                "o.Estado_o AS Estado, "
                "o.ID_c AS ID_cliente, "
                "c.Nombre_c AS Nombre_cliente, "
                "c.Apellido_c AS Apellido_cliente, "
                "m.N_modelo AS Modelo, "
                "o.Des_cliente "
                "FROM orden_e o JOIN modelo_producto m ON o.ID_modelo = m.ID_modelo "
                "JOIN cliente c ON o.ID_c = c.ID_c "
                "WHERE o.Estado_o = %s OR o.Estado_o = %s "
            )
            cursor.execute(sql, (r1, r2))
            ordenes = cursor.fetchall()
        
            return ordenes
        
        finally:
            cursor.close()
            db.close() 

    def listado_ordenes_servicio(self, estados=None):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            where_sql = ""
            params = []
            if estados:
                placeholders = ", ".join(["%s"] * len(estados))
                where_sql = f"WHERE o.Estado_o IN ({placeholders})"
                params = list(estados)

            sql = (
                "SELECT o.*, "
                "o.ID_orden_servicio AS ID_orden, "
                "o.Estado_o AS Estado, "
                "o.ID_c AS ID_cliente, "
                "c.Nombre_c AS Nombre_cliente, "
                "c.Apellido_c AS Apellido_cliente, "
                "m.N_modelo AS Modelo, "
                "o.Des_cliente "
                "FROM orden_e o JOIN modelo_producto m ON o.ID_modelo = m.ID_modelo "
                "JOIN cliente c ON o.ID_c = c.ID_c "
                f"{where_sql} "
                "ORDER BY o.ID_orden_servicio DESC"
            )
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def crear_orden(
        self,
        id_cliente: int,
        id_modelo: int,
        descripcion: str,
        patron,
        clave: str,
        fecha_ingreso,
        nota: str | None = None,
        estado: str = "Pendiente",
    ):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor()
        try:
            sql = (
                "INSERT INTO orden_e (ID_modelo, ID_c, Estado_o, Des_cliente, Patron, Clave, Costo_reparacion, Fecha_e, Nota) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            )
            cursor.execute(
                sql,
                (
                    id_modelo,
                    id_cliente,
                    estado,
                    descripcion,
                    patron,
                    clave,
                    None,
                    fecha_ingreso,
                    nota,
                ),
            )
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            db.rollback()
            print(f"Error al crear orden: {e}")
            return None
        finally:
            cursor.close()
            db.close()

    def ordenes_asignadas_empleado(self):
        db = self.conexion1()
        if not db:
            return None

        id_empleado = 1004
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                "SELECT i.ID_orden, m.N_modelo "
                "FROM interaccion i JOIN orden_e o ON i.ID_orden = o.ID_orden_servicio "
                "JOIN modelo_producto m ON o.ID_modelo = m.ID_modelo "
                "WHERE o.Estado_o IN ('Asignado', 'Revisado') AND i.ID_em = %s"
            )
            cursor.execute(sql, (id_empleado,))
            ordenes = cursor.fetchall()
        
            return ordenes
        
        finally:
            cursor.close()
            db.close()

    def ordenes_asignadas_tecnico(self, id_empleado: int):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                "SELECT o.*, "
                "o.ID_orden_servicio AS ID_orden, "
                "o.Estado_o AS Estado, "
                "m.N_modelo AS Modelo, "
                "c.Nombre_c AS Nombre_cliente, "
                "c.Apellido_c AS Apellido_cliente "
                "FROM interaccion i "
                "JOIN orden_e o ON i.ID_orden = o.ID_orden_servicio "
                "JOIN modelo_producto m ON o.ID_modelo = m.ID_modelo "
                "JOIN cliente c ON o.ID_c = c.ID_c "
                "WHERE i.ID_em = %s AND i.Accion = 'Asignado' "
                "ORDER BY o.ID_orden_servicio DESC"
            )
            cursor.execute(sql, (id_empleado,))
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    
    
    

    
    def eliminar_foto_orden(self, id_evidencia: int):
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT Foto_e FROM evidencia_e WHERE ID_evidencia_e = %s",
                (id_evidencia,)
            )
            foto = cursor.fetchone()

            if not foto:
                return False

            ruta_archivo = foto.get("Foto_e") if isinstance(foto, dict) else None
            if ruta_archivo:
                ruta_relativa = ruta_archivo.lstrip("/\\")
                posibles_rutas = []

                if ruta_archivo.startswith("/static/"):
                    try:
                        relativas_static = ruta_archivo.split("/static/", 1)[1].lstrip("/\\")
                        posibles_rutas.append(os.path.join(current_app.static_folder, relativas_static))
                    except RuntimeError:
                        pass

                try:
                    posibles_rutas.append(os.path.join(current_app.root_path, ruta_relativa))
                except RuntimeError:
                    pass

                posibles_rutas.append(os.path.join(os.getcwd(), ruta_relativa))

                ruta_local = next((ruta for ruta in posibles_rutas if os.path.exists(ruta)), None)
                if ruta_local:
                    os.remove(ruta_local)

            cursor.execute(
                "DELETE FROM evidencia_e WHERE ID_evidencia_e = %s",
                (id_evidencia,)
            )
            db.commit()
            return True

        except Exception as e:
            db.rollback()
            print(f"Error al eliminar foto: {e}")
            return False

        finally:
            cursor.close()
            db.close()

    def registrar_fotos_orden(self, id_orden: int, rutas_fotos: list[str]):
        if not rutas_fotos:
            return False

        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            db.start_transaction()

            sql = (
                "INSERT INTO evidencia_e (ID_orden, Foto_e) "
                "VALUES (%s, %s)"
            )
            for ruta in rutas_fotos:
                cursor.execute(sql, (id_orden, ruta))

            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error al registrar fotos: {e}")
            return False
        finally:
            cursor.close()
            db.close()

    def registrar_interaccion(self, id_orden: int, id_empleado: int, accion: str):
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT IGNORE INTO interaccion (ID_orden, ID_em, Accion) VALUES (%s, %s, %s)",
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

    def actualizar_revision_cotizacion(self, id_orden: int, revision: str | None = None, costo=None):
        if revision is None and costo is None:
            return False

        db = self.conexion1()
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
            sql = f"UPDATE orden_e SET {', '.join(fields)} WHERE ID_orden_servicio = %s"
            cursor.execute(sql, tuple(params))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            db.rollback()
            print(f"Error al actualizar revisión/cotización: {e}")
            return False
        finally:
            cursor.close()
            db.close()


    def asignar_orden_empleado(self, id_orden: int, id_empleado: int):
        # 1. Primero verificamos si ya existe esa asignación activa
        # Usamos la lógica de la función anterior
        asignada = self.verificar_asignacion(id_orden, id_empleado)
        
        if asignada:
            print(f"La orden {id_orden} ya está asignada al empleado {id_empleado}.")
            return False

        db = self.conexion1()
        if not db:
            return False
        
        cursor = db.cursor()
        try:
            # Iniciamos la transacción de forma explícita
            db.start_transaction()

            # 2. INSERT en la tabla interaccion
            sql_interaccion = (
                "INSERT INTO interaccion (ID_orden, ID_em, Accion) "
                "VALUES (%s, %s, 'Asignado')"
            )
            cursor.execute(sql_interaccion, (id_orden, id_empleado))

            # 3. UPDATE en la tabla orden_e
            sql_orden = (
                "UPDATE orden_e "
                "SET Estado_o = 'Asignado' "
                "WHERE ID_orden_servicio = %s"
            )
            cursor.execute(sql_orden, (id_orden,))

            # Si ambas consultas fueron exitosas, guardamos los cambios
            db.commit()
            print("Asignación realizada con éxito.")
            return True
        
        except Exception as e:
            # Si algo falla (ej. el ID no existe), deshacemos todo para evitar datos inconsistentes
            db.rollback()
            print(f"Error al procesar la asignación: {e}")
            return False
        
        finally:
            cursor.close()
            db.close()
    
    def liberar_orden(self, id_orden: int, id_empleado: int):
        # Verificamos si existe una asignación activa para esta orden y empleado
        asignada = self.verificar_asignacion(id_orden, id_empleado)
        if not asignada:
            print(f"No hay asignación activa para la orden {id_orden} y empleado {id_empleado}.")
            return False

        db = self.conexion1()
        if not db:
            return False
        
        cursor = db.cursor()
        try:
            # Iniciamos la transacción de forma explícita
            db.start_transaction()

            # Eliminar el registro de asignación en la tabla interaccion
            sql_delete = (
                "DELETE FROM interaccion "
                "WHERE ID_orden = %s AND ID_em = %s AND Accion = 'Asignado'"
            )
            cursor.execute(sql_delete, (id_orden, id_empleado))

            # Actualizar el estado de la orden a 'En Proceso'
            sql_orden = (
                "UPDATE orden_e "
                "SET Estado_o = 'En Proceso' "
                "WHERE ID_orden_servicio = %s"
            )
            cursor.execute(sql_orden, (id_orden,))

            # Guardamos los cambios
            db.commit()
            print("Liberación realizada con éxito.")
            return True

        except Exception as e:
            db.rollback()
            print(f"Error al liberar la orden: {e}")
            return False

        finally:
            cursor.close()
            db.close()
    
    def verificar_asignacion(self, id_orden: int, id_empleado: int):
        db = self.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            # Relacionamos las tablas por el ID de la orden
            sql = (
                "SELECT o.ID_orden_servicio, i.ID_em, o.Estado_o, i.Accion "
                "FROM orden_e o "
                "INNER JOIN interaccion i ON o.ID_orden_servicio = i.ID_orden "
                "WHERE o.ID_orden_servicio = %s "
                "AND i.ID_em = %s "
                "AND o.Estado_o = 'Asignado' "
                "AND i.Accion = 'Asignado'"
            )
            
            # Ejecutamos pasando ambos parámetros
            cursor.execute(sql, (id_orden, id_empleado))
            asignacion = cursor.fetchone()
            
            # Si encuentra el registro, significa que ambos están en estado 'Asignado'
            return asignacion
            
        except Exception as e:
            print(f"Error al verificar asignación: {e}")
            return None
            
        finally:
            cursor.close()
            db.close()


    def Orden_reparada(self, id_orden: int, id_productos, cantidades, id_empleado: int, reparacion: str):

        # Validación básica de parámetros
        if not isinstance(id_productos, (list, tuple)) or not isinstance(cantidades, (list, tuple)):
            return False
        if len(id_productos) != len(cantidades):
            return False

        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            db.start_transaction()

            sql_insert = (
                "INSERT INTO repuestos_u (ID_orden, ID_producto, Cantidad) "
                "VALUES (%s, %s, %s)"
            )
            for pid, qty in zip(id_productos, cantidades):
                cursor.execute(sql_insert, (id_orden, pid, qty))

            # Guardar texto de reparación en la orden
            sql_update_reparacion = (
                "UPDATE orden_e "
                "SET Reparacion = %s "
                "WHERE ID_orden_servicio = %s"
            )
            cursor.execute(sql_update_reparacion, (reparacion, id_orden))

            # Marcar orden como reparada
            sql_update = (
                "UPDATE orden_e "
                "SET Estado_o = 'Reparado' "
                "WHERE ID_orden_servicio = %s"
            )
            cursor.execute(sql_update, (id_orden,))

            sql_empleado = (
                "UPDATE interaccion "
                "SET Accion = 'Reparado' "
                "WHERE ID_orden = %s AND ID_em = %s"
            )
            cursor.execute(sql_empleado, (id_orden, id_empleado))

            db.commit()
            return True

        except Exception as e:
            db.rollback()
            print(f"Error al registrar reparación: {e}")
            return False

        finally:
            cursor.close()
            db.close()

"""