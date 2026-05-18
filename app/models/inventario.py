from __future__ import annotations

from app.models.database import conectar

class Inventario(conectar):

    def listar_inventario(self):
        db = self.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                "SELECT c.N_Clase AS tipo, mp.N_marca, m.N_modelo, s.Existencia, s.Costo_venta, s.ID_producto FROM stock s "
                "JOIN modelo_producto m ON s.ID_modelo = m.ID_modelo "
                " JOIN marca_producto mp ON m.ID_marca = mp.ID_marca "
                " JOIN clase_producto c ON mp.ID_clase = c.ID_clase "
                "Where s.Num_i = 2 "
            )
            cursor.execute(sql)
            inventario = cursor.fetchall()
        
            return inventario
        
        finally:
            cursor.close()
            db.close()

    def listar_inventario_modelo(self, N_modelo: str):
        db = self.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                "SELECT c.N_Clase AS tipo, mp.N_marca, m.N_modelo, s.Existencia, s.Costo_venta, s.ID_producto FROM stock s "
                "JOIN modelo_producto m ON s.ID_modelo = m.ID_modelo "
                " JOIN marca_producto mp ON m.ID_marca = mp.ID_marca "
                " JOIN clase_producto c ON mp.ID_clase = c.ID_clase "
                "Where s.Num_i = 2 AND m.N_modelo = %s"
            )
            cursor.execute(sql, (N_modelo,))
            inventario = cursor.fetchall()
        
            return inventario
        
        finally:
            cursor.close()
            db.close()

