from __future__ import annotations

from decimal import Decimal

from app.models.database import conectar

class Inventario(conectar):

    def _siguiente_id_texto(self, tabla: str, columna: str) -> str:
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")

        cursor = db.cursor()
        try:
            cursor.execute(f"SELECT COALESCE(MAX(CAST({columna} AS UNSIGNED)), 0) + 1 FROM {tabla}")
            row = cursor.fetchone()
            return str(int(row[0] or 0))
        finally:
            cursor.close()
            db.close()

    _BASE_SELECT = (
        "SELECT "
        "  cl.Nombre_Clase AS tipo, "
        "  ma.Nombre_marca AS N_marca, "
        "  p.Nombre_producto AS N_modelo, "
        "  (SELECT fi.Foto_inventario FROM Fotos_inventario fi "
        "     WHERE fi.ID_inventario = i.ID_inventario "
        "     ORDER BY fi.ID_foto_inventario DESC LIMIT 1) AS Foto_inventario, "
        "  i.Existencia, i.Costo_venta, "
        "  p.ID_producto AS ID_producto, "
        "  i.ID_inventario AS ID_inventario "
        "FROM Inventario i "
        "JOIN Producto p ON i.ID_producto = p.ID_producto "
        "LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca "
        "LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase "
    )

    def _listar(
        self,
        *,
        id_clase: str | None = None,
        id_marca: str | None = None,
        N_modelo: str | None = None,
    ):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            where = []
            params = []
            if id_clase is not None:
                where.append("p.ID_Clase = %s")
                params.append(str(id_clase))
            if id_marca is not None:
                where.append("p.ID_marca = %s")
                params.append(str(id_marca))
            if N_modelo is not None and str(N_modelo).strip() != "":
                where.append("p.Nombre_producto = %s")
                params.append(str(N_modelo).strip())

            sql = self._BASE_SELECT
            if where:
                sql += "WHERE " + " AND ".join(where) + " "
            sql += "ORDER BY cl.Nombre_Clase, ma.Nombre_marca, p.Nombre_producto"

            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
            # mysql-connector puede devolver Decimal para columnas DECIMAL.
            for row in rows or []:
                val = row.get("Costo_venta") if isinstance(row, dict) else None
                if isinstance(val, Decimal):
                    row["Costo_venta"] = float(val)
            return rows
        finally:
            cursor.close()
            db.close()

    def listar_inventario(self):
        # Compatibilidad: antes filtraba por Num_i (ya no existe). Devuelve todo.
        return self._listar()

    def listar_inventario_general(self):
        return self._listar()

    def listar_inventario_general_modelo(self, N_modelo: str):
        return self._listar(N_modelo=N_modelo)

    def listar_inventario_filtrado(self, *, num_i: int | None = None, N_modelo: str | None = None):
        # Compatibilidad: se ignora num_i.
        return self._listar(N_modelo=N_modelo)

    def registrar_stock(
        self,
        *,
        id_producto: str,
        existencia: int,
        costo_venta: Decimal,
        foto_inventario: str | None = None,
    ) -> str | None:
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor()
        try:
            # Mantener 1 registro de inventario por producto: actualizar si existe, si no insertar.
            cursor.execute(
                "SELECT ID_inventario FROM Inventario WHERE ID_producto=%s ORDER BY ID_inventario DESC LIMIT 1",
                (str(id_producto),),
            )
            row = cursor.fetchone()

            if row:
                id_inventario = str(row[0])
                cursor.execute(
                    "UPDATE Inventario SET Existencia=%s, Costo_venta=%s WHERE ID_inventario=%s",
                    (int(existencia), costo_venta, id_inventario),
                )
            else:
                id_inventario = self._siguiente_id_texto("Inventario", "ID_inventario")
                cursor.execute(
                    "INSERT INTO Inventario (ID_inventario, ID_producto, Existencia, Costo_venta, Numero_inventario) VALUES (%s, %s, %s, %s, %s)",
                    (id_inventario, str(id_producto), int(existencia), costo_venta, None),
                )

            foto_val = None
            if foto_inventario is not None:
                foto_val = str(foto_inventario).strip() or None

            if foto_val is not None:
                cursor.execute(
                    "SELECT ID_foto_inventario FROM Fotos_inventario WHERE ID_inventario=%s ORDER BY ID_foto_inventario DESC LIMIT 1",
                    (id_inventario,),
                )
                foto = cursor.fetchone()
                if foto:
                    cursor.execute(
                        "UPDATE Fotos_inventario SET Foto_inventario=%s WHERE ID_foto_inventario=%s",
                        (foto_val, str(foto[0])),
                    )
                else:
                    id_foto_inventario = self._siguiente_id_texto("Fotos_inventario", "ID_foto_inventario")
                    cursor.execute(
                        "INSERT INTO Fotos_inventario (ID_foto_inventario, ID_inventario, Foto_inventario) VALUES (%s, %s, %s)",
                        (id_foto_inventario, id_inventario, foto_val),
                    )

            db.commit()
            return id_inventario
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def listar_inventario_modelo(self, N_modelo: str):
        return self._listar(N_modelo=N_modelo)

# app/models/inventario.py - Agregar estos métodos

def obtener_producto_por_id(self, id_producto):
    """Obtiene información de un producto por su ID"""
    db = self.conexion1()
    if not db:
        return None
    
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT ID_producto, Nombre_producto FROM Producto WHERE ID_producto = %s LIMIT 1",
            (id_producto,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        db.close()


def obtener_stock_por_id(self, id_inventario):
    """Obtiene un registro de stock por su ID"""
    db = self.conexion1()
    if not db:
        return None
    
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT i.ID_inventario, i.ID_producto, i.Existencia, i.Costo_venta, 
                      p.Nombre_producto
               FROM Inventario i
               INNER JOIN Producto p ON p.ID_producto = i.ID_producto
               WHERE i.ID_inventario = %s
               LIMIT 1""",
            (id_inventario,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        db.close()


def actualizar_stock(self, id_inventario, existencia=None, costo_venta=None):
    """Actualiza un registro de stock"""
    if existencia is None and costo_venta is None:
        return False
    
    db = self.conexion1()
    if not db:
        return False
    
    cursor = db.cursor()
    try:
        updates = []
        params = []
        
        if existencia is not None:
            updates.append("Existencia = %s")
            params.append(existencia)
        
        if costo_venta is not None:
            updates.append("Costo_venta = %s")
            params.append(costo_venta)
        
        params.append(id_inventario)
        
        query = f"UPDATE Inventario SET {', '.join(updates)} WHERE ID_inventario = %s"
        cursor.execute(query, params)
        db.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        db.close()


    def eliminar_stock(self, id_inventario):
        """Elimina un registro de stock"""
        return self._ejecutar("DELETE FROM Inventario WHERE ID_inventario = %s", (id_inventario,))


    def listar_productos_sin_inventario(self):
        """Lista productos que no tienen registro en inventario"""
        return self._consultar(
            """SELECT ID_producto, Nombre_producto, ID_marca, ID_Clase
            FROM Producto
            WHERE ID_producto NOT IN (SELECT ID_producto FROM Inventario)
            ORDER BY Nombre_producto"""
        )
