from __future__ import annotations
from decimal import Decimal
from app.models.database import conectar


class Inventario:
    """Modelo para la tabla Existencias_productos"""
    
    def __init__(self, id_inventario: str = "", id_producto: str = "", 
                 existencia: int = 0, costo_venta: Decimal = Decimal(0), 
                 usuario_id: str = None):
        self.id_inventario = id_inventario
        self.id_producto = id_producto
        self.existencia = existencia
        self.costo_venta = costo_venta
        self.usuario_id = usuario_id  # Usuario que realiza la acción
        self.__conexion_bd = conectar()

    def _conexion(self):
        return self.__conexion_bd.conexion1()

    def _siguiente_id(self) -> str:
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute("SELECT COALESCE(MAX(CAST(ID_inventario AS UNSIGNED)), 0) + 1 FROM Existencias_productos")
            row = cursor.fetchone()
            return str(int(row[0] or 0))
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    # ==================== MÉTODOS DE LISTADO ====================

    def listar_inventario(self):
        """Lista todo el inventario con sus relaciones"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    e.ID_inventario AS id_inventario,
                    e.ID_producto AS id_producto,
                    e.Existencia AS existencia,
                    e.Costo_venta AS costo_venta,
                    p.Nombre_producto AS nombre_producto,
                    ma.Nombre_marca AS nombre_marca,
                    cl.Nombre_Clase AS nombre_clase,
                    (SELECT fi.Foto_inventario FROM Fotos_inventario fi 
                     WHERE fi.ID_inventario = e.ID_inventario 
                     ORDER BY fi.ID_foto_inventario DESC LIMIT 1) AS foto_inventario
                FROM Existencias_productos e
                JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                ORDER BY cl.Nombre_Clase, ma.Nombre_marca, p.Nombre_producto
            """)
            rows = cursor.fetchall() or []
            for row in rows:
                if isinstance(row.get("costo_venta"), Decimal):
                    row["costo_venta"] = float(row["costo_venta"])
            return rows
        finally:
            cursor.close()
            db.close()

    def listar_inventario_por_modelo(self, nombre_modelo: str = None):
        """Lista inventario filtrado por modelo (usa el atributo o parámetro)"""
        modelo_buscar = nombre_modelo if nombre_modelo is not None else self.nombre_modelo if hasattr(self, 'nombre_modelo') else None
        
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            if modelo_buscar:
                cursor.execute("""
                    SELECT 
                        e.ID_inventario AS id_inventario,
                        e.ID_producto AS id_producto,
                        e.Existencia AS existencia,
                        e.Costo_venta AS costo_venta,
                        p.Nombre_producto AS nombre_producto,
                        ma.Nombre_marca AS nombre_marca,
                        cl.Nombre_Clase AS nombre_clase,
                        (SELECT fi.Foto_inventario FROM Fotos_inventario fi 
                         WHERE fi.ID_inventario = e.ID_inventario 
                         ORDER BY fi.ID_foto_inventario DESC LIMIT 1) AS foto_inventario
                    FROM Existencias_productos e
                    JOIN Producto p ON e.ID_producto = p.ID_producto
                    LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                    LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                    WHERE p.Nombre_producto LIKE %s
                    ORDER BY cl.Nombre_Clase, ma.Nombre_marca, p.Nombre_producto
                """, (f"%{modelo_buscar}%",))
            else:
                return self.listar_inventario()
            
            rows = cursor.fetchall() or []
            for row in rows:
                if isinstance(row.get("costo_venta"), Decimal):
                    row["costo_venta"] = float(row["costo_venta"])
            return rows
        finally:
            cursor.close()
            db.close()

    def listar_inventario_general(self):
        """Lista inventario general (sin filtros)"""
        return self.listar_inventario()

    def listar_inventario_taller(self):
        """Lista inventario específico para taller"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    e.ID_inventario,
                    p.Nombre_producto,
                    m.Nombre_marca,
                    c.Nombre_Clase,
                    e.Existencia,
                    e.Costo_venta 
                FROM Existencias_productos e
                JOIN Producto p ON e.ID_producto = p.ID_producto
                JOIN Clase_producto c ON p.ID_Clase = c.ID_Clase
                JOIN Marca_producto m ON p.ID_marca = m.ID_marca
                WHERE e.ID_categoria = 2
                ORDER BY c.Nombre_Clase, m.Nombre_marca, p.Nombre_producto
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def listar_productos_bajo_stock(self, limite: int = 10):
        """Obtiene productos con stock menor o igual al límite (excluyendo 0)"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    e.ID_inventario AS id_inventario,
                    e.ID_producto AS id_producto,
                    e.Existencia AS existencia,
                    e.Costo_venta AS costo_venta,
                    p.Nombre_producto AS nombre_producto,
                    ma.Nombre_marca AS nombre_marca,
                    cl.Nombre_Clase AS nombre_clase,
                    (SELECT fi.Foto_inventario FROM Fotos_inventario fi 
                     WHERE fi.ID_inventario = e.ID_inventario 
                     ORDER BY fi.ID_foto_inventario DESC LIMIT 1) AS foto_inventario
                FROM Existencias_productos e
                JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                WHERE e.Existencia <= %s AND e.Existencia > 0
                ORDER BY e.Existencia ASC
                LIMIT %s
            """, (limite, limite))
            rows = cursor.fetchall() or []
            for row in rows:
                if isinstance(row.get("costo_venta"), Decimal):
                    row["costo_venta"] = float(row["costo_venta"])
            return rows
        finally:
            cursor.close()
            db.close()

    def listar_productos_sin_stock(self):
        """Obtiene productos con stock igual a 0"""
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    e.ID_inventario AS id_inventario,
                    e.ID_producto AS id_producto,
                    e.Existencia AS existencia,
                    e.Costo_venta AS costo_venta,
                    p.Nombre_producto AS nombre_producto,
                    ma.Nombre_marca AS nombre_marca,
                    cl.Nombre_Clase AS nombre_clase,
                    (SELECT fi.Foto_inventario FROM Fotos_inventario fi 
                     WHERE fi.ID_inventario = e.ID_inventario 
                     ORDER BY fi.ID_foto_inventario DESC LIMIT 1) AS foto_inventario
                FROM Existencias_productos e
                JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                WHERE e.Existencia = 0
                ORDER BY p.Nombre_producto ASC
                LIMIT 10
            """)
            rows = cursor.fetchall() or []
            for row in rows:
                if isinstance(row.get("costo_venta"), Decimal):
                    row["costo_venta"] = float(row["costo_venta"])
            return rows
        finally:
            cursor.close()
            db.close()

    # ==================== MÉTODOS DE CONSULTA ====================

    def verificar_existencia(self) -> bool:
        """Verifica si un registro de inventario existe (usa el atributo id_inventario)"""
        if not self.id_inventario:
            return False
        db = self._conexion()
        if not db:
            return False
        cursor = db.cursor()
        try:
            cursor.execute("SELECT 1 FROM Existencias_productos WHERE ID_inventario = %s LIMIT 1", (self.id_inventario,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    def obtener_inventario(self) -> dict | None:
        """Obtiene un registro de inventario por su ID (usa el atributo id_inventario)"""
        if not self.id_inventario:
            return None
        db = self._conexion()
        if not db:
            return None
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    e.ID_inventario AS id_inventario,
                    e.ID_producto AS id_producto,
                    e.Existencia AS existencia,
                    e.Costo_venta AS costo_venta,
                    p.Nombre_producto AS nombre_producto,
                    ma.Nombre_marca AS nombre_marca,
                    cl.Nombre_Clase AS nombre_clase
                FROM Existencias_productos e
                JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                WHERE e.ID_inventario = %s
            """, (self.id_inventario,))
            row = cursor.fetchone()
            if row and isinstance(row.get("costo_venta"), Decimal):
                row["costo_venta"] = float(row["costo_venta"])
            return row
        finally:
            cursor.close()
            db.close()

    def obtener_producto_info(self) -> dict | None:
        """Obtiene información del producto asociado (usa el atributo id_producto)"""
        if not self.id_producto:
            return None
        db = self._conexion()
        if not db:
            return None
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    p.ID_producto as id,
                    p.Nombre_producto as nombre_producto,
                    p.Descripcion as descripcion,
                    cl.Nombre_Clase as nombre_clase,
                    ma.Nombre_marca as nombre_marca
                FROM Producto p
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                WHERE p.ID_producto = %s
            """, (self.id_producto,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()

    # ==================== MÉTODOS DE OPERACIÓN ====================

    def registrar_stock(self) -> str:
        """Registra o actualiza stock usando los atributos de la instancia"""
        if not self.id_producto:
            raise ValueError("ID del producto es requerido")
        
        if self.existencia < 0:
            raise ValueError("La existencia no puede ser negativa")
        
        if self.costo_venta < 0:
            raise ValueError("El costo de venta no puede ser negativo")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = None
        try:
            cursor = db.cursor()
            
            cursor.execute(
                "SELECT ID_inventario FROM Existencias_productos WHERE ID_producto = %s LIMIT 1",
                (str(self.id_producto),)
            )
            row = cursor.fetchone()
            
            es_nuevo = False
            if row:
                # Actualizar existente
                self.id_inventario = str(row[0])
                cursor.execute(
                    "UPDATE Existencias_productos SET Existencia = %s, Costo_venta = %s WHERE ID_inventario = %s",
                    (int(self.existencia), self.costo_venta, self.id_inventario)
                )
                accion = "Actualizar stock"
                descripcion = f"Se actualizó stock del producto: {nombre_producto or id_producto} - Nueva existencia: {existencia} - Costo: {costo_venta}"
            else:
                # Crear nuevo
                self.id_inventario = self._siguiente_id()
                cursor.execute("""
                    INSERT INTO Existencias_productos (ID_inventario, ID_producto, Existencia, Costo_venta)
                    VALUES (%s, %s, %s, %s)
                """, (self.id_inventario, str(self.id_producto), int(self.existencia), self.costo_venta))
            
            db.commit()
            return self.id_inventario
        except Exception as e:
            if db:
                db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def actualizar_stock(self) -> bool:
        """Actualiza stock usando los atributos de la instancia"""
        if not self.id_inventario:
            raise ValueError("ID del inventario es requerido para actualizar")
        
        if self.existencia < 0:
            raise ValueError("La existencia no puede ser negativa")
        
        if self.costo_venta < 0:
            raise ValueError("El costo de venta no puede ser negativo")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute("""
                UPDATE Existencias_productos 
                SET Existencia = %s, Costo_venta = %s
                WHERE ID_inventario = %s
            """, (int(self.existencia), self.costo_venta, self.id_inventario))
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

    def eliminar_stock(self) -> bool:
        """Elimina un registro de inventario usando el atributo id_inventario"""
        if not self.id_inventario:
            raise ValueError("ID del inventario es requerido para eliminar")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute("DELETE FROM Existencias_productos WHERE ID_inventario = %s", (self.id_inventario,))
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


class FotosInventario:
    """Modelo para la tabla Fotos_inventario"""
    
    def __init__(self, id_foto_inventario: str = "", id_inventario: str = "", 
                 foto_inventario: str = "", usuario_id: str = None):
        self.id_foto_inventario = id_foto_inventario
        self.id_inventario = id_inventario
        self.foto_inventario = foto_inventario
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
            cursor.execute("SELECT COALESCE(MAX(CAST(ID_foto_inventario AS UNSIGNED)), 0) + 1 FROM Fotos_inventario")
            row = cursor.fetchone()
            return str(int(row[0] or 0))
        finally:
            cursor.close()
            db.close()

    # ==================== MÉTODOS DE LISTADO ====================

    def listar_fotos(self):
        """Lista todas las fotos del inventario (usa el atributo id_inventario)"""
        if not self.id_inventario:
            return []
        
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT ID_foto_inventario AS id, ID_inventario AS id_inventario, 
                       Foto_inventario AS foto
                FROM Fotos_inventario
                WHERE ID_inventario = %s
                ORDER BY ID_foto_inventario DESC
            """, (self.id_inventario,))
            return cursor.fetchall() or []
        finally:
            cursor.close()
            db.close()

    def obtener_ultima_foto(self) -> dict | None:
        """Obtiene la última foto del inventario (usa el atributo id_inventario)"""
        if not self.id_inventario:
            return None
        
        db = self._conexion()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT ID_foto_inventario AS id, Foto_inventario AS foto
                FROM Fotos_inventario
                WHERE ID_inventario = %s
                ORDER BY ID_foto_inventario DESC
                LIMIT 1
            """, (self.id_inventario,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()

    # ==================== MÉTODOS DE OPERACIÓN ====================

    def verificar_existencia(self) -> bool:
        """Verifica si una foto existe (usa el atributo id_foto_inventario)"""
        if not self.id_foto_inventario:
            return False
        db = self._conexion()
        if not db:
            return False
        cursor = db.cursor()
        try:
            cursor.execute("SELECT 1 FROM Fotos_inventario WHERE ID_foto_inventario = %s LIMIT 1", (self.id_foto_inventario,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    def registrar_foto(self) -> str:
        """Registra una nueva foto usando los atributos de la instancia"""
        if not self.id_inventario or not self.foto_inventario:
            raise ValueError("ID de inventario y foto son requeridos")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = None
        try:
            cursor = db.cursor()
            self.id_foto_inventario = self._siguiente_id()
            cursor.execute("""
                INSERT INTO Fotos_inventario (ID_foto_inventario, ID_inventario, Foto_inventario)
                VALUES (%s, %s, %s)
            """, (self.id_foto_inventario, self.id_inventario, self.foto_inventario))
            db.commit()
            return self.id_foto_inventario
        except Exception as e:
            if db:
                db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def actualizar_foto(self) -> bool:
        """Actualiza una foto usando los atributos de la instancia"""
        if not self.id_foto_inventario or not self.foto_inventario:
            raise ValueError("ID de foto y foto son requeridos")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE Fotos_inventario 
                SET Foto_inventario = %s 
                WHERE ID_foto_inventario = %s
            """, (self.foto_inventario, self.id_foto_inventario))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
            db.close()

    def eliminar_foto(self) -> bool:
        """Elimina una foto usando el atributo id_foto_inventario"""
        if not self.id_foto_inventario:
            raise ValueError("ID de foto es requerido")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM Fotos_inventario WHERE ID_foto_inventario = %s", (self.id_foto_inventario,))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
            db.close()