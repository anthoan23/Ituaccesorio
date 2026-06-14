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
                    DATE(o.Fecha_entrega) as Fecha_entrega,
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

    def obtener_detalles_orden(self):
        """Obtiene detalles completos de una orden"""
        if not self.id_orden:
            return None

        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    o.ID_orden_compra as ID_orden_c,
                    o.ID_proveedor,
                    p.Nombre_proveedor as nombre,
                    DATE(o.Fecha_orden_compra) as Fecha_o,
                    o.Estado_orden_compra as Estado,
                    CONCAT(e.Nombre_empleado, ' ', e.Apellido_empleado) as Realizado_por,
                    o.Recibido_por,
                    DATE(o.Fecha_entrega) as Fecha_entrega,
                    COALESCE(SUM(d.Cantidad_producto * s.Costo_producto), 0) as Costo_venta
                FROM Orden_compra o
                JOIN Proveedor p ON o.ID_proveedor = p.ID_proveedor
                LEFT JOIN Empleado e ON o.ID_empleado = e.ID_empleado
                LEFT JOIN Detalle_orden d ON o.ID_orden_compra = d.ID_orden_compra
                LEFT JOIN Suministra s ON d.ID_producto = s.ID_producto AND o.ID_proveedor = s.ID_proveedor
                WHERE o.ID_orden_compra = %s
                GROUP BY o.ID_orden_compra
            """, (self.id_orden,))
            datos_orden = cursor.fetchone()
            
            if not datos_orden:
                print(f"No se encontró la orden: {self.id_orden}")
                return None
            
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
            """, (datos_orden.get("ID_proveedor"), self.id_orden))
            productos_orden = cursor.fetchall()

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
                    Nombre_proveedor as N_proveedor,
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

    def obtener_productos_proveedor(self):
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
                    mp.Nombre_marca as N_marca, 
                    cp.Nombre_Clase as N_clase,
                    s.Costo_producto as Costo  
                FROM Suministra s 
                JOIN Producto p ON s.ID_producto = p.ID_producto
                JOIN Marca_producto mp ON p.ID_marca = mp.ID_marca
                JOIN Clase_producto cp ON p.ID_Clase = cp.ID_Clase
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
            print("Error: No se pudo conectar a la base de datos")
            return False

        cursor = db.cursor()
        try:
            if len(self.productos) == 0:
                print("Error: No hay productos para agregar")
                return False
            
            cursor.execute("SELECT MAX(CAST(SUBSTRING(ID_orden_compra, 3) AS UNSIGNED)) FROM Orden_compra")
            result = cursor.fetchone()
            last_num = result[0] if result and result[0] else 0
            new_num = last_num + 1
            self.id_orden = f"OC{str(new_num).zfill(7)}"
            
            cursor.execute("""
                INSERT INTO Orden_compra (ID_orden_compra, ID_empleado, ID_proveedor, Fecha_orden_compra, Estado_orden_compra) 
                VALUES (%s, %s, %s, NOW(), 'Pendiente')
            """, (self.id_orden, self.id_empleado, self.id_proveedor))
            
            for mid, qty in self.productos:
                cursor.execute("""
                    INSERT INTO Detalle_orden (ID_orden_compra, ID_producto, Cantidad_producto)
                    VALUES (%s, %s, %s)
                """, (self.id_orden, str(mid), qty))
            
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Crear orden de compra",
                    descripcion=f"Se creó la orden de compra ID: {self.id_orden} - Proveedor ID: {self.id_proveedor}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Órdenes de compra"
                )
                bitacora.registrar()
            
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
    
    def registrar_entrega(self) -> bool:
        """Registra la entrega de una orden"""
        if not self.id_orden:
            print("Error: ID de orden no especificado")
            return False

        db = self.conexion1()
        if not db:
            print("Error: No se pudo conectar a la base de datos")
            return False

        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT ID_orden_compra, Estado_orden_compra FROM Orden_compra 
                WHERE ID_orden_compra = %s
            """, (self.id_orden,))
            resultado = cursor.fetchone()
            
            if not resultado:
                print(f"Orden {self.id_orden} no encontrada")
                return False
            
            estado_actual = resultado[1] if len(resultado) > 1 else resultado[0]
            
            if estado_actual != 'Pendiente':
                print(f"La orden no está pendiente. Estado actual: {estado_actual}")
                return False
            
            if not self.fecha_entrega:
                self.fecha_entrega = datetime.now().strftime("%Y-%m-%d")
            
            cursor.execute("""
                UPDATE Orden_compra 
                SET Estado_orden_compra = 'Completada',
                    Recibido_por = %s,
                    Fecha_entrega = %s
                WHERE ID_orden_compra = %s AND Estado_orden_compra = 'Pendiente'
            """, (self.recibido_por, self.fecha_entrega, self.id_orden))
            
            db.commit()
            registrado = cursor.rowcount > 0
            
            if registrado and self.usuario_id:
                bitacora = Bitacora(
                    accion="Registrar entrega de orden",
                    descripcion=f"Se registró la entrega de la orden ID: {self.id_orden} - Recibido por: {self.recibido_por}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Órdenes de compra"
                )
                bitacora.registrar()
            
            return registrado
        except Exception as e:
            print(f"Error registrar_entrega: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
            return False
        finally:
            cursor.close()
            db.close()