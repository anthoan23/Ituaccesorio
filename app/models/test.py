from __future__ import annotations

from datetime import date

from app.models.database import conectar

class Tests(conectar):

    def buscar_ordenes(self, id_orden: int):
        db = self.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                "SELECT o.ID_orden , t.* FROM revision_orden o JOIN test t ON o.ID_test = t.ID_test WHERE o.ID_orden = %s"
            )
            cursor.execute(sql, (id_orden,))
            ordenes = cursor.fetchall()
        
            return ordenes
        
        finally:
            cursor.close()
            db.close()


    