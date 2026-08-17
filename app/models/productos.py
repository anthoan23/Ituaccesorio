from __future__ import annotations
from app.models.database import conectar
from decimal import Decimal
from app.models.bitacora import Bitacora
import mysql.connector


class Categoria:
    """Modelo para la tabla Categoria"""
    
    def __init__(self, id_categoria: int = 0, nombre: str = ""):
        self.id_categoria = id_categoria
        self.nombre = nombre
        self.__conexion_bd = conectar()

    def _conexion(self):
        return self.__conexion_bd.conexion1()

    def listar_categorias(self):
        """Lista todas las categorías"""
        db = self._conexion()
        if not db:
            return []
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT ID_categoria AS id, Nombre_categoria AS nombre
                FROM Categoria
                ORDER BY Nombre_categoria ASC
            """)
            return cursor.fetchall() or []
        finally:
            cursor.close()
            db.close()

    def obtener_categoria(self) -> dict | None:
        """Obtiene una categoría por su ID"""
        if not self.id_categoria:
            return None
        db = self._conexion()
        if not db:
            return None
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT ID_categoria AS id, Nombre_categoria AS nombre
                FROM Categoria
                WHERE ID_categoria = %s
            """, (self.id_categoria,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()


class ClaseProducto:
    """Modelo para la tabla Clase_producto"""
    
    def __init__(self, id_clase: str = "", nombre: str = "", usuario_id: str = None):
        self.id_clase = id_clase
        self.nombre = nombre
        self.usuario_id = usuario_id
        self.__conexion_bd = conectar()

    def _conexion(self):
        return self.__conexion_bd.conexion1()

    def _siguiente_id(self) -> str:
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        cursor = db.cursor()
        try:
            cursor.execute("SELECT COALESCE(MAX(CAST(ID_Clase AS UNSIGNED)), 0) + 1 FROM Clase_producto")
            row = cursor.fetchone()
            return str(int(row[0] or 0))
        finally:
            cursor.close()
            db.close()

    def listar_clases(self):
        """Lista todas las clases"""
        db = self._conexion()
        if not db:
            return []
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT ID_Clase AS id, Nombre_Clase AS nombre
                FROM Clase_producto
                ORDER BY CAST(ID_Clase AS UNSIGNED) ASC
            """)
            return cursor.fetchall() or []
        finally:
            cursor.close()
            db.close()

    def verificar_clase(self) -> bool:
        if not self.id_clase:
            return False
        db = self._conexion()
        if not db:
            return False
        cursor = db.cursor()
        try:
            cursor.execute("SELECT 1 FROM Clase_producto WHERE ID_Clase = %s LIMIT 1", (self.id_clase,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    def obtener_clase(self) -> dict | None:
        if not self.id_clase:
            return None
        db = self._conexion()
        if not db:
            return None
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT ID_Clase AS id, Nombre_Clase AS nombre
                FROM Clase_producto
                WHERE ID_Clase = %s
            """, (self.id_clase,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()

    def registrar_clase(self) -> str:
        if not self.nombre:
            raise ValueError("El nombre de la clase es obligatorio.")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            # Validación: Verificar si ya existe una clase con el mismo nombre
            cursor.execute(
                "SELECT 1 FROM Clase_producto WHERE Nombre_Clase = %s LIMIT 1",
                (self.nombre,)
            )
            if cursor.fetchone():
                raise ValueError(f"Ya existe una clase con el nombre '{self.nombre}'.")
            
            new_id = self._siguiente_id()
            cursor.execute(
                "INSERT INTO Clase_producto (ID_Clase, Nombre_Clase) VALUES (%s, %s)",
                (new_id, self.nombre)
            )
            db.commit()
            self.id_clase = new_id
            
            # Registrar en bitácora
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Crear clase",
                    descripcion=f"Clase creada: {self.nombre} (ID: {new_id})",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Productos"
                )
                bitacora.registrar()
            
            return new_id
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()


class MarcaProducto:
    """Modelo para la tabla Marca_producto"""
    
    def __init__(self, id_marca: str = "", nombre: str = "", id_clase: str | None = None, usuario_id: str = None):
        self.id_marca = id_marca
        self.nombre = nombre
        self.id_clase = id_clase
        self.usuario_id = usuario_id
        self.__conexion_bd = conectar()

    def _conexion(self):
        return self.__conexion_bd.conexion1()

    def _siguiente_id(self) -> str:
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        cursor = db.cursor()
        try:
            cursor.execute("SELECT COALESCE(MAX(CAST(ID_marca AS UNSIGNED)), 0) + 1 FROM Marca_producto")
            row = cursor.fetchone()
            return str(int(row[0] or 0))
        finally:
            cursor.close()
            db.close()

    def listar_marcas(self, id_clase: str | None = None):
        db = self._conexion()
        if not db:
            return []
        cursor = db.cursor(dictionary=True)
        try:
            filtro_clase = id_clase or self.id_clase
            if filtro_clase:
                cursor.execute("""
                    SELECT DISTINCT ma.ID_marca AS id, ma.Nombre_marca AS nombre
                    FROM Marca_producto ma
                    JOIN Producto p ON p.ID_marca = ma.ID_marca
                    WHERE p.ID_Clase = %s
                    ORDER BY CAST(ma.ID_marca AS UNSIGNED) ASC
                """, (filtro_clase,))
            else:
                cursor.execute("""
                    SELECT ID_marca AS id, Nombre_marca AS nombre
                    FROM Marca_producto
                    ORDER BY CAST(ID_marca AS UNSIGNED) ASC
                """)
            return cursor.fetchall() or []
        finally:
            cursor.close()
            db.close()

    def verificar_marca(self) -> bool:
        if not self.id_marca:
            return False
        db = self._conexion()
        if not db:
            return False
        cursor = db.cursor()
        try:
            cursor.execute("SELECT 1 FROM Marca_producto WHERE ID_marca = %s LIMIT 1", (self.id_marca,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    def obtener_marca(self) -> dict | None:
        if not self.id_marca:
            return None
        db = self._conexion()
        if not db:
            return None
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT ID_marca AS id, Nombre_marca AS nombre
                FROM Marca_producto
                WHERE ID_marca = %s
            """, (self.id_marca,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()

    def registrar_marca(self) -> str:
        if not self.nombre:
            raise ValueError("El nombre de la marca es obligatorio.")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            # Validación: Verificar si ya existe una marca con el mismo nombre
            cursor.execute(
                "SELECT 1 FROM Marca_producto WHERE Nombre_marca = %s LIMIT 1",
                (self.nombre,)
            )
            if cursor.fetchone():
                raise ValueError(f"Ya existe una marca con el nombre '{self.nombre}'.")
            
            new_id = self._siguiente_id()
            cursor.execute(
                "INSERT INTO Marca_producto (ID_marca, Nombre_marca) VALUES (%s, %s)",
                (new_id, self.nombre)
            )
            db.commit()
            self.id_marca = new_id
            
            # Registrar en bitácora
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Crear marca",
                    descripcion=f"Marca creada: {self.nombre} (ID: {new_id})",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Productos"
                )
                bitacora.registrar()
            
            return new_id
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()


class Producto:
    """Modelo para la tabla Producto"""
    
    def __init__(self, id_producto: str = "", id_clase: str = "", id_marca: str = "", 
                 nombre: str = "", descripcion: str | None = None, id_categoria: int = 0,
                 usuario_id: str = None):
        self.id_producto = id_producto
        self.id_clase = id_clase
        self.id_marca = id_marca
        self.nombre = nombre
        self.descripcion = descripcion
        self.id_categoria = id_categoria
        self.usuario_id = usuario_id
        self.__conexion_bd = conectar()

    def _conexion(self):
        return self.__conexion_bd.conexion1()

    def _siguiente_id(self) -> str:
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        cursor = db.cursor()
        try:
            cursor.execute("SELECT COALESCE(MAX(CAST(ID_producto AS UNSIGNED)), 0) + 1 FROM Producto")
            row = cursor.fetchone()
            return str(int(row[0] or 0))
        finally:
            cursor.close()
            db.close()

    def listar_productos(self, id_marca: str | None = None, id_clase: str | None = None, q: str | None = None):
        db = self._conexion()
        if not db:
            return []
        cursor = db.cursor(dictionary=True)
        try:
            where = []
            params = []
            if id_marca or self.id_marca:
                where.append("p.ID_marca = %s")
                params.append(id_marca or self.id_marca)
            if id_clase or self.id_clase:
                where.append("p.ID_Clase = %s")
                params.append(id_clase or self.id_clase)
            if q:
                where.append("p.Nombre_producto LIKE %s")
                params.append(f"%{q}%")

            where_sql = f"WHERE {' AND '.join(where)}" if where else ""

            cursor.execute(f"""
                SELECT
                    p.ID_producto AS id,
                    p.ID_marca AS id_marca,
                    p.ID_Clase AS id_clase,
                    p.Nombre_producto AS nombre,
                    p.Descripcion AS descripcion,
                    ma.Nombre_marca AS marca_nombre,
                    cl.Nombre_Clase AS clase_nombre
                FROM Producto p
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                {where_sql}
                ORDER BY CAST(cl.ID_Clase AS UNSIGNED) ASC, CAST(ma.ID_marca AS UNSIGNED) ASC, p.Nombre_producto ASC
            """, tuple(params))
            return cursor.fetchall() or []
        finally:
            cursor.close()
            db.close()

    def verificar_producto(self) -> bool:
        if not self.id_producto:
            return False
        db = self._conexion()
        if not db:
            return False
        cursor = db.cursor()
        try:
            cursor.execute("SELECT 1 FROM Producto WHERE ID_producto = %s LIMIT 1", (self.id_producto,))
            return cursor.fetchone() is not None        
        finally:
            cursor.close()
            db.close()

    def obtener_producto(self):
        if not self.id_producto:
            return None
        db = self._conexion()
        if not db:
            return None
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    p.ID_producto AS id,
                    p.ID_marca AS id_marca,
                    p.ID_Clase AS id_clase,
                    p.Nombre_producto AS nombre,
                    p.Descripcion AS descripcion,
                    ma.Nombre_marca AS marca_nombre,
                    cl.Nombre_Clase AS clase_nombre
                FROM Producto p
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                WHERE p.ID_producto = %s
                LIMIT 1
            """, (self.id_producto,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()

    # ==================== MÉTODO CON STORED PROCEDURE ====================
    
    def verificar_stock_procedure(self) -> dict:
        """
        Usa el stored procedure sp_verificar_stock_producto
        para verificar el stock de un producto
        """
        if not self.id_producto:
            return {"stock_total": 0, "tiene_stock": False, "detalle": [], "success": False, "error": "ID de producto no especificado"}
        
        db = self._conexion()
        if not db:
            return {"stock_total": 0, "tiene_stock": False, "detalle": [], "success": False, "error": "No se pudo conectar a la BD"}
        
        cursor = None
        try:
            cursor = db.cursor(dictionary=True)
            
            # Ejecutar el procedure con parámetros de salida
            # Los parámetros OUT se pasan como valores dummy (0, False)
            cursor.callproc('sp_verificar_stock_producto', (self.id_producto, 0, False))
            
            # Obtener los parámetros de salida
            # MySQL guarda los OUT params como @_nombre_procedure_0, @_nombre_procedure_1, etc.
            cursor.execute("SELECT @_sp_verificar_stock_producto_1 AS stock_total, @_sp_verificar_stock_producto_2 AS tiene_stock")
            out_params = cursor.fetchone()
            
            stock_total = out_params['stock_total'] if out_params else 0
            tiene_stock = bool(out_params['tiene_stock']) if out_params else False
            
            # Obtener el detalle (el SELECT que devuelve)
            detalle = []
            for result in cursor.stored_results():
                rows = result.fetchall()
                if rows:
                    detalle = rows
            
            return {
                "stock_total": stock_total,
                "tiene_stock": tiene_stock,
                "detalle": detalle,
                "success": True
            }
            
        except mysql.connector.Error as e:
            print(f"Error en procedure: {e}")
            return {
                "stock_total": 0,
                "tiene_stock": False,
                "detalle": [],
                "error": str(e),
                "success": False
            }
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    # ==================== FIN MÉTODO CON STORED PROCEDURE ====================

    def registrar_producto(self) -> str:
        if not self.id_clase or not self.id_marca or not self.nombre:
            raise ValueError("Clase, marca y nombre son obligatorios.")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            # Validación: Verificar que la clase exista
            cursor.execute(
                "SELECT 1 FROM Clase_producto WHERE ID_Clase = %s LIMIT 1",
                (self.id_clase,)
            )
            if not cursor.fetchone():
                raise ValueError(f"La clase con ID '{self.id_clase}' no existe.")
            
            # Validación: Verificar que la marca exista
            cursor.execute(
                "SELECT 1 FROM Marca_producto WHERE ID_marca = %s LIMIT 1",
                (self.id_marca,)
            )
            if not cursor.fetchone():
                raise ValueError(f"La marca con ID '{self.id_marca}' no existe.")
            
            # Validación: Verificar si ya existe un producto con el mismo nombre, clase y marca
            cursor.execute("""
                SELECT 1 FROM Producto 
                WHERE Nombre_producto = %s AND ID_Clase = %s AND ID_marca = %s
                LIMIT 1
            """, (self.nombre, self.id_clase, self.id_marca))
            if cursor.fetchone():
                raise ValueError(f"Ya existe un producto con el nombre '{self.nombre}' en esta clase y marca.")
            
            new_id = self._siguiente_id()
            cursor.execute("""
                INSERT INTO Producto (ID_producto, ID_Clase, ID_marca, Nombre_producto, Descripcion)
                VALUES (%s, %s, %s, %s, %s)
            """, (new_id, self.id_clase, self.id_marca, self.nombre, self.descripcion))
            db.commit()
            self.id_producto = new_id
            
            # Registrar en bitácora
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Crear producto",
                    descripcion=f"Producto creado: {self.nombre} (ID: {new_id})",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Productos"
                )
                bitacora.registrar()
            
            return new_id
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def actualizar_producto(self) -> bool:
        if not self.id_producto:
            raise ValueError("ID del producto es requerido para actualizar.")
        if not self.id_clase or not self.id_marca or not self.nombre:
            raise ValueError("Clase, marca y nombre son obligatorios.")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            # Validación: Verificar que el producto exista
            cursor.execute(
                "SELECT 1 FROM Producto WHERE ID_producto = %s LIMIT 1",
                (self.id_producto,)
            )
            if not cursor.fetchone():
                raise ValueError(f"El producto con ID '{self.id_producto}' no existe.")
            
            # Validación: Verificar que la clase exista
            cursor.execute(
                "SELECT 1 FROM Clase_producto WHERE ID_Clase = %s LIMIT 1",
                (self.id_clase,)
            )
            if not cursor.fetchone():
                raise ValueError(f"La clase con ID '{self.id_clase}' no existe.")
            
            # Validación: Verificar que la marca exista
            cursor.execute(
                "SELECT 1 FROM Marca_producto WHERE ID_marca = %s LIMIT 1",
                (self.id_marca,)
            )
            if not cursor.fetchone():
                raise ValueError(f"La marca con ID '{self.id_marca}' no existe.")
            
            # Validación: Verificar nombre duplicado (excluyendo el producto actual)
            cursor.execute("""
                SELECT 1 FROM Producto 
                WHERE Nombre_producto = %s AND ID_Clase = %s AND ID_marca = %s 
                AND ID_producto != %s
                LIMIT 1
            """, (self.nombre, self.id_clase, self.id_marca, self.id_producto))
            if cursor.fetchone():
                raise ValueError(f"Ya existe otro producto con el nombre '{self.nombre}' en esta clase y marca.")
            
            cursor.execute("""
                UPDATE Producto
                SET ID_Clase = %s, ID_marca = %s, Nombre_producto = %s, Descripcion = %s
                WHERE ID_producto = %s
            """, (self.id_clase, self.id_marca, self.nombre, self.descripcion, self.id_producto))
            db.commit()
            updated = cursor.rowcount > 0
            
            # Registrar en bitácora
            if updated and self.usuario_id:
                bitacora = Bitacora(
                    accion="Actualizar producto",
                    descripcion=f"Producto actualizado: {self.nombre} (ID: {self.id_producto})",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Productos"
                )
                bitacora.registrar()
            
            return updated
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def eliminar_producto(self) -> bool:
        if not self.id_producto:
            raise ValueError("ID del producto es requerido para eliminar.")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            # Validación: Verificar que el producto exista
            cursor.execute(
                "SELECT 1 FROM Producto WHERE ID_producto = %s LIMIT 1",
                (self.id_producto,)
            )
            if not cursor.fetchone():
                raise ValueError(f"El producto con ID '{self.id_producto}' no existe.")
            
            # Primero eliminar fotos del inventario
            cursor.execute("""
                DELETE fi FROM Fotos_inventario fi
                JOIN Existencias_productos e ON fi.ID_inventario = e.ID_inventario
                WHERE e.ID_producto = %s
            """, (self.id_producto,))
            
            # Eliminar existencias (inventario)
            cursor.execute("DELETE FROM Existencias_productos WHERE ID_producto = %s", (self.id_producto,))
            
            # Eliminar suministra
            cursor.execute("DELETE FROM Suministra WHERE ID_producto = %s", (self.id_producto,))
            
            # Eliminar producto
            cursor.execute("DELETE FROM Producto WHERE ID_producto = %s", (self.id_producto,))
            
            db.commit()
            deleted = cursor.rowcount > 0
            
            # Registrar en bitácora
            if deleted and self.usuario_id:
                bitacora = Bitacora(
                    accion="Eliminar producto",
                    descripcion=f"Producto eliminado (ID: {self.id_producto})",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Productos"
                )
                bitacora.registrar()
            
            return deleted
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def verificar_stock_asociado(self) -> bool:
        if not self.id_producto:
            return False
        
        db = self._conexion()
        if not db:
            return False
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM Existencias_productos 
                WHERE ID_producto = %s AND Existencia > 0
            """, (self.id_producto,))
            result = cursor.fetchone()
            return result[0] > 0 if result else False
        finally:
            cursor.close()
            db.close()

    def obtener_stock_producto(self) -> int:
        if not self.id_producto:
            return 0
        
        db = self._conexion()
        if not db:
            return 0
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT COALESCE(SUM(Existencia), 0) FROM Existencias_productos 
                WHERE ID_producto = %s
            """, (self.id_producto,))
            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            cursor.close()
            db.close()


class Productos(conectar):
    """Capa de compatibilidad para controladores antiguos"""
    
    def listar_clases(self):
        return ClaseProducto().listar_clases()
    
    def listar_marcas(self, id_clase: str | None = None):
        return MarcaProducto().listar_marcas(id_clase=id_clase)
    
    def listar_modelos(self, id_marca: str | None = None, id_clase: str | None = None, q: str | None = None):
        return Producto().listar_productos(id_marca=id_marca, id_clase=id_clase, q=q)
    
    def listar_categorias(self):
        return Categoria().listar_categorias()