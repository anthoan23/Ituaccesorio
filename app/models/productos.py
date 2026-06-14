from __future__ import annotations
from app.models.database import conectar


class ClaseProducto:
    """Modelo para la tabla Clase_producto"""
    
    def __init__(self, id_clase: str = "", nombre: str = ""):
        self.id_clase = id_clase
        self.nombre = nombre
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
        """Verifica si una clase existe (usa el atributo id_clase)"""
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
        """Obtiene una clase por su ID (usa el atributo id_clase)"""
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
        """Registra una nueva clase usando los atributos de la instancia"""
        if not self.nombre:
            raise ValueError("El nombre de la clase es obligatorio.")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            new_id = self._siguiente_id()
            cursor.execute(
                "INSERT INTO Clase_producto (ID_Clase, Nombre_Clase) VALUES (%s, %s)",
                (new_id, self.nombre)
            )
            db.commit()
            self.id_clase = new_id
            return new_id
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    # def actualizar_clase(self) -> bool:
    #     """Actualiza una clase usando los atributos de la instancia"""
    #     if not self.id_clase or not self.nombre:
    #         raise ValueError("ID y nombre son requeridos.")
        
    #     db = self._conexion()
    #     if not db:
    #         raise RuntimeError("No se pudo conectar a la base de datos.")
        
    #     cursor = db.cursor()
    #     try:
    #         cursor.execute(
    #             "UPDATE Clase_producto SET Nombre_Clase = %s WHERE ID_Clase = %s",
    #             (self.nombre, self.id_clase)
    #         )
    #         db.commit()
    #         return cursor.rowcount > 0
    #     except Exception:
    #         db.rollback()
    #         raise
    #     finally:
    #         cursor.close()
    #         db.close()

    # def eliminar_clase(self) -> bool:
    #     """Elimina una clase usando el atributo id_clase"""
    #     if not self.id_clase:
    #         raise ValueError("ID es requerido.")
        
    #     db = self._conexion()
    #     if not db:
    #         raise RuntimeError("No se pudo conectar a la base de datos.")
        
    #     cursor = db.cursor()
    #     try:
    #         cursor.execute("DELETE FROM Clase_producto WHERE ID_Clase = %s", (self.id_clase,))
    #         db.commit()
    #         return cursor.rowcount > 0
    #     except Exception:
    #         db.rollback()
    #         raise
    #     finally:
    #         cursor.close()
    #         db.close()


class MarcaProducto:
    """Modelo para la tabla Marca_producto"""
    
    def __init__(self, id_marca: str = "", nombre: str = "", id_clase: str | None = None):
        self.id_marca = id_marca
        self.nombre = nombre
        self.id_clase = id_clase
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
        """Lista todas las marcas, opcionalmente filtradas por clase"""
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
        """Verifica si una marca existe (usa el atributo id_marca)"""
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
        """Obtiene una marca por su ID (usa el atributo id_marca)"""
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
        """Registra una nueva marca usando los atributos de la instancia"""
        if not self.nombre:
            raise ValueError("El nombre de la marca es obligatorio.")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            new_id = self._siguiente_id()
            cursor.execute(
                "INSERT INTO Marca_producto (ID_marca, Nombre_marca) VALUES (%s, %s)",
                (new_id, self.nombre)
            )
            db.commit()
            self.id_marca = new_id
            return new_id
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    # def actualizar_marca(self) -> bool:
    #     """Actualiza una marca usando los atributos de la instancia"""
    #     if not self.id_marca or not self.nombre:
    #         raise ValueError("ID y nombre son requeridos.")
        
    #     db = self._conexion()
    #     if not db:
    #         raise RuntimeError("No se pudo conectar a la base de datos.")
        
    #     cursor = db.cursor()
    #     try:
    #         cursor.execute(
    #             "UPDATE Marca_producto SET Nombre_marca = %s WHERE ID_marca = %s",
    #             (self.nombre, self.id_marca)
    #         )
    #         db.commit()
    #         return cursor.rowcount > 0
    #     except Exception:
    #         db.rollback()
    #         raise
    #     finally:
    #         cursor.close()
    #         db.close()

    # def eliminar_marca(self) -> bool:
    #     """Elimina una marca usando el atributo id_marca"""
    #     if not self.id_marca:
    #         raise ValueError("ID es requerido.")
        
    #     db = self._conexion()
    #     if not db:
    #         raise RuntimeError("No se pudo conectar a la base de datos.")
        
    #     cursor = db.cursor()
    #     try:
    #         cursor.execute("DELETE FROM Marca_producto WHERE ID_marca = %s", (self.id_marca,))
    #         db.commit()
    #         return cursor.rowcount > 0
    #     except Exception:
    #         db.rollback()
    #         raise
    #     finally:
    #         cursor.close()
    #         db.close()


class Producto:
    """Modelo para la tabla Producto"""
    
    def __init__(self, id_producto: str = "", id_clase: str = "", id_marca: str = "", 
                 nombre: str = "", descripcion: str | None = None):
        self.id_producto = id_producto
        self.id_clase = id_clase
        self.id_marca = id_marca
        self.nombre = nombre
        self.descripcion = descripcion
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
        """Lista todos los productos, opcionalmente filtrados"""
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
        """Verifica si un producto existe (usa el atributo id_producto)"""
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
        """Obtiene un producto por su ID (usa el atributo id_producto)"""
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

    def registrar_producto(self) -> str:
        """Registra un nuevo producto usando los atributos de la instancia"""
        if not self.id_clase or not self.id_marca or not self.nombre:
            raise ValueError("Clase, marca y nombre son obligatorios.")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            new_id = self._siguiente_id()
            cursor.execute("""
                INSERT INTO Producto (ID_producto, ID_Clase, ID_marca, Nombre_producto, Descripcion)
                VALUES (%s, %s, %s, %s, %s)
            """, (new_id, self.id_clase, self.id_marca, self.nombre, self.descripcion))
            db.commit()
            self.id_producto = new_id
            return new_id
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def actualizar_producto(self) -> bool:
        """Actualiza un producto usando los atributos de la instancia"""
        if not self.id_producto:
            raise ValueError("ID del producto es requerido para actualizar.")
        if not self.id_clase or not self.id_marca or not self.nombre:
            raise ValueError("Clase, marca y nombre son obligatorios.")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE Producto
                SET ID_Clase = %s, ID_marca = %s, Nombre_producto = %s, Descripcion = %s
                WHERE ID_producto = %s
            """, (self.id_clase, self.id_marca, self.nombre, self.descripcion, self.id_producto))
            db.commit()
            return cursor.rowcount > 0
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def eliminar_producto(self) -> bool:
        """Elimina un producto usando el atributo id_producto"""
        if not self.id_producto:
            raise ValueError("ID del producto es requerido para eliminar.")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
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
            return cursor.rowcount > 0
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def verificar_stock_asociado(self) -> bool:
        """Verifica si el producto tiene stock en inventario (usa el atributo id_producto)"""
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
        """Obtiene la cantidad de stock del producto (usa el atributo id_producto)"""
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
    """Capa de compatibilidad para controladores antiguos que usan el nombre Productos."""
    
    def listar_clases(self):
        return ClaseProducto().listar_clases()
    
    def listar_marcas(self, id_clase: str | None = None):
        return MarcaProducto().listar_marcas(id_clase=id_clase)
    
    def listar_modelos(self, id_marca: str | None = None, id_clase: str | None = None, q: str | None = None):
        return Producto().listar_productos(id_marca=id_marca, id_clase=id_clase, q=q)