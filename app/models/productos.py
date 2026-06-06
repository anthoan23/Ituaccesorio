from __future__ import annotations

from app.models.database import conectar


class Productos(conectar):
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
            ORDER BY Nombre_Clase ASC
            """
        )

    def crear_clase(self, nombre: str, num_i: int | None = None) -> int:
        new_id = self._ejecutar(
            "INSERT INTO Clase_producto (Nombre_Clase) VALUES (%s)",
            (nombre,),
        )
        if new_id is None:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        return int(new_id)

    def actualizar_clase(self, id_clase: int, nombre: str, num_i: int | None = None) -> bool:
        resultado = self._ejecutar(
            "UPDATE Clase_producto SET Nombre_Clase=%s WHERE ID_Clase=%s",
            (nombre, id_clase),
        )
        return bool(resultado and resultado > 0)

    def eliminar_clase(self, id_clase: int) -> bool:
        resultado = self._ejecutar("DELETE FROM Clase_producto WHERE ID_Clase=%s", (id_clase,))
        return bool(resultado and resultado > 0)

    def listar_marcas(self, id_clase: int | None = None):
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
                ORDER BY ma.Nombre_marca ASC
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
            ORDER BY Nombre_marca ASC
            """
        )

    def crear_marca(self, id_clase: int | None, nombre: str) -> int:
        new_id = self._ejecutar(
            "INSERT INTO Marca_producto (Nombre_marca) VALUES (%s)",
            (nombre,),
        )
        if new_id is None:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        return int(new_id)

    def actualizar_marca(self, id_marca: int, id_clase: int | None, nombre: str) -> bool:
        resultado = self._ejecutar(
            "UPDATE Marca_producto SET Nombre_marca=%s WHERE ID_marca=%s",
            (nombre, id_marca),
        )
        return bool(resultado and resultado > 0)

    def eliminar_marca(self, id_marca: int) -> bool:
        resultado = self._ejecutar("DELETE FROM Marca_producto WHERE ID_marca=%s", (id_marca,))
        return bool(resultado and resultado > 0)

    def listar_modelos(self, id_marca: int | None = None, id_clase: int | None = None, q: str | None = None):
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
            ORDER BY cl.Nombre_Clase ASC, ma.Nombre_marca ASC, p.Nombre_producto ASC
            """,
            tuple(params),
        )

    def crear_modelo(self, id_clase: int, id_marca: int, nombre: str, descripcion: str | None = None) -> int:
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")

        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO Producto (ID_Clase, ID_marca, Nombre_producto, Descripcion) VALUES (%s, %s, %s, %s)",
                (id_clase, id_marca, nombre, descripcion),
            )
            id_producto = int(cursor.lastrowid)

            # Al registrar un producto nuevo, crear un inventario base en 0.
            cursor.execute(
                "INSERT INTO Inventario (ID_producto, Existencia, Costo_venta, Numero_inventario) VALUES (%s, %s, %s, %s)",
                (id_producto, 0, 0, None),
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
        id_modelo: int,
        id_clase: int,
        id_marca: int,
        nombre: str,
        descripcion: str | None = None,
    ) -> bool:
        resultado = self._ejecutar(
            "UPDATE Producto SET ID_Clase=%s, ID_marca=%s, Nombre_producto=%s, Descripcion=%s WHERE ID_producto=%s",
            (id_clase, id_marca, nombre, descripcion, id_modelo),
        )
        return bool(resultado and resultado > 0)

    def eliminar_modelo(self, id_modelo: int) -> bool:
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
