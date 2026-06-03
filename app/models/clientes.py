from app.models.database import conectar


class GestionClientes(conectar):
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
        finally:
            cursor.close()
            db.close()

    def listar_clientes(self):
        return self._consultar(
            """
            SELECT
                c.ID_cliente AS ID_c,
                c.Nombre_cliente AS nombre,
                COALESCE(pn.Apellido_cliente, '') AS apellido,
                c.Celular_cliente AS celular,
                c.Correo_cliente AS correo,
                c.Direccion_cliente AS direccion,
                CASE
                    WHEN cj.ID_cliente IS NOT NULL THEN 'Juridico'
                    WHEN pn.ID_cliente IS NOT NULL THEN 'Natural'
                    ELSE ''
                END AS tipo
            FROM Cliente c
            LEFT JOIN Persona_natural pn ON pn.ID_cliente = c.ID_cliente
            LEFT JOIN Cliente_juridico cj ON cj.ID_cliente = c.ID_cliente
            ORDER BY c.ID_cliente DESC
            """
        )

    def crear_cliente(self, cliente_id, nombre, apellido, celular, correo, direccion, tipo=None):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO Cliente (ID_cliente, Nombre_cliente, Direccion_cliente, Celular_cliente, Correo_cliente)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (cliente_id, nombre, direccion, celular, correo),
            )

            # Por compatibilidad con la UI actual (pide apellido), registramos como persona natural.
            cursor.execute(
                """
                INSERT INTO Persona_natural (ID_cliente, Apellido_cliente)
                VALUES (%s, %s)
                """,
                (cliente_id, apellido),
            )

            db.commit()
            return cliente_id
        except Exception:
            db.rollback()
            return None
        finally:
            cursor.close()
            db.close()

    def obtener_cliente_por_id(self, cliente_id):
        datos = self._consultar(
            """
            SELECT
                c.ID_cliente AS ID_c,
                c.Nombre_cliente AS nombre,
                COALESCE(pn.Apellido_cliente, '') AS apellido,
                c.Celular_cliente AS celular,
                c.Correo_cliente AS correo,
                c.Direccion_cliente AS direccion,
                CASE
                    WHEN cj.ID_cliente IS NOT NULL THEN 'Juridico'
                    WHEN pn.ID_cliente IS NOT NULL THEN 'Natural'
                    ELSE ''
                END AS tipo
            FROM Cliente c
            LEFT JOIN Persona_natural pn ON pn.ID_cliente = c.ID_cliente
            LEFT JOIN Cliente_juridico cj ON cj.ID_cliente = c.ID_cliente
            WHERE c.ID_cliente = %s
            LIMIT 1
            """,
            (cliente_id,),
        )
        return datos[0] if datos else None

    def crear_cliente_con_id(self, cliente_id, nombre, apellido, celular, correo, direccion, tipo=None):
        return self.crear_cliente(cliente_id, nombre, apellido, celular, correo, direccion, tipo)

    def actualizar_cliente(self, cliente_id_actual, nuevo_cliente_id, nombre, apellido, celular, correo, direccion, tipo=None):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor()
        try:
            cursor.execute(
                """
                UPDATE Cliente
                SET ID_cliente = %s,
                    Nombre_cliente = %s,
                    Direccion_cliente = %s,
                    Celular_cliente = %s,
                    Correo_cliente = %s
                WHERE ID_cliente = %s
                """,
                (nuevo_cliente_id, nombre, direccion, celular, correo, cliente_id_actual),
            )

            # Upsert de Persona_natural (apellido)
            cursor.execute(
                """
                INSERT INTO Persona_natural (ID_cliente, Apellido_cliente)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE Apellido_cliente = VALUES(Apellido_cliente)
                """,
                (nuevo_cliente_id, apellido),
            )

            db.commit()
            return cursor.rowcount
        except Exception:
            db.rollback()
            return None
        finally:
            cursor.close()
            db.close()

    def eliminar_cliente(self, cliente_id):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM Persona_natural WHERE ID_cliente = %s", (cliente_id,))
            cursor.execute("DELETE FROM Cliente_juridico WHERE ID_cliente = %s", (cliente_id,))
            cursor.execute("DELETE FROM Cliente WHERE ID_cliente = %s", (cliente_id,))
            db.commit()
            return cursor.rowcount
        except Exception:
            db.rollback()
            return None
        finally:
            cursor.close()
            db.close()
