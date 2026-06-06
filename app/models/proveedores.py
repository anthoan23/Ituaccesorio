from __future__ import annotations

from app.models.database import conectar


class Proveedores(conectar):
    def _consultar(self, query, params=None):
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

    def _ejecutar(self, query, params=None):
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

    def listar_proveedores(self, q: str | None = None):
        where_sql = ""
        params: list = []
        if q:
            where_sql = "WHERE (Nombre_proveedor LIKE %s OR CAST(ID_proveedor AS CHAR) LIKE %s)"
            params = [f"%{q}%", f"%{q}%"]

        return self._consultar(
            f"""
            SELECT
                ID_proveedor AS id,
                Nombre_proveedor AS nombre,
                Tipo_proveedor AS tipo,
                Celular_proveedor AS celular,
                Correo_proveedor AS correo,
                Direccion_proveedor AS direccion,
                Limite_credito AS limite_credito
            FROM Proveedor
            {where_sql}
            ORDER BY Nombre_proveedor ASC
            """,
            tuple(params),
        )

    def obtener_proveedor(self, id_proveedor: int):
        datos = self._consultar(
            """
            SELECT
                ID_proveedor AS id,
                Nombre_proveedor AS nombre,
                Tipo_proveedor AS tipo,
                Celular_proveedor AS celular,
                Correo_proveedor AS correo,
                Direccion_proveedor AS direccion,
                Limite_credito AS limite_credito
            FROM Proveedor
            WHERE ID_proveedor = %s
            LIMIT 1
            """,
            (id_proveedor,),
        )
        return datos[0] if datos else None

    def siguiente_id_proveedor(self) -> int:
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")

        cursor = db.cursor()
        try:
            cursor.execute("SELECT COALESCE(MAX(ID_proveedor), 0) + 1 FROM Proveedor")
            row = cursor.fetchone()
            return int(row[0])
        finally:
            cursor.close()
            db.close()

    def crear_proveedor(
        self,
        id_proveedor: int,
        nombre: str,
        tipo: str | None = None,
        celular: str | None = None,
        correo: str | None = None,
        direccion: str | None = None,
        limite_credito: int | None = None,
    ) -> int:
        resultado = self._ejecutar(
            """
            INSERT INTO Proveedor
                (ID_proveedor, Nombre_proveedor, Tipo_proveedor, Celular_proveedor, Correo_proveedor, Direccion_proveedor, Limite_credito)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s)
            """,
            (id_proveedor, nombre, tipo, celular, correo, direccion, limite_credito),
        )
        if resultado is None:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        return int(id_proveedor)

    def crear_proveedor_con_productos(
        self,
        id_proveedor: int,
        nombre: str,
        tipo: str | None = None,
        celular: str | None = None,
        correo: str | None = None,
        direccion: str | None = None,
        limite_credito: int | None = None,
        productos: list[dict] | None = None,
    ) -> int:
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")

        cursor = db.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO Proveedor
                    (ID_proveedor, Nombre_proveedor, Tipo_proveedor, Celular_proveedor, Correo_proveedor, Direccion_proveedor, Limite_credito)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s)
                """,
                (id_proveedor, nombre, tipo, celular, correo, direccion, limite_credito),
            )

            rows = []
            for item in (productos or []):
                id_modelo = item.get("id_modelo")
                costo = item.get("costo")
                rows.append((id_proveedor, str(id_modelo), costo if costo in (None, "") else int(costo)))

            if rows:
                cursor.executemany(
                    """
                    INSERT INTO Suministra (ID_proveedor, ID_producto, Costo_producto)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE Costo_producto = VALUES(Costo_producto)
                    """,
                    rows,
                )

            db.commit()
            return int(id_proveedor)
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def actualizar_proveedor(
        self,
        id_proveedor: int,
        nombre: str,
        tipo: str | None = None,
        celular: str | None = None,
        correo: str | None = None,
        direccion: str | None = None,
        limite_credito: int | None = None,
    ) -> bool:
        resultado = self._ejecutar(
            """
            UPDATE Proveedor
            SET
                Nombre_proveedor=%s,
                Tipo_proveedor=%s,
                Celular_proveedor=%s,
                Correo_proveedor=%s,
                Direccion_proveedor=%s,
                Limite_credito=%s
            WHERE ID_proveedor=%s
            """,
            (nombre, tipo, celular, correo, direccion, limite_credito, id_proveedor),
        )
        return bool(resultado and resultado > 0)

    def eliminar_proveedor(self, id_proveedor: int) -> bool:
        resultado = self._ejecutar("DELETE FROM Proveedor WHERE ID_proveedor=%s", (id_proveedor,))
        return bool(resultado and resultado > 0)

    def listar_productos_por_proveedor(self, id_proveedor: int):
        return self._consultar(
            """
            SELECT
                s.ID_producto AS id_modelo,
                p.Nombre_producto AS modelo_nombre,
                ma.Nombre_marca AS marca_nombre,
                cl.Nombre_Clase AS clase_nombre,
                s.Costo_producto AS costo
            FROM Suministra s
            JOIN Producto p ON s.ID_producto = p.ID_producto
            JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
            JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
            WHERE s.ID_proveedor = %s
            ORDER BY CAST(cl.ID_Clase AS UNSIGNED) ASC, CAST(ma.ID_marca AS UNSIGNED) ASC, p.Nombre_producto ASC
            """,
            (id_proveedor,),
        )

    def upsert_producto_proveedor(self, id_proveedor: int, id_modelo: str, costo: int | None) -> bool:
        resultado = self._ejecutar(
            """
            INSERT INTO Suministra (ID_proveedor, ID_producto, Costo_producto)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE Costo_producto = VALUES(Costo_producto)
            """,
            (id_proveedor, id_modelo, costo),
        )
        return bool(resultado and resultado > 0)

    def eliminar_producto_proveedor(self, id_proveedor: int, id_modelo: str) -> bool:
        resultado = self._ejecutar(
            "DELETE FROM Suministra WHERE ID_proveedor=%s AND ID_producto=%s",
            (id_proveedor, id_modelo),
        )
        return bool(resultado and resultado > 0)
