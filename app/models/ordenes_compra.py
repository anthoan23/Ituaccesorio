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
                SELECT o.ID_orden_c, p.N_proveedor, o.Fecha_o,  SUM(pp.Costo * oc.Cantidad_p) as Costo_venta, o.Estado
                FROM orden_compra o
                JOIN proveedor p ON o.ID_proveedor = p.ID_proveedor
                JOIN productos_orden oc On o.ID_orden_c = oc.ID_orden_c
                Join proveedores_productos pp On oc.ID_modelo = pp.ID_modelo
                WHERE o.Estado = 'Pendiente' OR o.Estado = 'Incompleto'
                GROUP BY o.ID_orden_c, p.N_proveedor, o.Fecha_o, o.Estado;
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()


    def obtener_detalles_orden(self, ID_orden_c: int):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            consulta1 = (
                """
                SELECT o.ID_orden_c, p.N_proveedor, o.Fecha_o,  SUM(pp.Costo * oc.Cantidad_p) as Costo_venta, o.Estado, em.Nombre_em, em.Apellido_em
                FROM orden_compra o
                JOIN proveedor p ON o.ID_proveedor = p.ID_proveedor
                JOIN productos_orden oc On o.ID_orden_c = oc.ID_orden_c
                Join proveedores_productos pp On oc.ID_modelo = pp.ID_modelo
                JOIN empleado em ON o.ID_em = em.ID_em
                WHERE o.ID_orden_c = %s 
                GROUP BY o.ID_orden_c, p.N_proveedor, o.Fecha_o, o.Estado, em.Nombre_em, em.Apellido_em;
                """
            )

            consulta2 = (
                """
                SELECT mp.N_marca ,m.N_modelo, p.Cantidad_p, pp.Costo, p.Cantidad_p * pp.Costo as sup_total FROM productos_orden p
                Join orden_compra o ON p.ID_orden_c = o.ID_orden_c
                JOin modelo_producto m On p.ID_modelo = m.ID_modelo
                Join proveedor pr On o.ID_proveedor = pr.ID_proveedor
                JOIN proveedores_productos pp on m.ID_modelo = pp.ID_modelo
                Join marca_producto mp ON m.ID_marca = mp.ID_marca
                where p.ID_orden_c = %s
                """
            )

            cursor.execute(consulta1, (ID_orden_c,))
            datos = cursor.fetchall()
            datos_orden = datos[0] if datos else None

            cursor.execute(consulta2, (ID_orden_c,))
            productos_orden = cursor.fetchall()

            return {
                "datos_orden": datos_orden,
                "productos_orden": productos_orden
            }
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


    def agregar_orden_compra(self, ID_em: int, ID_proveedor: int, productos: list | None = None):
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            consulta1 = (
                """
                INSERT INTO orden_compra (ID_em, ID_proveedor, Fecha_o, Estado) 
                VALUES (%s, %s, DATE_FORMAT(NOW(), '%Y-%m-%d'), 'Pendiente')
                """
            )

            consultar2 = (
                """
                INSERT INTO productos_orden (ID_orden_c, ID_modelo, Cantidad_p)
                VALUES (%s, %s, %s)
                """
            )  

            cursor.execute(consulta1, (ID_em, ID_proveedor))
            ID_orden_c = cursor.lastrowid
            # Insert each product row if an array of products was provided.
            # Each item in `productos` should be a dict-like object with keys
            # `ID_modelo` and `Cantidad_p`, or a tuple/list with those values.
            if productos:
                for p in productos:
                    try:
                        if isinstance(p, (list, tuple)):
                            mid, qty = p[0], p[1]
                        else:
                            mid = p.get('ID_modelo') if hasattr(p, 'get') else None
                            qty = p.get('Cantidad_p') if hasattr(p, 'get') else None
                        cursor.execute(consultar2, (ID_orden_c, mid, qty))
                    except Exception:
                        # If one product fails, roll back the whole transaction
                        raise
            db.commit()

        
            return True
        except Exception as e:
            print(f"Error al agregar orden de compra: {e}")
            db.rollback()
            return False
        finally:
            cursor.close()
            db.close()

    

    def actualizar_productos_orden(self, ID_orden_c: int, productos: list | None = None):
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            # First delete existing products for the order
            cursor.execute("DELETE FROM productos_orden WHERE ID_orden_c = %s", (ID_orden_c,))

            # Then insert the new products if provided
            if productos:
                for p in productos:
                    try:
                        if isinstance(p, (list, tuple)):
                            mid, qty = p[0], p[1]
                        else:
                            mid = p.get('ID_modelo') if hasattr(p, 'get') else None
                            qty = p.get('Cantidad_p') if hasattr(p, 'get') else None
                        cursor.execute(
                            """
                            INSERT INTO productos_orden (ID_orden_c, ID_modelo, Cantidad_p)
                            VALUES (%s, %s, %s)
                            """,
                            (ID_orden_c, mid, qty)
                        )
                    except Exception:
                        raise
            db.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar productos de la orden: {e}")
            db.rollback()
            return False
        finally:
            cursor.close()
            db.close()


    def anular_orden_compra(self, ID_orden_c: int):
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute("UPDATE orden_compra SET Estado = 'Anulada' WHERE ID_orden_c = %s", (ID_orden_c,))
            db.commit()
            return True
        except Exception as e:
            print(f"Error al anular la orden de compra: {e}")
            db.rollback()
            return False
        finally:
            cursor.close()
            db.close()


    


      

    

    