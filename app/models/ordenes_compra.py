from __future__ import annotations
from app.models.database import conectar

class OrdenCompra(conectar):
    
    def enlistar_ordenes_compra(self):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT * FROM ordenes_compra")
        ordenes = cursor.fetchall()
        return ordenes