from __future__ import annotations

from decimal import Decimal

from app.models.database import conectar

class Inventario(conectar):

    _BASE_SELECT = (
        "SELECT "
        "  cl.Nombre_Clase AS tipo, "
        "  ma.Nombre_marca AS N_marca, "
        "  p.Nombre_producto AS N_modelo, "
        "  (SELECT fi.Capacidad FROM Fotos_inventario fi "
        "     WHERE fi.ID_inventario = i.ID_inventario "
        "     ORDER BY fi.ID_foto_inventario DESC LIMIT 1) AS Capacidad, "
        "  (SELECT fi.Color FROM Fotos_inventario fi "
        "     WHERE fi.ID_inventario = i.ID_inventario "
        "     ORDER BY fi.ID_foto_inventario DESC LIMIT 1) AS Color, "
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
        id_clase: int | None = None,
        id_marca: int | None = None,
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
                params.append(int(id_clase))
            if id_marca is not None:
                where.append("p.ID_marca = %s")
                params.append(int(id_marca))
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

    def listar_inventario_por_num_i(self, num_i: int):
        # Compatibilidad: Num_i ya no existe.
        return self._listar()

    def listar_inventario_filtrado(self, *, num_i: int | None = None, N_modelo: str | None = None):
        # Compatibilidad: se ignora num_i.
        return self._listar(N_modelo=N_modelo)

    def registrar_stock(
        self,
        *,
        id_producto: int,
        existencia: int,
        costo_venta: Decimal,
        capacidad: str | None = None,
        color: str | None = None,
    ) -> int | None:
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor()
        try:
            # Mantener 1 registro de inventario por producto: actualizar si existe, si no insertar.
            cursor.execute(
                "SELECT ID_inventario FROM Inventario WHERE ID_producto=%s ORDER BY ID_inventario DESC LIMIT 1",
                (int(id_producto),),
            )
            row = cursor.fetchone()

            if row:
                id_inventario = int(row[0])
                cursor.execute(
                    "UPDATE Inventario SET Existencia=%s, Costo_venta=%s WHERE ID_inventario=%s",
                    (int(existencia), costo_venta, id_inventario),
                )
            else:
                cursor.execute(
                    "INSERT INTO Inventario (ID_producto, Existencia, Costo_venta, Numero_inventario) VALUES (%s, %s, %s, %s)",
                    (int(id_producto), int(existencia), costo_venta, None),
                )
                id_inventario = int(cursor.lastrowid)

            cap_val = None
            if capacidad is not None:
                cap_val = str(capacidad).strip() or None

            color_val = None
            if color is not None:
                color_val = str(color).strip() or None

            # Upsert de capacidad/color en Fotos_inventario solo si se envía al menos uno.
            if capacidad is not None or color is not None:
                cursor.execute(
                    "SELECT ID_foto_inventario FROM Fotos_inventario WHERE ID_inventario=%s ORDER BY ID_foto_inventario DESC LIMIT 1",
                    (id_inventario,),
                )
                foto = cursor.fetchone()
                if foto:
                    cursor.execute(
                        "UPDATE Fotos_inventario SET Capacidad=%s, Color=%s WHERE ID_foto_inventario=%s",
                        (cap_val, color_val, int(foto[0])),
                    )
                else:
                    cursor.execute(
                        "INSERT INTO Fotos_inventario (ID_inventario, Capacidad, Color) VALUES (%s, %s, %s)",
                        (id_inventario, cap_val, color_val),
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

