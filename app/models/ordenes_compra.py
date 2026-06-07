from __future__ import annotations
from app.models.database import conectar
from datetime import datetime


class OrdenCompra(conectar):
    
    def enlistar_ordenes_compra(self):
        db = self.conexion1()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    o.ID_orden_compra as ID_orden_c,
                    o.ID_proveedor,
                    p.Nombre_proveedor as N_proveedor,
                    o.Fecha_orden_compra as Fecha_o,
                    o.Estado_orden_compra as Estado
                FROM Orden_compra o
                JOIN Proveedor p ON o.ID_proveedor = p.ID_proveedor
                WHERE o.Estado_orden_compra = 'Pendiente'
                ORDER BY o.Fecha_orden_compra DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def enlistar_ordenes_compra_todas(self):
        db = self.conexion1()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    o.ID_orden_compra as ID_orden_c,
                    o.ID_proveedor,
                    p.Nombre_proveedor as N_proveedor,
                    o.Fecha_orden_compra as Fecha_o,
                    o.Estado_orden_compra as Estado
                FROM Orden_compra o
                JOIN Proveedor p ON o.ID_proveedor = p.ID_proveedor
                ORDER BY o.Fecha_orden_compra DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def enlistar_ordenes_entregadas(self):
        db = self.conexion1()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    o.ID_orden_compra as ID_orden_c,
                    p.Nombre_proveedor as N_proveedor,
                    o.Fecha_orden_compra as Fecha_o,
                    o.Estado_orden_compra as Estado
                FROM Orden_compra o
                JOIN Proveedor p ON o.ID_proveedor = p.ID_proveedor
                WHERE o.Estado_orden_compra = 'Completada'
                ORDER BY o.Fecha_orden_compra DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def obtener_detalles_orden(self, ID_orden_c: str):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    o.ID_orden_compra as ID_orden_c,
                    o.ID_proveedor,
                    p.Nombre_proveedor as N_proveedor,
                    o.Fecha_orden_compra as Fecha_o,
                    o.Estado_orden_compra as Estado,
                    e.Nombre_empleado as Nombre_em,
                    e.Apellido_empleado as Apellido_em
                FROM Orden_compra o
                JOIN Proveedor p ON o.ID_proveedor = p.ID_proveedor
                LEFT JOIN Empleado e ON o.ID_empleado = e.ID_empleado
                WHERE o.ID_orden_compra = %s
            """, (ID_orden_c,))
            datos_orden = cursor.fetchone()
            
            cursor.execute("""
                SELECT 
                    prod.Nombre_producto as N_modelo,
                    mp.Nombre_marca as N_marca,
                    d.Cantidad_producto as Cantidad_p,
                    s.Costo_producto as Costo
                FROM Detalle_orden d
                JOIN Producto prod ON d.ID_producto = prod.ID_producto
                JOIN Suministra s ON d.ID_producto = s.ID_producto AND d.ID_orden_compra = s.ID_proveedor
                JOIN Marca_producto mp ON prod.ID_marca = mp.ID_marca
                WHERE d.ID_orden_compra = %s
            """, (ID_orden_c,))
            productos_orden = cursor.fetchall()

            return {
                "datos_orden": datos_orden,
                "productos_orden": productos_orden
            }
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            cursor.close()
            db.close()

    def enlistar_proveedores(self):
        db = self.conexion1()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT ID_proveedor, Nombre_proveedor as N_proveedor FROM Proveedor ORDER BY Nombre_proveedor ASC")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def obtener_productos_proveedor(self, ID_proveedor: int):
        db = self.conexion1()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    s.ID_producto as ID_modelo, 
                    p.Nombre_producto as N_modelo, 
                    mp.Nombre_marca as N_marca, 
                    s.Costo_producto as Costo  
                FROM Suministra s 
                JOIN Producto p ON s.ID_producto = p.ID_producto
                JOIN Marca_producto mp ON p.ID_marca = mp.ID_marca
                WHERE s.ID_proveedor = %s
            """, (ID_proveedor,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def agregar_orden_compra(self, ID_em: int, ID_proveedor: int, productos: list):
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            # Generar ID para la orden (formato: OC0000001)
            cursor.execute("SELECT MAX(ID_orden_compra) FROM Orden_compra")
            last_id = cursor.fetchone()[0]
            if last_id:
                num = int(last_id[2:]) + 1
                ID_orden = f"OC{str(num).zfill(7)}"
            else:
                ID_orden = "OC0000001"
            
            # Insertar orden
            cursor.execute("""
                INSERT INTO Orden_compra (ID_orden_compra, ID_empleado, ID_proveedor, Fecha_orden_compra, Estado_orden_compra) 
                VALUES (%s, %s, %s, NOW(), 'Pendiente')
            """, (ID_orden, ID_em, ID_proveedor))
            
            # Insertar detalles
            for mid, qty in productos:
                cursor.execute("""
                    INSERT INTO Detalle_orden (ID_orden_compra, ID_producto, Cantidad_producto)
                    VALUES (%s, %s, %s)
                """, (ID_orden, str(mid), qty))
            
            db.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            db.rollback()
            return False
        finally:
            cursor.close()
            db.close()

    def actualizar_productos_orden(self, ID_orden_c: str, productos: list):
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM Detalle_orden WHERE ID_orden_compra = %s", (ID_orden_c,))

            for mid, qty in productos:
                cursor.execute("""
                    INSERT INTO Detalle_orden (ID_orden_compra, ID_producto, Cantidad_producto)
                    VALUES (%s, %s, %s)
                """, (ID_orden_c, str(mid), qty))
            
            db.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            db.rollback()
            return False
        finally:
            cursor.close()
            db.close()

    def anular_orden_compra(self, ID_orden_c: str):
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute("UPDATE Orden_compra SET Estado_orden_compra = 'Anulada' WHERE ID_orden_compra = %s", (ID_orden_c,))
            db.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            db.rollback()
            return False
        finally:
            cursor.close()
            db.close()
    
    def registrar_entrega(self, ID_orden_c: str, recibido_por: str, fecha_entrega: str):
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE Orden_compra 
                SET Estado_orden_compra = 'Completada'
                WHERE ID_orden_compra = %s
            """, (ID_orden_c,))
            db.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            db.rollback()
            return False
        finally:
            cursor.close()
            db.close()