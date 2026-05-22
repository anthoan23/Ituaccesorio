from __future__ import annotations
from app.models.database import conectar

class OrdenCompra(conectar):
    
    def enlistar_ordenes_compra(self):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT o.ID_orden_c, p.N_proveedor, o.Fecha_o, o.Costo_venta, o.Estado
                FROM orden_compra o
                JOIN proveedor p ON o.ID_proveedor = p.ID_proveedor
                WHERE o.Estado = 'Pendiente' OR o.Estado = 'Incompleto'
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def enlistar_proveedores(self):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT ID_proveedor, N_proveedor FROM proveedor")
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def obtener_productos_proveedor(self, ID_proveedor: int):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT p.ID_modelo, m.N_modelo, ma.N_marca, c.N_Clase, p.Costo  FROM proveedores_productos p join modelo_producto m On p.ID_modelo = m.ID_modelo
                Join marca_producto ma On m.ID_marca = ma.ID_marca
                Join clase_producto c on ma.ID_marca = c.ID_clase
                where p.ID_proveedor = %s
                """,
                (ID_proveedor,)
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()


    def agregar_orden_compra(self, ID_em: int, ID_proveedor: int, Costo_venta: int):
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO orden_compra (ID_em, ID_proveedor, Fecha_o, Costo_venta, Estado)
                VALUES (%s, %s, NOW(), %s, 'Pendiente')
                """,
                (ID_em, ID_proveedor, Costo_venta)
            )
            db.commit()
            return True
        except Exception as e:
            print(f"Error al agregar orden de compra: {e}")
            db.rollback()
            return False
        finally:
            cursor.close()
            db.close()  


      

    

    