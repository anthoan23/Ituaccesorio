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
                "SELECT o.ID_orden_e AS ID_orden, "
                "o.Estado_o AS Estado, "
                "o.ID_c AS ID_cliente, "
                "c.Nombre_c AS Nombre_cliente, "
                "c.Apellido_c AS Apellido_cliente, "
                "m.N_modelo AS Modelo, "
                "o.Des_cliente, "
                "o.Fecha_e "
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

    def ordenes_asignadas_empleado(self):
        db = self.conexion1()
        if not db:
            return None

        id_empleado = 1004
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                "SELECT i.ID_orden, m.N_modelo "
                "FROM interaccion i JOIN orden_e o ON i.ID_orden = o.ID_orden_e "
                "JOIN modelo_producto m ON o.ID_modelo = m.ID_modelo "
                "WHERE o.Estado_o IN ('Asignado', 'Revisado') AND i.ID_em = %s"
            )
            cursor.execute(sql, (id_empleado,))
            ordenes = cursor.fetchall()
        
            return ordenes
        
        finally:
            cursor.close()
            db.close()

    def detalles_orden(self, id_orden: int):
        db = self.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                "SELECT o.*, "
                "m.N_modelo AS Modelo, "
                "c.Nombre_c AS Nombre_cliente, "
                "c.Apellido_c AS Apellido_cliente "
                "FROM orden_e o JOIN modelo_producto m ON o.ID_modelo = m.ID_modelo "
                "JOIN cliente c ON o.ID_c = c.ID_c "
                "WHERE o.ID_orden_e = %s"
            )
            cursor.execute(sql, (id_orden,))
            orden = cursor.fetchone()
        
            return orden
        
        finally:
            cursor.close()
            db.close()
    
    def empleados_asignados(self, id_orden: int):
        db = self.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                "SELECT i.Accion, e.* "
                "FROM interaccion i JOIN empleado e ON i.ID_em = e.ID_em "
                "WHERE i.ID_orden = %s"
            )
            cursor.execute(sql, (id_orden,))
            empleados = cursor.fetchall()
        
            return empleados
        
        finally:
            cursor.close()
            db.close()

    def fotos_orden(self, id_orden: int):
        db = self.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                "SELECT * FROM evidencia_e "
                "WHERE ID_orden = %s"
            )
            cursor.execute(sql, (id_orden,))
            fotos = cursor.fetchall()
        
            return fotos
        
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
                "WHERE ID_orden_e = %s"
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
                "WHERE ID_orden_e = %s"
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
                "SELECT o.ID_orden_e, i.ID_em, o.Estado_o, i.Accion "
                "FROM orden_e o "
                "INNER JOIN interaccion i ON o.ID_orden_e = i.ID_orden "
                "WHERE o.ID_orden_e = %s "
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

