from __future__ import annotations
from app.models.database import conectar


class Proveedores:
    """Modelo para la tabla Proveedor"""
    
    def __init__(self, id_proveedor: int = 0, nombre: str = "", 
                 tipo: str = "", celular: str = "", correo: str = "", 
                 direccion: str = "", limite_credito: int = 0):
        self.id_proveedor = id_proveedor
        self.nombre = nombre
        self.tipo = tipo
        self.celular = celular
        self.correo = correo
        self.direccion = direccion
        self.limite_credito = limite_credito
        self.__conexion_bd = conectar()

    def _conexion(self):
        return self.__conexion_bd.conexion1()

    def _siguiente_id(self) -> int:
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute("SELECT COALESCE(MAX(ID_proveedor), 0) + 1 FROM Proveedor")
            row = cursor.fetchone()
            return int(row[0])
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def siguiente_id_proveedor(self) -> int:
        """Obtiene el siguiente ID disponible para un nuevo proveedor"""
        return self._siguiente_id()

    def listar_proveedores(self, q: str | None = None) -> list:
        """Lista todos los proveedores, opcionalmente filtrados por búsqueda"""
        db = self._conexion()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            where_sql = ""
            params = []
            if q:
                where_sql = "WHERE (Nombre_proveedor LIKE %s OR CAST(ID_proveedor AS CHAR) LIKE %s)"
                params = [f"%{q}%", f"%{q}%"]
            
            cursor.execute(f"""
                SELECT
                    ID_proveedor AS id,
                    Nombre_proveedor AS nombre,
                    Tipo_proveedor AS tipo,
                    Celular_proveedor AS celular,
                    Correo_proveedor AS correo,
                    Direccion_proveedor AS direccion,
                    Limite_credito AS limite_credito
                FROM Proveedor
                {where_sql}
                ORDER BY Nombre_proveedor ASC
            """, tuple(params))
            return cursor.fetchall() or []
        finally:
            cursor.close()
            db.close()

    def obtener_proveedor(self, id_proveedor: int = None) -> dict | None:
        """Obtiene un proveedor por su ID"""
        proveedor_id = id_proveedor if id_proveedor is not None else self.id_proveedor
        
        if proveedor_id == 0:
            return None
            
        db = self._conexion()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    ID_proveedor AS id,
                    Nombre_proveedor AS nombre,
                    Tipo_proveedor AS tipo,
                    Celular_proveedor AS celular,
                    Correo_proveedor AS correo,
                    Direccion_proveedor AS direccion,
                    Limite_credito AS limite_credito
                FROM Proveedor
                WHERE ID_proveedor = %s
                LIMIT 1
            """, (proveedor_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()

    def crear_proveedor(self) -> int:
        """Crea un nuevo proveedor usando los atributos de la instancia"""
        if not self.nombre:
            raise ValueError("El nombre del proveedor es obligatorio.")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = None
        try:
            cursor = db.cursor()
            
            # Si no tiene ID o es 0, obtener el siguiente
            if self.id_proveedor == 0:
                self.id_proveedor = self._siguiente_id()
            
            cursor.execute("""
                INSERT INTO Proveedor
                    (ID_proveedor, Nombre_proveedor, Tipo_proveedor, Celular_proveedor, 
                     Correo_proveedor, Direccion_proveedor, Limite_credito)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s)
            """, (self.id_proveedor, self.nombre, self.tipo or None, 
                  self.celular or None, self.correo or None, 
                  self.direccion or None, self.limite_credito or None))
            
            db.commit()
            return self.id_proveedor
        except Exception as e:
            if db:
                db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def actualizar_proveedor(self, id_proveedor: int = None) -> bool:
        """Actualiza un proveedor existente usando los atributos de la instancia"""
        proveedor_id = id_proveedor if id_proveedor is not None else self.id_proveedor
        
        if proveedor_id == 0:
            raise ValueError("ID del proveedor es requerido para actualizar.")
        if not self.nombre:
            raise ValueError("El nombre del proveedor es obligatorio.")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute("""
                UPDATE Proveedor
                SET
                    Nombre_proveedor = %s,
                    Tipo_proveedor = %s,
                    Celular_proveedor = %s,
                    Correo_proveedor = %s,
                    Direccion_proveedor = %s,
                    Limite_credito = %s
                WHERE ID_proveedor = %s
            """, (self.nombre, self.tipo or None, self.celular or None,
                  self.correo or None, self.direccion or None, 
                  self.limite_credito or None, proveedor_id))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            if db:
                db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def eliminar_proveedor(self, id_proveedor: int = None) -> bool:
        """Elimina un proveedor usando el ID de la instancia o el proporcionado"""
        proveedor_id = id_proveedor if id_proveedor is not None else self.id_proveedor
        
        if proveedor_id == 0:
            raise ValueError("ID del proveedor es requerido para eliminar.")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute("DELETE FROM Proveedor WHERE ID_proveedor = %s", (proveedor_id,))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            if db:
                db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def tiene_relaciones_activas(self, id_proveedor: int = None) -> tuple[bool, str]:
        """Verifica si el proveedor tiene relaciones activas en otros módulos"""
        proveedor_id = id_proveedor if id_proveedor is not None else self.id_proveedor
        
        if proveedor_id == 0:
            return True, "ID de proveedor no especificado"
        
        db = self._conexion()
        if not db:
            return True, "No se pudo conectar a la base de datos"
        
        cursor = db.cursor(dictionary=True)
        try:
            # Verificar órdenes de compra pendientes o completadas
            cursor.execute("""
                SELECT COUNT(*) as total FROM Orden_compra 
                WHERE ID_proveedor = %s 
                AND Estado_orden_compra IN ('Pendiente', 'Completada')
            """, (proveedor_id,))
            ordenes = cursor.fetchone()
            if ordenes and ordenes['total'] > 0:
                return True, f"No se puede eliminar el proveedor porque tiene {ordenes['total']} órdenes de compra asociadas."
            
            # Verificar productos suministrados
            cursor.execute("""
                SELECT COUNT(*) as total FROM Suministra 
                WHERE ID_proveedor = %s
            """, (proveedor_id,))
            suministros = cursor.fetchone()
            if suministros and suministros['total'] > 0:
                return True, f"No se puede eliminar el proveedor porque tiene {suministros['total']} productos asociados."
            
            return False, ""
        except Exception as e:
            print(f"Error verificando relaciones: {e}")
            return True, "Error al verificar relaciones del proveedor"
        finally:
            cursor.close()
            db.close()

    def obtener_detalle_relaciones(self, id_proveedor: int = None) -> dict:
        """Obtiene el detalle de las relaciones activas del proveedor"""
        proveedor_id = id_proveedor if id_proveedor is not None else self.id_proveedor
        
        if proveedor_id == 0:
            return {}
        
        db = self._conexion()
        if not db:
            return {}
        
        cursor = db.cursor(dictionary=True)
        try:
            # Obtener órdenes de compra
            cursor.execute("""
                SELECT ID_orden_compra as id, Estado_orden_compra as estado, DATE(Fecha_orden_compra) as fecha
                FROM Orden_compra 
                WHERE ID_proveedor = %s 
                AND Estado_orden_compra IN ('Pendiente', 'Completada')
            """, (proveedor_id,))
            ordenes = cursor.fetchall()
            
            # Obtener productos suministrados
            cursor.execute("""
                SELECT 
                    s.ID_producto as id_modelo,
                    p.Nombre_producto as nombre,
                    s.Costo_producto as costo
                FROM Suministra s
                JOIN Producto p ON s.ID_producto = p.ID_producto
                WHERE s.ID_proveedor = %s
            """, (proveedor_id,))
            productos = cursor.fetchall()
            
            return {
                "ordenes": ordenes or [],
                "productos": productos or []
            }
        except Exception as e:
            print(f"Error obteniendo detalle de relaciones: {e}")
            return {}
        finally:
            cursor.close()
            db.close()

    def listar_productos_por_proveedor(self, id_proveedor: int = None) -> list:
        """Lista los productos que suministra este proveedor"""
        proveedor_id = id_proveedor if id_proveedor is not None else self.id_proveedor
        
        if proveedor_id == 0:
            return []
        
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    s.ID_producto AS id_modelo,
                    p.Nombre_producto AS modelo_nombre,
                    ma.Nombre_marca AS marca_nombre,
                    cl.Nombre_Clase AS clase_nombre,
                    s.Costo_producto AS costo
                FROM Suministra s
                JOIN Producto p ON s.ID_producto = p.ID_producto
                JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                WHERE s.ID_proveedor = %s
                ORDER BY CAST(cl.ID_Clase AS UNSIGNED) ASC, 
                         CAST(ma.ID_marca AS UNSIGNED) ASC, 
                         p.Nombre_producto ASC
            """, (proveedor_id,))
            return cursor.fetchall() or []
        finally:
            cursor.close()
            db.close()

    def upsert_producto_proveedor(self, id_proveedor: int = None, id_modelo: str = None, costo: int | None = None) -> bool:
        """Inserta o actualiza un producto para este proveedor"""
        proveedor_id = id_proveedor if id_proveedor is not None else self.id_proveedor
        
        if proveedor_id == 0:
            raise ValueError("ID del proveedor es requerido")
        if not id_modelo:
            raise ValueError("ID del modelo es requerido")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO Suministra (ID_proveedor, ID_producto, Costo_producto)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE Costo_producto = VALUES(Costo_producto)
            """, (proveedor_id, id_modelo, costo))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            if db:
                db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def eliminar_producto_proveedor(self, id_proveedor: int = None, id_modelo: str = None) -> bool:
        """Elimina un producto de este proveedor"""
        proveedor_id = id_proveedor if id_proveedor is not None else self.id_proveedor
        
        if proveedor_id == 0:
            raise ValueError("ID del proveedor es requerido")
        if not id_modelo:
            raise ValueError("ID del modelo es requerido")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute(
                "DELETE FROM Suministra WHERE ID_proveedor = %s AND ID_producto = %s",
                (proveedor_id, id_modelo)
            )
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            if db:
                db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def crear_proveedor_con_productos(self, productos: list[dict]) -> int:
        """Crea un proveedor con sus productos iniciales en una transacción"""
        if not self.nombre:
            raise ValueError("El nombre del proveedor es obligatorio.")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = None
        try:
            cursor = db.cursor()
            
            # Si no tiene ID o es 0, obtener el siguiente
            if self.id_proveedor == 0:
                self.id_proveedor = self._siguiente_id()
            
            # Insertar proveedor
            cursor.execute("""
                INSERT INTO Proveedor
                    (ID_proveedor, Nombre_proveedor, Tipo_proveedor, Celular_proveedor, 
                     Correo_proveedor, Direccion_proveedor, Limite_credito)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s)
            """, (self.id_proveedor, self.nombre, self.tipo or None, 
                  self.celular or None, self.correo or None, 
                  self.direccion or None, self.limite_credito or None))
            
            # Insertar productos
            rows = []
            for item in (productos or []):
                id_modelo = item.get("id_modelo")
                costo = item.get("costo")
                rows.append((self.id_proveedor, str(id_modelo), 
                            costo if costo in (None, "") else int(costo)))
            
            if rows:
                cursor.executemany("""
                    INSERT INTO Suministra (ID_proveedor, ID_producto, Costo_producto)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE Costo_producto = VALUES(Costo_producto)
                """, rows)
            
            db.commit()
            return self.id_proveedor
        except Exception as e:
            if db:
                db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()