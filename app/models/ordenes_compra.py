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
                    DATE(o.Fecha_orden_compra) as Fecha_o,
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
                    DATE(o.Fecha_orden_compra) as Fecha_entrega,
                    COALESCE(SUM(d.Cantidad_producto * s.Costo_producto), 0) as Costo_venta
                FROM Orden_compra o
                JOIN Proveedor p ON o.ID_proveedor = p.ID_proveedor
                LEFT JOIN Detalle_orden d ON o.ID_orden_compra = d.ID_orden_compra
                LEFT JOIN Suministra s ON d.ID_producto = s.ID_producto AND o.ID_proveedor = s.ID_proveedor
                WHERE o.Estado_orden_compra = 'Completada'
                GROUP BY o.ID_orden_compra, p.Nombre_proveedor, o.Fecha_orden_compra
                ORDER BY o.Fecha_orden_compra DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error enlistar_ordenes_entregadas: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def obtener_detalles_orden(self, ID_orden_c: str):
        """Obtiene detalles completos de una orden - VERSIÓN SIMPLIFICADA"""
        db = self.conexion1()
        if not db:
            print("Error: No se pudo conectar a la base de datos")
            return None

        cursor = db.cursor(dictionary=True)
        try:
            print(f"=== Buscando orden: {ID_orden_c} ===")
            
            # PRIMERO: Verificar si la orden existe (SIN Recibido_por ni Fecha_entrega)
            cursor.execute("""
                SELECT 
                    o.ID_orden_compra as ID_orden_c,
                    o.ID_proveedor,
                    o.ID_empleado,
                    o.Fecha_orden_compra as Fecha_o,
                    o.Estado_orden_compra as Estado
                FROM Orden_compra o
                WHERE o.ID_orden_compra = %s
            """, (ID_orden_c,))
            
            datos_orden = cursor.fetchone()
            
            if not datos_orden:
                print(f"❌ Orden {ID_orden_c} no encontrada en tabla Orden_compra")
                return None
            
            print(f"✅ Orden encontrada: {datos_orden['ID_orden_c']}")
            
            # SEGUNDO: Obtener nombre del proveedor
            cursor.execute("""
                SELECT Nombre_proveedor as nombre
                FROM Proveedor
                WHERE ID_proveedor = %s
            """, (datos_orden["ID_proveedor"],))
            
            proveedor = cursor.fetchone()
            datos_orden["nombre"] = proveedor["nombre"] if proveedor else "Proveedor no encontrado"
            
            # TERCERO: Obtener nombre del empleado
            if datos_orden.get("ID_empleado"):
                cursor.execute("""
                    SELECT CONCAT(Nombre_empleado, ' ', Apellido_empleado) as Realizado_por
                    FROM Empleado
                    WHERE ID_empleado = %s
                """, (datos_orden["ID_empleado"],))
                empleado = cursor.fetchone()
                datos_orden["Realizado_por"] = empleado["Realizado_por"] if empleado else "Sistema"
            else:
                datos_orden["Realizado_por"] = "Sistema"
            
            # CUARTO: Calcular costo total
            cursor.execute("""
                SELECT COALESCE(SUM(d.Cantidad_producto * s.Costo_producto), 0) as Costo_venta
                FROM Detalle_orden d
                LEFT JOIN Suministra s ON d.ID_producto = s.ID_producto AND s.ID_proveedor = %s
                WHERE d.ID_orden_compra = %s
            """, (datos_orden["ID_proveedor"], ID_orden_c))
            
            total = cursor.fetchone()
            datos_orden["Costo_venta"] = float(total["Costo_venta"]) if total else 0
            
            # QUINTO: Obtener productos de la orden
            cursor.execute("""
                SELECT 
                    p.Nombre_producto as N_modelo,
                    COALESCE(mp.Nombre_marca, 'Sin marca') as N_marca,
                    COALESCE(cp.Nombre_Clase, 'Sin clase') as N_clase,
                    d.Cantidad_producto as Cantidad_p,
                    COALESCE(s.Costo_producto, 0) as Costo,
                    (d.Cantidad_producto * COALESCE(s.Costo_producto, 0)) as sup_total
                FROM Detalle_orden d
                JOIN Producto p ON d.ID_producto = p.ID_producto
                LEFT JOIN Suministra s ON d.ID_producto = s.ID_producto AND s.ID_proveedor = %s
                LEFT JOIN Marca_producto mp ON p.ID_marca = mp.ID_marca
                LEFT JOIN Clase_producto cp ON p.ID_Clase = cp.ID_Clase
                WHERE d.ID_orden_compra = %s
            """, (datos_orden["ID_proveedor"], ID_orden_c))
            
            productos_orden = cursor.fetchall()
            print(f"Productos encontrados: {len(productos_orden)}")
            print(f"Costo total: {datos_orden['Costo_venta']}")

            return {
                "datos_orden": datos_orden,
                "productos_orden": productos_orden
            }
        except Exception as e:
            print(f"Error obtener_detalles_orden: {e}")
            import traceback
            traceback.print_exc()
            return None
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
                    Nombre_proveedor as nombre,
                    Celular_proveedor as celular,
                    Correo_proveedor as correo
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
                    COALESCE(mp.Nombre_marca, 'Sin marca') as N_marca, 
                    COALESCE(cp.Nombre_Clase, 'Sin clase') as N_clase,
                    COALESCE(s.Costo_producto, 0) as Costo  
                FROM Suministra s 
                JOIN Producto p ON s.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto mp ON p.ID_marca = mp.ID_marca
                LEFT JOIN Clase_producto cp ON p.ID_Clase = cp.ID_Clase
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

    def agregar_orden_compra(self, ID_em: int, ID_proveedor: int, productos: list):
        """Agrega una nueva orden de compra"""
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            if not productos or len(productos) == 0:
                return False
            
            # Generar ID para la orden
            cursor.execute("SELECT MAX(ID_orden_compra) FROM Orden_compra")
            result = cursor.fetchone()
            last_id = result[0] if result and result[0] else "OC0000000"
            
            if last_id and last_id.startswith("OC"):
                try:
                    last_num = int(last_id[2:])
                except ValueError:
                    last_num = 0
            else:
                last_num = 0
            
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
                cursor.execute("""
                    INSERT INTO Detalle_orden (ID_orden_compra, ID_producto, Cantidad_producto)
                    VALUES (%s, %s, %s)
                """, (ID_orden, str(mid), qty))
            
            db.commit()
            print(f"Orden {ID_orden} creada exitosamente")
            return True
        except Exception as e:
            print(f"Error agregar_orden_compra: {e}")
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
            return False

        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE Orden_compra 
                SET Estado_orden_compra = 'Completada',
                    Recibido_por = %s,
                    Fecha_entrega = %s
                WHERE ID_orden_compra = %s AND Estado_orden_compra = 'Pendiente'
            """, (recibido_por, fecha_entrega, ID_orden_c))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error registrar_entrega: {e}")
            db.rollback()
            return False
        finally:
            cursor.close()
            db.close()