from __future__ import annotations

from datetime import date

from app.models.database import conectar

class OrdenServicio(conectar):

    def listado_ordenes(self):
        db = self.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                "SELECT o.ID_orden_e AS ID_orden, "
                "o.Estado_o AS Estado, "
                "m.N_modelo AS Modelo, "
                "o.Des_cliente, "
                "o.Fecha_e "
                "FROM orden_e o JOIN modelo_producto m ON o.ID_modelo = m.ID_modelo"
            )
            cursor.execute(sql)
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

    

