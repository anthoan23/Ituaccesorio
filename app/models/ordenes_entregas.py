from __future__ import annotations
from app.models.database import conectar
from app.models.bitacora import Bitacora
from datetime import datetime


class OrdenEntregaModel:
    """Modelo para Entregas / Recepción de Inventario"""
    
    def __init__(self, id_orden: str = None, recibido_por: str = None,
                 fecha_entrega: str = None, id_empleado: int = None,
                 usuario_id: str = None, id_entrega: str = None):
        self.id_orden = id_orden
        self.recibido_por = recibido_por
        self.fecha_entrega = fecha_entrega
        self.id_empleado = id_empleado
        self.usuario_id = usuario_id
        self.id_entrega = id_entrega
        self.__conexion_bd = conectar()
    
    def _conexion(self):
        return self.__conexion_bd.conexion1()
    
    def _generar_id_entrega(self) -> str:
        """Genera un ID único para la entrega"""
        db = self._conexion()
        if not db:
            return "ENT0000000"
        
        cursor = db.cursor()
        try:
            cursor.execute("SELECT MAX(ID_entrega_inventario) FROM Entrega_inventario")
            result = cursor.fetchone()
            last_id = result[0] if result and result[0] else "ENT0000000"
            last_num = int(last_id[3:]) if last_id and last_id.startswith("ENT") else 0
            return f"ENT{str(last_num + 1).zfill(7)}"
        finally:
            cursor.close()
            db.close()
    
    def listar_entregas(self):
        """Lista todas las entregas realizadas"""
        db = self._conexion()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    ei.ID_entrega_inventario as ID_entrega,
                    ei.ID_orden_compra as ID_orden_c,
                    DATE(ei.Fecha_entrega_inventario) as Fecha_entrega,
                    p.Nombre_proveedor as Proveedor,
                    CONCAT(e.Nombre_empleado, ' ', e.Apellido_empleado) as Recibido_por,
                    o.Estado_orden_compra as Estado_orden
                FROM Entrega_inventario ei
                JOIN Orden_compra o ON ei.ID_orden_compra = o.ID_orden_compra
                JOIN Proveedor p ON o.ID_proveedor = p.ID_proveedor
                JOIN Empleado e ON ei.ID_empleado = e.ID_empleado
                ORDER BY ei.Fecha_entrega_inventario DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error listar_entregas: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def obtener_entrega(self, id_entrega: str):
        """Obtiene los detalles de una entrega específica"""
        db = self._conexion()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    ei.ID_entrega_inventario as ID_entrega,
                    ei.ID_orden_compra as ID_orden_c,
                    DATE(ei.Fecha_entrega_inventario) as Fecha_entrega,
                    p.Nombre_proveedor as Proveedor,
                    CONCAT(e.Nombre_empleado, ' ', e.Apellido_empleado) as Recibido_por,
                    o.Estado_orden_compra as Estado_orden
                FROM Entrega_inventario ei
                JOIN Orden_compra o ON ei.ID_orden_compra = o.ID_orden_compra
                JOIN Proveedor p ON o.ID_proveedor = p.ID_proveedor
                JOIN Empleado e ON ei.ID_empleado = e.ID_empleado
                WHERE ei.ID_entrega_inventario = %s
            """, (id_entrega,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error obtener_entrega: {e}")
            return None
        finally:
            cursor.close()
            db.close()
    
    def registrar_entrega(self) -> bool:
        """
        Registra la entrega de una orden.
        Si el producto no existe en Existencias_productos, lo crea.
        Luego aumenta el stock.
        """
        if not self.id_orden:
            return False

        db = self._conexion()
        if not db:
            return False

        cursor = None
        try:
            cursor = db.cursor()
            
            # 1. Verificar si la orden existe y está pendiente
            cursor.execute("""
                SELECT ID_orden_compra, Estado_orden_compra, ID_proveedor 
                FROM Orden_compra 
                WHERE ID_orden_compra = %s
            """, (self.id_orden,))
            resultado = cursor.fetchone()
            
            if not resultado or resultado[1] != 'Pendiente':
                return False
            
            id_proveedor = resultado[2]
            
            # 2. Obtener los detalles de la orden con costo de suministra
            cursor.execute("""
                SELECT 
                    d.ID_producto,
                    d.Cantidad_producto,
                    s.Costo_producto
                FROM Detalle_orden d
                JOIN Suministra s ON d.ID_producto = s.ID_producto AND s.ID_proveedor = %s
                WHERE d.ID_orden_compra = %s
            """, (id_proveedor, self.id_orden))
            
            detalles = cursor.fetchall()
            if not detalles:
                return False
            
            # 3. Generar ID para la entrega
            id_entrega = self._generar_id_entrega()
            self.id_entrega = id_entrega
            
            # 4. Insertar en Entrega_inventario
            cursor.execute("""
                INSERT INTO Entrega_inventario (ID_entrega_inventario, ID_empleado, ID_orden_compra, Fecha_entrega_inventario)
                VALUES (%s, %s, %s, NOW())
            """, (id_entrega, self.id_empleado, self.id_orden))
            
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
                    """, (id_entrega, id_inventario, cantidad))
                    
                    # Actualizar stock
                    cursor.execute("""
                        UPDATE Existencias_productos 
                        SET Existencia = Existencia + %s
                        WHERE ID_inventario = %s
                    """, (cantidad, id_inventario))
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
                    
                    # Insertar en Abastece
                    cursor.execute("""
                        INSERT INTO Abastece (ID_entrega_inventario, ID_inventario, Cantidad_entregada)
                        VALUES (%s, %s, %s)
                    """, (id_entrega, new_inv_id, cantidad))
            
            # 6. Actualizar estado de la orden a Completada
            cursor.execute("""
                UPDATE Orden_compra 
                SET Estado_orden_compra = 'Completada'
                WHERE ID_orden_compra = %s
            """, (self.id_orden,))
            
            db.commit()
            
            # Registrar en bitácora
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Registrar entrega",
                    descripcion=f"Se registró entrega para orden: {self.id_orden} - Recibido por: {self.recibido_por}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Entregas"
                )
                bitacora.registrar()
            
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

    # ==================== NUEVOS MÉTODOS ====================

    def editar_entrega(self) -> bool:
        """Edita los datos de una entrega existente"""
        if not self.id_entrega:
            return False

        db = self._conexion()
        if not db:
            return False

        cursor = None
        try:
            cursor = db.cursor()
            
            # Verificar que la entrega existe
            cursor.execute("""
                SELECT ID_entrega_inventario FROM Entrega_inventario 
                WHERE ID_entrega_inventario = %s
            """, (self.id_entrega,))
            if not cursor.fetchone():
                return False
            
            # Actualizar fecha y recibido_por
            cursor.execute("""
                UPDATE Entrega_inventario 
                SET Fecha_entrega_inventario = %s
                WHERE ID_entrega_inventario = %s
            """, (self.fecha_entrega, self.id_entrega))
            
            # Nota: Recibido_por está en el modelo pero no en la tabla Entrega_inventario
            # Si quieres almacenarlo, necesitas agregar una columna o usar otra tabla
            
            db.commit()
            
            # Registrar en bitácora
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Editar entrega",
                    descripcion=f"Se editó la entrega ID: {self.id_entrega}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Entregas"
                )
                bitacora.registrar()
            
            return True
            
        except Exception as e:
            print(f"Error editar_entrega: {e}")
            if db:
                db.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def eliminar_entrega(self) -> bool:
        """
        Elimina (anula) una entrega.
        Revierta el stock de cada producto y cambia la orden a Pendiente.
        """
        if not self.id_entrega:
            return False

        db = self._conexion()
        if not db:
            return False

        cursor = None
        try:
            cursor = db.cursor()
            
            # 1. Verificar que la entrega existe
            cursor.execute("""
                SELECT ID_orden_compra FROM Entrega_inventario 
                WHERE ID_entrega_inventario = %s
            """, (self.id_entrega,))
            resultado = cursor.fetchone()
            if not resultado:
                return False
            
            id_orden = resultado[0]
            
            # 2. Obtener los productos entregados con sus cantidades
            cursor.execute("""
                SELECT a.ID_inventario, a.Cantidad_entregada
                FROM Abastece a
                WHERE a.ID_entrega_inventario = %s
            """, (self.id_entrega,))
            productos_entregados = cursor.fetchall()
            
            # 3. Revertir el stock de cada producto
            for inv_id, cantidad in productos_entregados:
                cursor.execute("""
                    UPDATE Existencias_productos 
                    SET Existencia = GREATEST(Existencia - %s, 0)
                    WHERE ID_inventario = %s
                """, (cantidad, inv_id))
            
            # 4. Eliminar registros de Abastece
            cursor.execute("""
                DELETE FROM Abastece 
                WHERE ID_entrega_inventario = %s
            """, (self.id_entrega,))
            
            # 5. Eliminar la entrega
            cursor.execute("""
                DELETE FROM Entrega_inventario 
                WHERE ID_entrega_inventario = %s
            """, (self.id_entrega,))
            
            # 6. Cambiar la orden a Pendiente
            cursor.execute("""
                UPDATE Orden_compra 
                SET Estado_orden_compra = 'Pendiente'
                WHERE ID_orden_compra = %s
            """, (id_orden,))
            
            db.commit()
            
            # Registrar en bitácora
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Eliminar entrega",
                    descripcion=f"Se eliminó la entrega ID: {self.id_entrega} - Orden: {id_orden}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Entregas"
                )
                bitacora.registrar()
            
            return True
            
        except Exception as e:
            print(f"Error eliminar_entrega: {e}")
            if db:
                db.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()