from __future__ import annotations

from datetime import date

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
                "WHERE o.Estado_o = 'Asignado' AND i.ID_em = %s"
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
                "m.N_modelo AS Modelo "
                "FROM orden_e o JOIN modelo_producto m ON o.ID_modelo = m.ID_modelo "
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

