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
        """Lista todos los clientes con su información completa"""
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
            SELECT 
                c.ID_cliente AS id,
                c.Nombre_cliente AS nombre,
                c.Direccion_cliente AS direccion,
                c.Celular_cliente AS celular,
                c.Correo_cliente AS correo,
                p.Apellido_cliente AS apellido,
                CASE 
                    WHEN p.ID_cliente IS NOT NULL THEN 'natural'
                    WHEN j.ID_cliente IS NOT NULL THEN 'juridico'
                    ELSE 'natural'
                END AS tipo
            FROM Cliente c
            LEFT JOIN Persona_natural p ON c.ID_cliente = p.ID_cliente
            LEFT JOIN Cliente_juridico j ON c.ID_cliente = j.ID_cliente
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
        """Obtiene un cliente por su ID incluyendo su tipo y apellido"""
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
            SELECT 
                c.ID_cliente AS id,
                c.Nombre_cliente AS nombre,
                c.Direccion_cliente AS direccion,
                c.Celular_cliente AS celular,
                c.Correo_cliente AS correo,
                p.Apellido_cliente AS apellido,
                CASE 
                    WHEN p.ID_cliente IS NOT NULL THEN 'natural'
                    WHEN j.ID_cliente IS NOT NULL THEN 'juridico'
                    ELSE 'natural'
                END AS tipo
            FROM Cliente c
            LEFT JOIN Persona_natural p ON c.ID_cliente = p.ID_cliente
            LEFT JOIN Cliente_juridico j ON c.ID_cliente = j.ID_cliente
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
    def crear_cliente(self, cliente_id, nombre, apellido=None, celular=None, correo=None, direccion=None):
        """Crea un nuevo cliente (persona natural por defecto)"""
        
        # Primero insertar en la tabla Cliente
        resultado = self._ejecutar(
            """
            INSERT INTO Cliente (ID_cliente, Nombre_cliente, Direccion_cliente, Celular_cliente, Correo_cliente)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (cliente_id, nombre, direccion, celular, correo),
        )
        
        if not resultado:
            return None
        
        # Si es persona natural (ID numérico), insertar apellido en Persona_natural
        if str(cliente_id).isdigit() and apellido:
            self._ejecutar(
                """
                INSERT INTO Persona_natural (ID_cliente, Apellido_cliente)
                VALUES (%s, %s)
                """,
                (cliente_id, apellido)
            )
        
        return cliente_id

    def crear_cliente_con_id(self, cliente_id, nombre, apellido=None, celular=None, correo=None, direccion=None, tipo=None):
        """Crea un cliente (compatible con la estructura anterior)"""
        return self.crear_cliente(cliente_id, nombre, apellido, celular, correo, direccion)

    def actualizar_cliente(self, cliente_id_actual, nuevo_cliente_id, nombre, apellido=None, celular=None, correo=None, direccion=None, tipo=None):
        """Actualiza un cliente existente"""
        
        # Actualizar tabla Cliente
        resultado = self._ejecutar(
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
        
        # Si hay apellido y es persona natural, actualizar Persona_natural
        if apellido and str(nuevo_cliente_id).isdigit():
            # Verificar si ya existe registro en Persona_natural
            existe = self._consultar(
                "SELECT 1 FROM Persona_natural WHERE ID_cliente = %s",
                (nuevo_cliente_id,)
            )
            if existe:
                self._ejecutar(
                    "UPDATE Persona_natural SET Apellido_cliente = %s WHERE ID_cliente = %s",
                    (apellido, nuevo_cliente_id)
                )
            else:
                self._ejecutar(
                    "INSERT INTO Persona_natural (ID_cliente, Apellido_cliente) VALUES (%s, %s)",
                    (nuevo_cliente_id, apellido)
                )
        
        return resultado

    def eliminar_cliente(self, cliente_id):
        """Elimina un cliente (las tablas hijas se eliminan por CASCADE)"""
        return self._ejecutar("DELETE FROM Cliente WHERE ID_cliente = %s", (cliente_id,))

    def obtener_cliente_completo(self, cliente_id):
        """Obtiene un cliente con información adicional según su tipo"""
        cliente = self.obtener_cliente_por_id(cliente_id)
        if not cliente:
            return None
        return cliente
