from __future__ import annotations
from decimal import Decimal
from app.models.database import conectar
from app.models.productos import Producto


class Inventario(conectar):
    """Modelo para la tabla Inventario"""
    
    def __init__(self, id_inventario: str = "", id_producto: str = "", 
                 existencia: int = 0, costo_venta: Decimal = Decimal(0)):
        self.id_inventario = id_inventario
        self.id_producto = id_producto
        self.existencia = existencia
        self.costo_venta = costo_venta

    def _siguiente_id(self) -> str:
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        cursor = db.cursor()
        try:
            cursor.execute("SELECT COALESCE(MAX(CAST(ID_inventario AS UNSIGNED)), 0) + 1 FROM Inventario")
            row = cursor.fetchone()
            return str(int(row[0] or 0))
        finally:
            cursor.close()
            db.close()

    def listar_inventario(self):
        """Lista todo el inventario con sus relaciones"""
        db = self.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    i.ID_inventario AS id_inventario,
                    i.ID_producto AS id_producto,
                    i.Existencia AS existencia,
                    i.Costo_venta AS costo_venta,
                    p.Nombre_producto AS nombre_producto,
                    ma.Nombre_marca AS nombre_marca,
                    cl.Nombre_Clase AS nombre_clase,
                    (SELECT fi.Foto_inventario FROM Fotos_inventario fi 
                     WHERE fi.ID_inventario = i.ID_inventario 
                     ORDER BY fi.ID_foto_inventario DESC LIMIT 1) AS foto_inventario
                FROM Inventario i
                JOIN Producto p ON i.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                ORDER BY cl.Nombre_Clase, ma.Nombre_marca, p.Nombre_producto
            """)
            rows = cursor.fetchall() or []
            # Convertir Decimal a float para JSON
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

    def listar_inventario_general_modelo(self, nombre_modelo: str):
        """Lista inventario filtrado por modelo"""
        db = self.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    i.ID_inventario AS id_inventario,
                    i.ID_producto AS id_producto,
                    i.Existencia AS existencia,
                    i.Costo_venta AS costo_venta,
                    p.Nombre_producto AS nombre_producto,
                    ma.Nombre_marca AS nombre_marca,
                    cl.Nombre_Clase AS nombre_clase,
                    (SELECT fi.Foto_inventario FROM Fotos_inventario fi 
                     WHERE fi.ID_inventario = i.ID_inventario 
                     ORDER BY fi.ID_foto_inventario DESC LIMIT 1) AS foto_inventario
                FROM Inventario i
                JOIN Producto p ON i.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                WHERE p.Nombre_producto LIKE %s
                ORDER BY cl.Nombre_Clase, ma.Nombre_marca, p.Nombre_producto
            """, (f"%{nombre_modelo}%",))
            rows = cursor.fetchall() or []
            for row in rows:
                if isinstance(row.get("costo_venta"), Decimal):
                    row["costo_venta"] = float(row["costo_venta"])
            return rows
        finally:
            cursor.close()
            db.close()

    def listar_inventario_filtrado(self, num_i: int | None = None, N_modelo: str | None = None):
        """Lista inventario con filtros opcionales"""
        db = self.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            where = []
            params = []
            
            if N_modelo:
                where.append("p.Nombre_producto = %s")
                params.append(N_modelo)
            
            where_sql = f"WHERE {' AND '.join(where)}" if where else ""
            
            cursor.execute(f"""
                SELECT 
                    i.ID_inventario AS id_inventario,
                    i.ID_producto AS id_producto,
                    i.Existencia AS existencia,
                    i.Costo_venta AS costo_venta,
                    p.Nombre_producto AS nombre_producto,
                    ma.Nombre_marca AS nombre_marca,
                    cl.Nombre_Clase AS nombre_clase,
                    (SELECT fi.Foto_inventario FROM Fotos_inventario fi 
                     WHERE fi.ID_inventario = i.ID_inventario 
                     ORDER BY fi.ID_foto_inventario DESC LIMIT 1) AS foto_inventario
                FROM Inventario i
                JOIN Producto p ON i.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                {where_sql}
                ORDER BY cl.Nombre_Clase, ma.Nombre_marca, p.Nombre_producto
            """, tuple(params))
            rows = cursor.fetchall() or []
            for row in rows:
                if isinstance(row.get("costo_venta"), Decimal):
                    row["costo_venta"] = float(row["costo_venta"])
            return rows
        finally:
            cursor.close()
            db.close()

    def listar_inventario_modelo(self, nombre_modelo: str):
        """Lista inventario por modelo exacto"""
        return self.listar_inventario_filtrado(N_modelo=nombre_modelo)

    def registrar_stock(self, id_producto: str, existencia: int, 
                        costo_venta: Decimal, foto_inventario: str | None = None) -> str | None:
        """Registra o actualiza stock de un producto"""
        if not id_producto:
            raise ValueError("ID del producto es requerido")
        
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            # Buscar si ya existe inventario para este producto
            cursor.execute(
                "SELECT ID_inventario FROM Inventario WHERE ID_producto = %s LIMIT 1",
                (str(id_producto),)
            )
            row = cursor.fetchone()
            
            if row:
                # Actualizar existente
                id_inventario = str(row[0])
                cursor.execute(
                    "UPDATE Inventario SET Existencia = %s, Costo_venta = %s WHERE ID_inventario = %s",
                    (int(existencia), costo_venta, id_inventario)
                )
            else:
                # Crear nuevo
                id_inventario = self._siguiente_id()
                cursor.execute("""
                    INSERT INTO Inventario (ID_inventario, ID_producto, Existencia, Costo_venta, Numero_inventario)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_inventario, str(id_producto), int(existencia), costo_venta, None))
            
            # Guardar foto si se proporcionó
            if foto_inventario:
                from app.models.inventario import FotosInventario
                fotos = FotosInventario()
                fotos.insertar_foto(id_inventario, foto_inventario)
            
            db.commit()
            return id_inventario
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
            db.close()


class FotosInventario(conectar):
    """Modelo para la tabla Fotos_inventario"""
    
    def __init__(self, id_foto_inventario: str = "", id_inventario: str = "", 
                 foto_inventario: str = ""):
        self.id_foto_inventario = id_foto_inventario
        self.id_inventario = id_inventario
        self.foto_inventario = foto_inventario

    def _siguiente_id(self) -> str:
        db = self.conexion1()
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

    def listar_fotos(self, id_inventario: str):
        """Lista todas las fotos de un inventario"""
        db = self.conexion1()
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
            """, (id_inventario,))
            return cursor.fetchall() or []
        finally:
            cursor.close()
            db.close()

    def insertar_foto(self, id_inventario: str, foto_inventario: str) -> str:
        """Inserta una nueva foto para un inventario"""
        if not id_inventario or not foto_inventario:
            raise ValueError("ID de inventario y foto son requeridos")
        
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            new_id = self._siguiente_id()
            cursor.execute("""
                INSERT INTO Fotos_inventario (ID_foto_inventario, ID_inventario, Foto_inventario)
                VALUES (%s, %s, %s)
            """, (new_id, id_inventario, foto_inventario))
            db.commit()
            return new_id
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
            db.close()

    def actualizar_foto(self, id_foto_inventario: str, foto_inventario: str) -> bool:
        """Actualiza una foto existente"""
        if not id_foto_inventario or not foto_inventario:
            raise ValueError("ID de foto y foto son requeridos")
        
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE Fotos_inventario 
                SET Foto_inventario = %s 
                WHERE ID_foto_inventario = %s
            """, (foto_inventario, id_foto_inventario))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
            db.close()

    def eliminar_foto(self, id_foto_inventario: str) -> bool:
        """Elimina una foto"""
        if not id_foto_inventario:
            raise ValueError("ID de foto es requerido")
        
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM Fotos_inventario WHERE ID_foto_inventario = %s", (id_foto_inventario,))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
            db.close()

    def obtener_ultima_foto(self, id_inventario: str) -> dict | None:
        """Obtiene la última foto de un inventario"""
        db = self.conexion1()
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
            """, (id_inventario,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()