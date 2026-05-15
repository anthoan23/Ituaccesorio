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
                    ID_clase AS id,
                    N_Clase AS nombre,
                    Num_i AS num_i
                FROM clase_producto
                ORDER BY N_Clase ASC
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
                "INSERT INTO clase_producto (N_Clase, Num_i) VALUES (%s, %s)",
                (nombre, num_i),
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
                "UPDATE clase_producto SET N_Clase=%s, Num_i=%s WHERE ID_clase=%s",
                (nombre, num_i, id_clase),
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
            cursor.execute("DELETE FROM clase_producto WHERE ID_clase=%s", (id_clase,))
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
                        ID_marca AS id,
                        ID_clase AS id_clase,
                        N_marca AS nombre
                    FROM marca_producto
                    WHERE ID_clase = %s
                    ORDER BY N_marca ASC
                    """,
                    (id_clase,),
                )
            else:
                cursor.execute(
                    """
                    SELECT
                        ID_marca AS id,
                        ID_clase AS id_clase,
                        N_marca AS nombre
                    FROM marca_producto
                    ORDER BY N_marca ASC
                    """
                )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def crear_marca(self, id_clase: int, nombre: str) -> int:
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")

        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO marca_producto (ID_clase, N_marca) VALUES (%s, %s)",
                (id_clase, nombre),
            )
            db.commit()
            return int(cursor.lastrowid)
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def actualizar_marca(self, id_marca: int, id_clase: int, nombre: str) -> bool:
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE marca_producto SET ID_clase=%s, N_marca=%s WHERE ID_marca=%s",
                (id_clase, nombre, id_marca),
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
            cursor.execute("DELETE FROM marca_producto WHERE ID_marca=%s", (id_marca,))
            db.commit()
            return cursor.rowcount > 0
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def listar_modelos(self, id_marca: int | None = None, q: str | None = None):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            where = []
            params: list = []

            if id_marca:
                where.append("mo.ID_marca = %s")
                params.append(id_marca)
            if q:
                where.append("mo.N_modelo LIKE %s")
                params.append(f"%{q}%")

            where_sql = ("WHERE " + " AND ".join(where)) if where else ""

            cursor.execute(
                f"""
                SELECT
                    mo.ID_modelo AS id,
                    mo.ID_marca AS id_marca,
                    mo.N_modelo AS nombre,
                    ma.N_marca AS marca_nombre,
                    ma.ID_clase AS id_clase,
                    cl.N_Clase AS clase_nombre
                FROM modelo_producto mo
                JOIN marca_producto ma ON mo.ID_marca = ma.ID_marca
                JOIN clase_producto cl ON ma.ID_clase = cl.ID_clase
                {where_sql}
                ORDER BY cl.N_Clase ASC, ma.N_marca ASC, mo.N_modelo ASC
                """,
                tuple(params),
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def crear_modelo(self, id_marca: int, nombre: str) -> int:
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")

        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO modelo_producto (ID_marca, N_modelo) VALUES (%s, %s)",
                (id_marca, nombre),
            )
            db.commit()
            return int(cursor.lastrowid)
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def actualizar_modelo(self, id_modelo: int, id_marca: int, nombre: str) -> bool:
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE modelo_producto SET ID_marca=%s, N_modelo=%s WHERE ID_modelo=%s",
                (id_marca, nombre, id_modelo),
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
            cursor.execute("DELETE FROM modelo_producto WHERE ID_modelo=%s", (id_modelo,))
            db.commit()
            return cursor.rowcount > 0
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
