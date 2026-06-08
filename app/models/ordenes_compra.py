from __future__ import annotations
from app.models.database import conectar
from datetime import datetime
import mysql.connector


class OrdenCompra(conectar):
    
    def enlistar_ordenes_compra(self):
        """Lista órdenes pendientes"""
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
                    DATE_FORMAT(o.Fecha_orden_compra, '%%Y-%%m-%%d') as Fecha_o,
                    o.Estado_orden_compra as Estado,
                    COALESCE(SUM(d.Cantidad_producto * s.Costo_producto), 0) as Costo_venta
                FROM Orden_compra o
                JOIN Proveedor p ON o.ID_proveedor = p.ID_proveedor
                LEFT JOIN Detalle_orden d ON o.ID_orden_compra = d.ID_orden_compra
                LEFT JOIN Suministra s ON d.ID_producto = s.ID_producto AND o.ID_proveedor = s.ID_proveedor
                WHERE o.Estado_orden_compra = 'Pendiente'
                GROUP BY o.ID_orden_compra, o.ID_proveedor, p.Nombre_proveedor, o.Fecha_orden_compra, o.Estado_orden_compra
                ORDER BY o.Fecha_orden_compra DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error enlistar_ordenes_compra: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def enlistar_ordenes_entregadas(self):
        """Lista órdenes entregadas/completadas"""
        db = self.conexion1()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    o.ID_orden_compra as ID_orden_c,
                    p.Nombre_proveedor as N_proveedor,
                    DATE_FORMAT(o.Fecha_entrega, '%%Y-%%m-%%d') as Fecha_entrega,
                    o.Recibido_por,
                    COALESCE(SUM(d.Cantidad_producto * s.Costo_producto), 0) as Costo_venta
                FROM Orden_compra o
                JOIN Proveedor p ON o.ID_proveedor = p.ID_proveedor
                LEFT JOIN Detalle_orden d ON o.ID_orden_compra = d.ID_orden_compra
                LEFT JOIN Suministra s ON d.ID_producto = s.ID_producto AND o.ID_proveedor = s.ID_proveedor
                WHERE o.Estado_orden_compra = 'Completada'
                GROUP BY o.ID_orden_compra, p.Nombre_proveedor, o.Fecha_entrega, o.Recibido_por
                ORDER BY o.Fecha_entrega DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error enlistar_ordenes_entregadas: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def enlistar_proveedores(self):
        """Lista todos los proveedores"""
        db = self.conexion1()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    ID_proveedor as id, 
                    Nombre_proveedor as N_proveedor,
                    Celular_proveedor as celular,
                    Correo_proveedor as correo,
                    Direccion_proveedor as direccion,
                    Limite_credito as limite_credito
                FROM Proveedor 
                WHERE ID_proveedor IS NOT NULL
                ORDER BY Nombre_proveedor ASC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error enlistar_proveedores: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def obtener_productos_proveedor(self, ID_proveedor: int):
        """Obtiene productos que suministra un proveedor"""
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
                    cp.Nombre_Clase as N_clase,
                    s.Costo_producto as Costo  
                FROM Suministra s 
                JOIN Producto p ON s.ID_producto = p.ID_producto
                JOIN Marca_producto mp ON p.ID_marca = mp.ID_marca
                JOIN Clase_producto cp ON p.ID_Clase = cp.ID_Clase
                WHERE s.ID_proveedor = %s
                ORDER BY p.Nombre_producto ASC
            """, (ID_proveedor,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error obtener_productos_proveedor: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def obtener_detalles_orden(self, ID_orden_c: str):
        """Obtiene detalles completos de una orden"""
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
                    DATE_FORMAT(o.Fecha_orden_compra, '%%Y-%%m-%%d') as Fecha_o,
                    o.Estado_orden_compra as Estado,
                    CONCAT(e.Nombre_empleado, ' ', e.Apellido_empleado) as Realizado_por,
                    o.Recibido_por,
                    DATE_FORMAT(o.Fecha_entrega, '%%Y-%%m-%%d') as Fecha_entrega,
                    COALESCE(SUM(d.Cantidad_producto * s.Costo_producto), 0) as Costo_venta
                FROM Orden_compra o
                JOIN Proveedor p ON o.ID_proveedor = p.ID_proveedor
                LEFT JOIN Empleado e ON o.ID_empleado = e.ID_empleado
                LEFT JOIN Detalle_orden d ON o.ID_orden_compra = d.ID_orden_compra
                LEFT JOIN Suministra s ON d.ID_producto = s.ID_producto AND o.ID_proveedor = s.ID_proveedor
                WHERE o.ID_orden_compra = %s
                GROUP BY o.ID_orden_compra
            """, (ID_orden_c,))
            datos_orden = cursor.fetchone()
            
            if datos_orden:
                cursor.execute("""
                    SELECT 
                        p.Nombre_producto as N_modelo,
                        mp.Nombre_marca as N_marca,
                        cp.Nombre_Clase as N_clase,
                        d.Cantidad_producto as Cantidad_p,
                        s.Costo_producto as Costo,
                        (d.Cantidad_producto * s.Costo_producto) as sup_total
                    FROM Detalle_orden d
                    JOIN Producto p ON d.ID_producto = p.ID_producto
                    JOIN Suministra s ON d.ID_producto = s.ID_producto AND s.ID_proveedor = %s
                    JOIN Marca_producto mp ON p.ID_marca = mp.ID_marca
                    JOIN Clase_producto cp ON p.ID_Clase = cp.ID_Clase
                    WHERE d.ID_orden_compra = %s
                """, (datos_orden.get("ID_proveedor"), ID_orden_c))
                productos_orden = cursor.fetchall()
            else:
                productos_orden = []

            return {
                "datos_orden": datos_orden,
                "productos_orden": productos_orden
            }
        except Exception as e:
            print(f"Error obtener_detalles_orden: {e}")
            return None
        finally:
            cursor.close()
            db.close()

    def agregar_orden_compra(self, ID_em: int, ID_proveedor: int, productos: list):
        """Agrega una nueva orden de compra"""
        db = self.conexion1()
        if not db:
            print("Error: No se pudo conectar a la base de datos")
            return False

        cursor = db.cursor()
        try:
            if not productos or len(productos) == 0:
                print("Error: No hay productos para agregar")
                return False
            
            # Generar ID para la orden
            cursor.execute("SELECT MAX(CAST(SUBSTRING(ID_orden_compra, 3) AS UNSIGNED)) FROM Orden_compra")
            result = cursor.fetchone()
            last_num = result[0] if result and result[0] else 0
            new_num = last_num + 1
            ID_orden = f"OC{str(new_num).zfill(7)}"
            
            print(f"Generando orden: {ID_orden}")
            
            # Insertar orden
            cursor.execute("""
                INSERT INTO Orden_compra (ID_orden_compra, ID_empleado, ID_proveedor, Fecha_orden_compra, Estado_orden_compra) 
                VALUES (%s, %s, %s, NOW(), 'Pendiente')
            """, (ID_orden, ID_em, ID_proveedor))
            
            # Insertar detalles
            for mid, qty in productos:
                print(f"Insertando producto: ID_producto={mid}, Cantidad={qty}")
                cursor.execute("""
                    INSERT INTO Detalle_orden (ID_orden_compra, ID_producto, Cantidad_producto)
                    VALUES (%s, %s, %s)
                """, (ID_orden, str(mid), qty))
            
            db.commit()
            print(f"Orden {ID_orden} creada exitosamente")
            return True
        except mysql.connector.Error as err:
            print(f"Error SQL: {err}")
            db.rollback()
            return False
        except Exception as e:
            print(f"Error general: {e}")
            db.rollback()
            return False
        finally:
            cursor.close()
            db.close()

    def anular_orden_compra(self, ID_orden_c: str):
        """Anula una orden de compra"""
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE Orden_compra 
                SET Estado_orden_compra = 'Anulada' 
                WHERE ID_orden_compra = %s AND Estado_orden_compra = 'Pendiente'
            """, (ID_orden_c,))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error anular_orden_compra: {e}")
            db.rollback()
            return False
        finally:
            cursor.close()
            db.close()
    
    def registrar_entrega(self, ID_orden_c: str, recibido_por: str, fecha_entrega: str):
        """Registra la entrega de una orden"""
        db = self.conexion1()
        if not db:
            print("Error: No se pudo conectar a la base de datos")
            return False

        cursor = db.cursor()
        try:
            # Primero verificar si la orden existe y está pendiente
            cursor.execute("""
                SELECT Estado_orden_compra FROM Orden_compra 
                WHERE ID_orden_compra = %s
            """, (ID_orden_c,))
            resultado = cursor.fetchone()
            
            if not resultado:
                print(f"Orden {ID_orden_c} no encontrada")
                return False
            
            estado_actual = resultado[0]
            print(f"Estado actual de la orden: {estado_actual}")
            
            if estado_actual != 'Pendiente':
                print(f"La orden no está pendiente. Estado actual: {estado_actual}")
                return False
            
            # Actualizar la orden
            cursor.execute("""
                UPDATE Orden_compra 
                SET Estado_orden_compra = 'Completada',
                    Recibido_por = %s,
                    Fecha_entrega = %s
                WHERE ID_orden_compra = %s AND Estado_orden_compra = 'Pendiente'
            """, (recibido_por, fecha_entrega, ID_orden_c))
            
            db.commit()
            print(f"Orden {ID_orden_c} actualizada. Filas afectadas: {cursor.rowcount}")
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error registrar_entrega: {e}")
            db.rollback()
            return False
        finally:
            cursor.close()
            db.close()