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

    def crear_cliente(self, cliente_id, nombre, apellido, celular, correo, direccion, tipo=None):
        resultado = self._ejecutar(
            """
            INSERT INTO cliente (ID_c, Nombre_c, Apellido_c, Celular_c, Correo_c, Direccion_c, Tipo_c)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (cliente_id, nombre, apellido, celular, correo, direccion, tipo),
        )
        return cliente_id if resultado else None

    def obtener_cliente_por_id(self, cliente_id):
        datos = self._consultar(
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
            WHERE ID_c = %s
            LIMIT 1
            """,
            (cliente_id,),
        )
        return datos[0] if datos else None

    def crear_cliente_con_id(self, cliente_id, nombre, apellido, celular, correo, direccion, tipo=None):
        resultado = self._ejecutar(
            """
            INSERT INTO cliente (ID_c, Nombre_c, Apellido_c, Celular_c, Correo_c, Direccion_c, Tipo_c)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (cliente_id, nombre, apellido, celular, correo, direccion, tipo),
        )
        return cliente_id if resultado else None

    def actualizar_cliente(self, cliente_id_actual, nuevo_cliente_id, nombre, apellido, celular, correo, direccion, tipo=None):
        return self._ejecutar(
            """
            UPDATE cliente
            SET ID_c = %s,
                Nombre_c = %s,
                Apellido_c = %s,
                Celular_c = %s,
                Correo_c = %s,
                Direccion_c = %s,
                Tipo_c = %s
            WHERE ID_c = %s
            """,
            (nuevo_cliente_id, nombre, apellido, celular, correo, direccion, tipo, cliente_id_actual),
        )

    def eliminar_cliente(self, cliente_id):
        return self._ejecutar("DELETE FROM cliente WHERE ID_c = %s", (cliente_id,))
