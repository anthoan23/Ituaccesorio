from __future__ import annotations

from app.models.database import conectar


class Productos(conectar):
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

    def _consultar(self, query: str, params: tuple | list | None = None):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def _ejecutar(self, query: str, params: tuple | list | None = None):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor()
        try:
            cursor.execute(query, params or ())
            db.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def listar_clases(self):
        return self._consultar(
            """
            SELECT
                ID_Clase AS id,
                Nombre_Clase AS nombre,
                NULL AS num_i
            FROM Clase_producto
            ORDER BY CAST(ID_Clase AS UNSIGNED) ASC, Nombre_Clase ASC
            """
        )

    def crear_clase(self, nombre: str, num_i: int | None = None) -> str:
        new_id = self._siguiente_id_texto("Clase_producto", "ID_Clase")
        resultado = self._ejecutar(
            "INSERT INTO Clase_producto (ID_Clase, Nombre_Clase) VALUES (%s, %s)",
            (new_id, nombre),
        )
        if resultado is None:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        return new_id

    def actualizar_clase(self, id_clase: str, nombre: str, num_i: int | None = None) -> bool:
        resultado = self._ejecutar(
            "UPDATE Clase_producto SET Nombre_Clase=%s WHERE ID_Clase=%s",
            (nombre, id_clase),
        )
        return bool(resultado and resultado > 0)

    def eliminar_clase(self, id_clase: str) -> bool:
        resultado = self._ejecutar("DELETE FROM Clase_producto WHERE ID_Clase=%s", (id_clase,))
        return bool(resultado and resultado > 0)

    def listar_marcas(self, id_clase: str | None = None):
        if id_clase:
            return self._consultar(
                """
                SELECT
                    ma.ID_marca AS id,
                    %s AS id_clase,
                    ma.Nombre_marca AS nombre
                FROM Marca_producto ma
                JOIN Producto p ON p.ID_marca = ma.ID_marca
                WHERE p.ID_Clase = %s
                GROUP BY ma.ID_marca, ma.Nombre_marca
                ORDER BY CAST(ma.ID_marca AS UNSIGNED) ASC, ma.Nombre_marca ASC
                """,
                (id_clase, id_clase),
            )

        return self._consultar(
            """
            SELECT
                ID_marca AS id,
                NULL AS id_clase,
                Nombre_marca AS nombre
            FROM Marca_producto
            ORDER BY CAST(ID_marca AS UNSIGNED) ASC, Nombre_marca ASC
            """
        )

    def crear_marca(self, id_clase: str | None, nombre: str) -> str:
        new_id = self._siguiente_id_texto("Marca_producto", "ID_marca")
        resultado = self._ejecutar(
            "INSERT INTO Marca_producto (ID_marca, Nombre_marca) VALUES (%s, %s)",
            (new_id, nombre),
        )
        if resultado is None:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        return new_id

    def actualizar_marca(self, id_marca: str, id_clase: str | None, nombre: str) -> bool:
        resultado = self._ejecutar(
            "UPDATE Marca_producto SET Nombre_marca=%s WHERE ID_marca=%s",
            (nombre, id_marca),
        )
        return bool(resultado and resultado > 0)

    def eliminar_marca(self, id_marca: str) -> bool:
        resultado = self._ejecutar("DELETE FROM Marca_producto WHERE ID_marca=%s", (id_marca,))
        return bool(resultado and resultado > 0)

    def listar_modelos(self, id_marca: str | None = None, id_clase: str | None = None, q: str | None = None):
        where = []
        params: list = []

        if id_marca:
            where.append("p.ID_marca = %s")
            params.append(id_marca)
        if id_clase:
            where.append("p.ID_Clase = %s")
            params.append(id_clase)
        if q:
            where.append("p.Nombre_producto LIKE %s")
            params.append(f"%{q}%")

        where_sql = ("WHERE " + " AND ".join(where)) if where else ""

        return self._consultar(
            f"""
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
            """,
            tuple(params),
        )

    def crear_modelo(self, id_clase: str, id_marca: str, nombre: str, descripcion: str | None = None) -> str:
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")

        cursor = db.cursor()
        try:
            id_producto = self._siguiente_id_texto("Producto", "ID_producto")
            cursor.execute(
                "INSERT INTO Producto (ID_producto, ID_Clase, ID_marca, Nombre_producto, Descripcion) VALUES (%s, %s, %s, %s, %s)",
                (id_producto, id_clase, id_marca, nombre, descripcion),
            )

            id_inventario = self._siguiente_id_texto("Inventario", "ID_inventario")
            cursor.execute(
                "INSERT INTO Inventario (ID_inventario, ID_producto, Existencia, Costo_venta, Numero_inventario) VALUES (%s, %s, %s, %s, %s)",
                (id_inventario, id_producto, 0, 0, None),
            )

            db.commit()
            return id_producto
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def actualizar_modelo(
        self,
        id_modelo: str,
        id_clase: str,
        id_marca: str,
        nombre: str,
        descripcion: str | None = None,
    ) -> bool:
        resultado = self._ejecutar(
            "UPDATE Producto SET ID_Clase=%s, ID_marca=%s, Nombre_producto=%s, Descripcion=%s WHERE ID_producto=%s",
            (id_clase, id_marca, nombre, descripcion, id_modelo),
        )
        return bool(resultado and resultado > 0)

    def eliminar_modelo(self, id_modelo: str) -> bool:
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            # Borrar relaciones directas primero (si existen) para evitar restricciones FK.
            cursor.execute("DELETE FROM Inventario WHERE ID_producto=%s", (id_modelo,))
            cursor.execute("DELETE FROM Suministra WHERE ID_producto=%s", (id_modelo,))
            cursor.execute("DELETE FROM Producto WHERE ID_producto=%s", (id_modelo,))
            db.commit()
            return cursor.rowcount > 0
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
