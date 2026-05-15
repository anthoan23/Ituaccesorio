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
                ID_c,
                Nombre_c AS nombre,
                Apellido_c AS apellido,
                Celular_c AS celular,
                Correo_c AS correo,
                Direccion_c AS direccion,
                Tipo_c AS tipo
            FROM cliente
            ORDER BY ID_c DESC
            """
        )

    def crear_cliente(self, nombre, apellido, celular, correo, direccion, tipo=None):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor()
        try:
            cursor.execute("SELECT COALESCE(MAX(ID_c), 0) + 1 FROM cliente")
            row = cursor.fetchone()
            next_id = int(row[0]) if row else 1
            cursor.execute(
                "INSERT INTO cliente (ID_c, Nombre_c, Apellido_c, Celular_c, Correo_c, Direccion_c, Tipo_c) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (next_id, nombre, apellido, celular, correo, direccion, tipo),
            )
            db.commit()
            return next_id
        finally:
            cursor.close()
            db.close()

    def actualizar_cliente(self, cliente_id, nombre, apellido, celular, correo, direccion, tipo=None):
        return self._ejecutar(
            """
            UPDATE cliente
            SET Nombre_c = %s,
                Apellido_c = %s,
                Celular_c = %s,
                Correo_c = %s,
                Direccion_c = %s,
                Tipo_c = %s
            WHERE ID_c = %s
            """,
            (nombre, apellido, celular, correo, direccion, tipo, cliente_id),
        )

    def eliminar_cliente(self, cliente_id):
        return self._ejecutar("DELETE FROM cliente WHERE ID_c = %s", (cliente_id,))
