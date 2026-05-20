from __future__ import annotations

from app.models.database import conectar

class Inventario(conectar):

    _BASE_SELECT = (
        "SELECT c.N_Clase AS tipo, mp.N_marca, m.N_modelo, "
        "ca.Capacidad AS Capacidad, ca.Color AS Color, "
        "s.Existencia, s.Costo_venta, s.ID_producto "
        "FROM stock s "
        "JOIN modelo_producto m ON s.ID_modelo = m.ID_modelo "
        "JOIN marca_producto mp ON m.ID_marca = mp.ID_marca "
        "JOIN clase_producto c ON mp.ID_clase = c.ID_clase "
        "LEFT JOIN caracteristica ca ON ca.ID_producto = s.ID_producto "
    )

    def _listar(self, *, num_i: int | None = None, N_modelo: str | None = None):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            where = []
            params = []
            if num_i is not None:
                where.append("c.Num_i = %s")
                params.append(int(num_i))
            if N_modelo is not None and str(N_modelo).strip() != "":
                where.append("m.N_modelo = %s")
                params.append(str(N_modelo).strip())

            sql = self._BASE_SELECT
            if where:
                sql += "WHERE " + " AND ".join(where) + " "
            sql += "ORDER BY c.N_Clase, mp.N_marca, m.N_modelo"

            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def listar_inventario(self):
        # Inventario de taller (repuestos/herramientas). En el dump, Num_i está en clase_producto.
        return self._listar(num_i=2)

    def listar_inventario_general(self):
        # Inventario general (sin filtrar por Num_i), coincide con la consulta que pasaste.
        return self._listar()

    def listar_inventario_general_modelo(self, N_modelo: str):
        return self._listar(N_modelo=N_modelo)

    def listar_inventario_por_num_i(self, num_i: int):
        return self._listar(num_i=num_i)

    def listar_inventario_filtrado(self, *, num_i: int | None = None, N_modelo: str | None = None):
        return self._listar(num_i=num_i, N_modelo=N_modelo)

    def registrar_stock(
        self,
        *,
        id_modelo: int,
        existencia: int,
        costo_venta: int,
        capacidad: str | None = None,
        color: str | None = None,
    ) -> int | None:
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT ID_producto FROM stock WHERE ID_modelo=%s LIMIT 1",
                (int(id_modelo),),
            )
            row = cursor.fetchone()

            if row:
                id_producto = int(row[0])
                cursor.execute(
                    "UPDATE stock SET Existencia=%s, Costo_venta=%s WHERE ID_producto=%s",
                    (int(existencia), int(costo_venta), id_producto),
                )
            else:
                cursor.execute(
                    "INSERT INTO stock (ID_modelo, Existencia, Costo_venta) VALUES (%s, %s, %s)",
                    (int(id_modelo), int(existencia), int(costo_venta)),
                )
                id_producto = int(cursor.lastrowid)

            cap_val = None
            if capacidad is not None:
                cap_val = str(capacidad).strip() or None

            color_val = None
            if color is not None:
                color_val = str(color).strip() or None

            # Upsert de caracteristica solo si se envía al menos uno.
            if capacidad is not None or color is not None:
                cursor.execute(
                    "SELECT 1 FROM caracteristica WHERE ID_producto=%s LIMIT 1",
                    (id_producto,),
                )
                existe_car = cursor.fetchone() is not None
                if existe_car:
                    cursor.execute(
                        "UPDATE caracteristica SET Capacidad=%s, Color=%s WHERE ID_producto=%s",
                        (cap_val, color_val, id_producto),
                    )
                else:
                    cursor.execute(
                        "INSERT INTO caracteristica (ID_producto, Capacidad, Color) VALUES (%s, %s, %s)",
                        (id_producto, cap_val, color_val),
                    )

            db.commit()
            return id_producto
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def listar_inventario_modelo(self, N_modelo: str):
        return self._listar(num_i=2, N_modelo=N_modelo)

