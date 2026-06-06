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
            where_sql = "WHERE (N_proveedor LIKE %s OR CAST(ID_proveedor AS CHAR) LIKE %s)"
            params = [f"%{q}%", f"%{q}%"]

        return self._consultar(
            f"""
            SELECT
                ID_proveedor AS id,
                N_proveedor AS nombre,
                Tipo_proveedor AS tipo,
                Celular_pr AS celular,
                Correo_pr AS correo,
                Direccion_pr AS direccion,
                Limite_credito AS limite_credito
            FROM proveedor
            {where_sql}
            ORDER BY N_proveedor ASC
            """,
            tuple(params),
        )

    def obtener_proveedor(self, id_proveedor: int):
        datos = self._consultar(
            """
            SELECT
                ID_proveedor AS id,
                N_proveedor AS nombre,
                Tipo_proveedor AS tipo,
                Celular_pr AS celular,
                Correo_pr AS correo,
                Direccion_pr AS direccion,
                Limite_credito AS limite_credito
            FROM proveedor
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
            cursor.execute("SELECT COALESCE(MAX(ID_proveedor), 0) + 1 FROM proveedor")
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
            INSERT INTO proveedor
                (ID_proveedor, N_proveedor, Tipo_proveedor, Celular_pr, Correo_pr, Direccion_pr, Limite_credito)
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
                INSERT INTO proveedor
                    (ID_proveedor, N_proveedor, Tipo_proveedor, Celular_pr, Correo_pr, Direccion_pr, Limite_credito)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s)
                """,
                (id_proveedor, nombre, tipo, celular, correo, direccion, limite_credito),
            )

            rows = []
            for item in (productos or []):
                id_modelo = item.get("id_modelo")
                costo = item.get("costo")
                rows.append((id_proveedor, int(id_modelo), costo if costo in (None, "") else int(costo)))

            if rows:
                cursor.executemany(
                    """
                    INSERT INTO proveedores_productos (ID_proveedor, ID_modelo, Costo)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE Costo = VALUES(Costo)
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
            UPDATE proveedor
            SET
                N_proveedor=%s,
                Tipo_proveedor=%s,
                Celular_pr=%s,
                Correo_pr=%s,
                Direccion_pr=%s,
                Limite_credito=%s
            WHERE ID_proveedor=%s
            """,
            (nombre, tipo, celular, correo, direccion, limite_credito, id_proveedor),
        )
        return bool(resultado and resultado > 0)

    def eliminar_proveedor(self, id_proveedor: int) -> bool:
        resultado = self._ejecutar("DELETE FROM proveedor WHERE ID_proveedor=%s", (id_proveedor,))
        return bool(resultado and resultado > 0)

    def listar_productos_por_proveedor(self, id_proveedor: int):
        return self._consultar(
            """
            SELECT
                pp.ID_modelo AS id_modelo,
                mo.N_modelo AS modelo_nombre,
                ma.N_marca AS marca_nombre,
                cl.N_Clase AS clase_nombre,
                pp.Costo AS costo
            FROM proveedores_productos pp
            JOIN modelo_producto mo ON pp.ID_modelo = mo.ID_modelo
            JOIN marca_producto ma ON mo.ID_marca = ma.ID_marca
            JOIN clase_producto cl ON ma.ID_clase = cl.ID_clase
            WHERE pp.ID_proveedor = %s
            ORDER BY cl.N_Clase ASC, ma.N_marca ASC, mo.N_modelo ASC
            """,
            (id_proveedor,),
        )

    def upsert_producto_proveedor(self, id_proveedor: int, id_modelo: int, costo: int | None) -> bool:
        resultado = self._ejecutar(
            """
            INSERT INTO proveedores_productos (ID_proveedor, ID_modelo, Costo)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE Costo = VALUES(Costo)
            """,
            (id_proveedor, id_modelo, costo),
        )
        return bool(resultado and resultado > 0)

    def eliminar_producto_proveedor(self, id_proveedor: int, id_modelo: int) -> bool:
        resultado = self._ejecutar(
            "DELETE FROM proveedores_productos WHERE ID_proveedor=%s AND ID_modelo=%s",
            (id_proveedor, id_modelo),
        )
        return bool(resultado and resultado > 0)
