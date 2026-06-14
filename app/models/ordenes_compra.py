from __future__ import annotations
from app.models.database import conectar
from app.models.bitacora import Bitacora
from datetime import datetime
import mysql.connector


class OrdenCompra(conectar):
    
    def __init__(self, id_orden: str = None, id_empleado: int = None, 
                 id_proveedor: int = None, productos: list = None,
                 recibido_por: str = None, fecha_entrega: str = None,
                 usuario_id: str = None):
        super().__init__()
        self.id_orden = id_orden
        self.id_empleado = id_empleado
        self.id_proveedor = id_proveedor
        self.productos = productos or []
        self.recibido_por = recibido_por
        self.fecha_entrega = fecha_entrega
        self.usuario_id = usuario_id
    
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
                    DATE(ei.Fecha_entrega_inventario) as Fecha_entrega,
                    CONCAT(emp.Nombre_empleado, ' ', emp.Apellido_empleado) as Recibido_por,
                    COALESCE(SUM(d.Cantidad_producto * s.Costo_producto), 0) as Costo_venta
                FROM Orden_compra o
                JOIN Proveedor p ON o.ID_proveedor = p.ID_proveedor
                JOIN Entrega_inventario ei ON o.ID_orden_compra = ei.ID_orden_compra
                JOIN Empleado emp ON ei.ID_empleado = emp.ID_empleado
                LEFT JOIN Detalle_orden d ON o.ID_orden_compra = d.ID_orden_compra
                LEFT JOIN Suministra s ON d.ID_producto = s.ID_producto AND o.ID_proveedor = s.ID_proveedor
                WHERE o.Estado_orden_compra = 'Completada'
                GROUP BY o.ID_orden_compra, p.Nombre_proveedor, ei.Fecha_entrega_inventario, emp.Nombre_empleado, emp.Apellido_empleado
                ORDER BY ei.Fecha_entrega_inventario DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error enlistar_ordenes_entregadas: {e}")
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
                    o.ID_empleado,
                    DATE(o.Fecha_orden_compra) as Fecha_o,
                    o.Estado_orden_compra as Estado
                FROM Orden_compra o
                WHERE o.ID_orden_compra = %s
                GROUP BY o.ID_orden_compra
            """, (ID_orden_c,))
            datos_orden = cursor.fetchone()
            if not datos_orden:
                return None
            
            cursor.execute("""
                SELECT Nombre_proveedor as nombre
                FROM Proveedor
                WHERE ID_proveedor = %s
            """, (datos_orden["ID_proveedor"],))
            
            proveedor = cursor.fetchone()
            datos_orden["nombre"] = proveedor["nombre"] if proveedor else "Proveedor no encontrado"
            
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
            
            cursor.execute("""
                SELECT COALESCE(SUM(d.Cantidad_producto * s.Costo_producto), 0) as Costo_venta
                FROM Detalle_orden d
                LEFT JOIN Suministra s ON d.ID_producto = s.ID_producto AND s.ID_proveedor = %s
                WHERE d.ID_orden_compra = %s
            """, (datos_orden["ID_proveedor"], ID_orden_c))
            
            total = cursor.fetchone()
            datos_orden["Costo_venta"] = float(total["Costo_venta"]) if total else 0
            
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
            """, (datos_orden.get("ID_proveedor"), ID_orden_c))
            productos_orden = cursor.fetchall()

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

    def enlistar_empleados(self):
        """Lista todos los empleados para el selector"""
        db = self.conexion1()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    ID_empleado as id,
                    Nombre_empleado as nombre,
                    Apellido_empleado as apellido
                FROM Empleado 
                WHERE ID_empleado IS NOT NULL
                ORDER BY Nombre_empleado ASC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error enlistar_empleados: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def obtener_productos_proveedor(self, ID_proveedor: int):
        """Obtiene productos que suministra un proveedor"""
        if not self.id_proveedor:
            return []

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
            """, (self.id_proveedor,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error obtener_productos_proveedor: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def agregar_orden_compra(self) -> bool:
        """Agrega una nueva orden de compra"""
        if not self.id_empleado or not self.id_proveedor or not self.productos:
            print("Error: Faltan datos para crear la orden")
            return False

        db = self.conexion1()
        if not db:
            return False

        cursor = None
        try:
            cursor = db.cursor()
            
            if not productos:
                return False
            
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
            self.id_orden = f"OC{str(new_num).zfill(7)}"
            
            cursor.execute("""
                INSERT INTO Orden_compra (ID_orden_compra, ID_empleado, ID_proveedor, Fecha_orden_compra, Estado_orden_compra) 
                VALUES (%s, %s, %s, NOW(), 'Pendiente')
            """, (self.id_orden, self.id_empleado, self.id_proveedor))
            
            for mid, qty in productos:
                print(f"Insertando producto: ID_producto={mid}, Cantidad={qty}")
                cursor.execute("""
                    INSERT INTO Detalle_orden (ID_orden_compra, ID_producto, Cantidad_producto)
                    VALUES (%s, %s, %s)
                """, (self.id_orden, str(mid), qty))
            
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error agregar_orden_compra: {e}")
            if db:
                db.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def anular_orden_compra(self) -> bool:
        """Anula una orden de compra"""
        if not self.id_orden:
            return False

        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE Orden_compra 
                SET Estado_orden_compra = 'Anulada' 
                WHERE ID_orden_compra = %s AND Estado_orden_compra = 'Pendiente'
            """, (self.id_orden,))
            db.commit()
            anulado = cursor.rowcount > 0
            
            if anulado and self.usuario_id:
                bitacora = Bitacora(
                    accion="Anular orden de compra",
                    descripcion=f"Se anuló la orden de compra ID: {self.id_orden}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Órdenes de compra"
                )
                bitacora.registrar()
            
            return anulado
        except Exception as e:
            print(f"Error anular_orden_compra: {e}")
            db.rollback()
            return False
        finally:
            cursor.close()
            db.close()
    
    def registrar_entrega(self, ID_orden_c: str, recibido_por: str, fecha_entrega: str, id_empleado: int):
        """
        Registra la entrega de una orden.
        Si el producto no existe en Existencias_productos, lo crea.
        Luego aumenta el stock.
        """
        db = self.conexion1()
        if not db:
            return False

        cursor = None
        try:
            cursor = db.cursor()
            
            # 1. Verificar si la orden existe y está pendiente
            cursor.execute("""
                SELECT ID_orden_compra, Estado_orden_compra FROM Orden_compra 
                WHERE ID_orden_compra = %s
            """, (ID_orden_c,))
            resultado = cursor.fetchone()
            
            if not resultado or resultado[1] != 'Pendiente':
                return False
            
            # 2. Obtener los detalles de la orden con costo de suministra
            cursor.execute("""
                SELECT 
                    d.ID_producto,
                    d.Cantidad_producto,
                    s.Costo_producto
                FROM Detalle_orden d
                JOIN Suministra s ON d.ID_producto = s.ID_producto AND s.ID_proveedor = (
                    SELECT ID_proveedor FROM Orden_compra WHERE ID_orden_compra = %s
                )
                WHERE d.ID_orden_compra = %s
            """, (ID_orden_c, ID_orden_c))
            
            detalles = cursor.fetchall()
            if not detalles:
                return False
            
            # 3. Generar ID para la entrega de inventario
            cursor.execute("SELECT MAX(ID_entrega_inventario) FROM Entrega_inventario")
            result = cursor.fetchone()
            last_id = result[0] if result and result[0] else "ENT0000000"
            last_num = int(last_id[3:]) if last_id and last_id.startswith("ENT") else 0
            ID_entrega = f"ENT{str(last_num + 1).zfill(7)}"
            
            # 4. Insertar en Entrega_inventario
            cursor.execute("""
                INSERT INTO Entrega_inventario (ID_entrega_inventario, ID_empleado, ID_orden_compra, Fecha_entrega_inventario)
                VALUES (%s, %s, %s, NOW())
            """, (ID_entrega, id_empleado, ID_orden_c))
            
            # 5. Para cada producto, verificar/crear en Existencias_productos y actualizar stock
            for detalle in detalles:
                id_producto = detalle[0]
                cantidad = detalle[1]
                costo_compra = float(detalle[2]) if detalle[2] else 0
                
                # Calcular costo de venta (ej: 30% de ganancia)
                costo_venta = round(costo_compra * 1.3, 2)
                
                # Verificar si el producto ya existe en Existencias_productos
                cursor.execute("""
                    SELECT ID_inventario, Existencia FROM Existencias_productos 
                    WHERE ID_producto = %s
                """, (id_producto,))
                inventario_existente = cursor.fetchone()
                
                if inventario_existente:
                    # Ya existe, actualizar stock
                    id_inventario = inventario_existente[0]
                    
                    # Insertar en Abastece
                    cursor.execute("""
                        INSERT INTO Abastece (ID_entrega_inventario, ID_inventario, Cantidad_entregada)
                        VALUES (%s, %s, %s)
                    """, (ID_entrega, id_inventario, cantidad))
                    
                    # Actualizar stock
                    cursor.execute("""
                        UPDATE Existencias_productos 
                        SET Existencia = Existencia + %s
                        WHERE ID_inventario = %s
                    """, (cantidad, id_inventario))
                    print(f"Stock actualizado para producto {id_producto}: +{cantidad}")
                else:
                    # No existe, crear nuevo registro
                    cursor.execute("SELECT MAX(CAST(ID_inventario AS UNSIGNED)) FROM Existencias_productos")
                    result = cursor.fetchone()
                    last_inv_id = result[0] if result and result[0] else 0
                    new_inv_id = str(last_inv_id + 1)
                    
                    # Insertar nuevo inventario
                    cursor.execute("""
                        INSERT INTO Existencias_productos (ID_inventario, ID_producto, Existencia, Costo_venta)
                        VALUES (%s, %s, %s, %s)
                    """, (new_inv_id, id_producto, cantidad, costo_venta))
                    print(f"Nuevo inventario creado para producto {id_producto}: +{cantidad}")
                    
                    # Insertar en Abastece
                    cursor.execute("""
                        INSERT INTO Abastece (ID_entrega_inventario, ID_inventario, Cantidad_entregada)
                        VALUES (%s, %s, %s)
                    """, (ID_entrega, new_inv_id, cantidad))
            
            # 6. Actualizar estado de la orden a Completada
            cursor.execute("""
                UPDATE Orden_compra 
                SET Estado_orden_compra = 'Completada'
                WHERE ID_orden_compra = %s
            """, (ID_orden_c,))
            
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error registrar_entrega: {e}")
            if db:
                db.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()