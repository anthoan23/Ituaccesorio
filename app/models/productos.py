from __future__ import annotations

from app.models.database import conectar


class Productos(conectar):
    def listar_clases(self):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    ID_Clase AS id,
                    Nombre_Clase AS nombre,
                    NULL AS num_i
                FROM Clase_producto
                ORDER BY Nombre_Clase ASC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def crear_clase(self, nombre: str, num_i: int | None = None) -> int:
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")

        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO Clase_producto (Nombre_Clase) VALUES (%s)",
                (nombre,),
            )
            db.commit()
            return int(cursor.lastrowid)
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def actualizar_clase(self, id_clase: int, nombre: str, num_i: int | None = None) -> bool:
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE Clase_producto SET Nombre_Clase=%s WHERE ID_Clase=%s",
                (nombre, id_clase),
            )
            db.commit()
            return cursor.rowcount > 0
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def eliminar_clase(self, id_clase: int) -> bool:
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM Clase_producto WHERE ID_Clase=%s", (id_clase,))
            db.commit()
            return cursor.rowcount > 0
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def listar_marcas(self, id_clase: int | None = None):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            if id_clase:
                cursor.execute(
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
            else:
                cursor.execute(
                    """
                    SELECT
                        ID_marca AS id,
                        NULL AS id_clase,
                        Nombre_marca AS nombre
                    FROM Marca_producto
                    ORDER BY Nombre_marca ASC
                    """
                )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def crear_marca(self, id_clase: int | None, nombre: str) -> int:
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")

        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO Marca_producto (Nombre_marca) VALUES (%s)",
                (nombre,),
            )
            db.commit()
            return int(cursor.lastrowid)
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def actualizar_marca(self, id_marca: int, id_clase: int | None, nombre: str) -> bool:
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE Marca_producto SET Nombre_marca=%s WHERE ID_marca=%s",
                (nombre, id_marca),
            )
            db.commit()
            return cursor.rowcount > 0
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def eliminar_marca(self, id_marca: int) -> bool:
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM Marca_producto WHERE ID_marca=%s", (id_marca,))
            db.commit()
            return cursor.rowcount > 0
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def listar_modelos(self, id_marca: int | None = None, id_clase: int | None = None, q: str | None = None):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
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

            cursor.execute(
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
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

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
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE Producto SET ID_Clase=%s, ID_marca=%s, Nombre_producto=%s, Descripcion=%s WHERE ID_producto=%s",
                (id_clase, id_marca, nombre, descripcion, id_modelo),
            )
            db.commit()
            return cursor.rowcount > 0
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

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
