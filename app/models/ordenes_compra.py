from __future__ import annotations
from app.models.database import conectar
from app.models.bitacora import Bitacora
from datetime import datetime


class OrdenCompra:
    """Modelo para Órdenes de Compra"""
    
    def __init__(self, id_orden: str = None, id_empleado: int = None, 
                 id_proveedor: int = None, productos: list = None,
                 usuario_id: str = None):
        self.id_orden = id_orden
        self.id_empleado = id_empleado
        self.id_proveedor = id_proveedor
        self.productos = productos or []
        self.usuario_id = usuario_id
        self.__conexion_bd = conectar()
    
    def _conexion(self):
        return self.__conexion_bd.conexion1()
    
    def listar_ordenes_pendientes(self):
        """Lista órdenes pendientes de entrega"""
        db = self._conexion()
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
                    COALESCE((
                        SELECT SUM(d2.Cantidad_producto * COALESCE(s2.Costo_producto, 0))
                        FROM Detalle_orden d2
                        LEFT JOIN Suministra s2 ON d2.ID_producto = s2.ID_producto AND s2.ID_proveedor = o.ID_proveedor
                        WHERE d2.ID_orden_compra = o.ID_orden_compra
                    ), 0) as Costo_venta
                FROM Orden_compra o
                JOIN Proveedor p ON o.ID_proveedor = p.ID_proveedor
                WHERE o.Estado_orden_compra = 'Pendiente'
                GROUP BY o.ID_orden_compra, o.ID_proveedor, p.Nombre_proveedor, o.Fecha_orden_compra, o.Estado_orden_compra
                ORDER BY o.Fecha_orden_compra DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error listar_ordenes_pendientes: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            cursor.close()
            db.close()

    def listar_ordenes_entregadas(self):
        """Lista órdenes entregadas/completadas"""
        db = self._conexion()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    o.ID_orden_compra as ID_orden_c,
                    p.Nombre_proveedor as N_proveedor,
                    DATE(ei.Fecha_entrega_inventario) as Fecha_entrega,
                    ei.Recibido_por,
                    COALESCE((
                        SELECT SUM(d2.Cantidad_producto * COALESCE(s2.Costo_producto, 0))
                        FROM Detalle_orden d2
                        LEFT JOIN Suministra s2 ON d2.ID_producto = s2.ID_producto AND s2.ID_proveedor = o.ID_proveedor
                        WHERE d2.ID_orden_compra = o.ID_orden_compra
                    ), 0) as Costo_venta
                FROM Orden_compra o
                JOIN Proveedor p ON o.ID_proveedor = p.ID_proveedor
                JOIN Entrega_inventario ei ON o.ID_orden_compra = ei.ID_orden_compra
                WHERE o.Estado_orden_compra = 'Completada'
                GROUP BY o.ID_orden_compra, p.Nombre_proveedor, ei.Fecha_entrega_inventario, ei.Recibido_por
                ORDER BY ei.Fecha_entrega_inventario DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error listar_ordenes_entregadas: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def obtener_detalles_orden(self, id_orden: str):
        """Obtiene detalles completos de una orden"""
        db = self._conexion()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            # Datos de la orden
            cursor.execute("""
                SELECT 
                    o.ID_orden_compra as ID_orden_c,
                    o.ID_proveedor,
                    o.ID_empleado,
                    DATE(o.Fecha_orden_compra) as Fecha_o,
                    o.Estado_orden_compra as Estado
                FROM Orden_compra o
                WHERE o.ID_orden_compra = %s
            """, (id_orden,))
            datos_orden = cursor.fetchone()
            if not datos_orden:
                return None
            
            # Nombre del proveedor
            cursor.execute("""
                SELECT Nombre_proveedor as nombre
                FROM Proveedor
                WHERE ID_proveedor = %s
            """, (datos_orden["ID_proveedor"],))
            proveedor = cursor.fetchone()
            datos_orden["nombre"] = proveedor["nombre"] if proveedor else "Proveedor no encontrado"
            
            # Nombre del empleado
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
            
            # Total
            cursor.execute("""
                SELECT COALESCE(SUM(d.Cantidad_producto * COALESCE(s.Costo_producto, 0)), 0) as Costo_venta
                FROM Detalle_orden d
                LEFT JOIN Suministra s ON d.ID_producto = s.ID_producto AND s.ID_proveedor = %s
                WHERE d.ID_orden_compra = %s
            """, (datos_orden["ID_proveedor"], id_orden))
            total = cursor.fetchone()
            datos_orden["Costo_venta"] = float(total["Costo_venta"]) if total else 0
            
            # Productos de la orden - INCLUYE ID_producto
            cursor.execute("""
                SELECT 
                    d.ID_producto,
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
            """, (datos_orden.get("ID_proveedor"), id_orden))
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

    def obtener_productos_orden(self, id_orden: str):
        """Obtiene los productos de una orden para entrega"""
        db = self._conexion()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    d.ID_producto as ID_modelo,
                    p.Nombre_producto as N_modelo,
                    COALESCE(mp.Nombre_marca, 'Sin marca') as N_marca,
                    COALESCE(cp.Nombre_Clase, 'Sin clase') as N_clase,
                    d.Cantidad_producto as Cantidad_p,
                    COALESCE(s.Costo_producto, 0) as Costo,
                    (d.Cantidad_producto * COALESCE(s.Costo_producto, 0)) as sup_total
                FROM Detalle_orden d
                JOIN Producto p ON d.ID_producto = p.ID_producto
                LEFT JOIN Suministra s ON d.ID_producto = s.ID_producto
                LEFT JOIN Marca_producto mp ON p.ID_marca = mp.ID_marca
                LEFT JOIN Clase_producto cp ON p.ID_Clase = cp.ID_Clase
                WHERE d.ID_orden_compra = %s
            """, (id_orden,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error obtener_productos_orden: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def listar_proveedores(self):
        """Lista todos los proveedores"""
        db = self._conexion()
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
            print(f"Error listar_proveedores: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def listar_empleados(self):
        """Lista todos los empleados para el selector"""
        db = self._conexion()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    ID_empleado as id,
                    CONCAT(Nombre_empleado, ' ', Apellido_empleado) as nombre_completo,
                    Cedula_empleado as cedula,
                    Nombre_empleado as nombre,
                    Apellido_empleado as apellido
                FROM Empleado 
                WHERE ID_empleado IS NOT NULL
                ORDER BY Nombre_empleado ASC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error listar_empleados: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def obtener_productos_proveedor(self, id_proveedor: int):
        """Obtiene productos que suministra un proveedor"""
        if not id_proveedor:
            return []

        db = self._conexion()
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
            """, (id_proveedor,))
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
            return False

        db = self._conexion()
        if not db:
            return False

        cursor = None
        try:
            cursor = db.cursor()
            
            # Generar ID de orden
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
            
            for mid, qty in self.productos:
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

    def actualizar_orden_compra(self) -> bool:
        """Actualiza una orden de compra existente"""
        print(f"🔧 actualizar_orden_compra() iniciado para orden: {self.id_orden}")
        print(f"   Empleado: {self.id_empleado}, Proveedor: {self.id_proveedor}")
        print(f"   Productos: {self.productos}")
        
        if not self.id_orden:
            raise ValueError("ID de orden es requerido para actualizar")
        if not self.id_empleado or not self.id_proveedor or not self.productos:
            raise ValueError("Empleado, proveedor y productos son requeridos")

        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")

        cursor = None
        try:
            cursor = db.cursor()
            
            # Verificar que la orden existe y está pendiente
            cursor.execute(
                "SELECT ID_orden_compra, Estado_orden_compra FROM Orden_compra WHERE ID_orden_compra = %s",
                (self.id_orden,)
            )
            result = cursor.fetchone()
            print(f"📊 Resultado verificación: {result}")
            
            if not result:
                print(f"❌ Orden {self.id_orden} no encontrada")
                return False
            
            if result[1] != 'Pendiente':
                print(f"❌ La orden {self.id_orden} no está pendiente (estado: {result[1]})")
                return False

            # ✅ VALIDACIÓN: Verificar que todos los productos existan en la tabla Producto
            print("🔍 Verificando productos...")
            for mid, qty in self.productos:
                cursor.execute(
                    "SELECT ID_producto FROM Producto WHERE ID_producto = %s",
                    (str(mid),)
                )
                producto_existe = cursor.fetchone()
                if not producto_existe:
                    print(f"❌ Producto con ID '{mid}' no existe en la tabla Producto")
                    raise ValueError(f"El producto con ID '{mid}' no existe en el catálogo")
                print(f"✅ Producto {mid} existe")

            # Actualizar empleado y proveedor
            cursor.execute("""
                UPDATE Orden_compra 
                SET ID_empleado = %s, ID_proveedor = %s
                WHERE ID_orden_compra = %s
            """, (self.id_empleado, self.id_proveedor, self.id_orden))
            
            print(f"✅ UPDATE Orden_compra afectó {cursor.rowcount} filas")
            
            # Eliminar detalles antiguos
            cursor.execute(
                "DELETE FROM Detalle_orden WHERE ID_orden_compra = %s",
                (self.id_orden,)
            )
            print(f"✅ DELETE Detalle_orden afectó {cursor.rowcount} filas")
            
            # Insertar nuevos detalles
            for mid, qty in self.productos:
                cursor.execute("""
                    INSERT INTO Detalle_orden (ID_orden_compra, ID_producto, Cantidad_producto)
                    VALUES (%s, %s, %s)
                """, (self.id_orden, str(mid), qty))
                print(f"✅ INSERT Detalle_orden: producto={mid}, cantidad={qty}")
            
            db.commit()
            print("✅ Transacción completada exitosamente")
            
            # Registrar en bitácora
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Actualizar orden de compra",
                    descripcion=f"Se actualizó la orden de compra ID: {self.id_orden}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Órdenes de compra"
                )
                bitacora.registrar()
                print("✅ Bitácora registrada")
            
            return True
            
        except Exception as e:
            print(f"❌ Error actualizar_orden_compra: {e}")
            import traceback
            traceback.print_exc()
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

        db = self._conexion()
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