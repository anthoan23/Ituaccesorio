from __future__ import annotations
from app.models.database import conectar

class Clientes(conectar):
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


class Persona_natural(Clientes):
    pass


class Cliente_juridico(Clientes):
    def listar_clientes(self):
<<<<<<< Updated upstream
        """Lista todos los clientes (personas naturales) con nombre completo"""
=======
>>>>>>> Stashed changes
        return self._consultar(
            """
            SELECT 
                c.ID_cliente AS id,
                CONCAT(p.Nombre_cliente, ' ', p.Apellido_cliente) AS nombre,
                p.Nombre_cliente AS nombre_solo,
                p.Apellido_cliente AS apellido,
                c.Direccion_cliente AS direccion,
                c.Celular_cliente AS celular,
                c.Correo_cliente AS correo
            FROM Cliente c
<<<<<<< Updated upstream
            INNER JOIN Persona_natural p ON c.ID_cliente = p.ID_cliente
            ORDER BY c.ID_cliente DESC
            """
        )

    def listar_clientes_para_select(self):
        """Lista clientes para usar en selects (solo ID y nombre completo)"""
        return self._consultar(
            """
            SELECT 
                c.ID_cliente AS cedula,
                CONCAT(p.Nombre_cliente, ' ', p.Apellido_cliente) AS nombre_completo,
                p.Nombre_cliente AS nombre,
                p.Apellido_cliente AS apellido
            FROM Cliente c
            INNER JOIN Persona_natural p ON c.ID_cliente = p.ID_cliente
            ORDER BY p.Nombre_cliente ASC
=======
            LEFT JOIN Persona_natural p ON c.ID_cliente = p.ID_cliente
            LEFT JOIN Cliente_juridico j ON c.ID_cliente = j.ID_cliente
            WHERE p.ID_cliente IS NOT NULL OR j.ID_cliente IS NOT NULL
            ORDER BY c.ID_cliente ASC
            """
        )


    def crear_cliente(
        self,
        cliente_id,
        nombre,
        tipo="natural",
        apellido=None,
        rif=None,
        razon_social=None,
        celular=None,
        correo=None,
        direccion=None,
    ):
        """Crea un cliente natural o jurídico usando el ID_cliente para unir las tablas."""
        if not cliente_id or not nombre:
            raise ValueError("ID de cliente y nombre son obligatorios.")

        tipo = (tipo or "natural").strip().lower()
        if tipo == "juridico":
            if not rif or not razon_social:
                raise ValueError("RIF y razón social son obligatorios para cliente jurídico.")
        elif tipo == "natural":
            if not apellido:
                raise ValueError("Apellido es obligatorio para cliente natural.")
        else:
            raise ValueError("Tipo de cliente inválido. Use 'natural' o 'juridico'.")

        resultado = self._ejecutar(
>>>>>>> Stashed changes
            """
        )

<<<<<<< Updated upstream
=======
        if not resultado:
            return None

        if tipo == "natural":
            self._ejecutar(
                """
                INSERT INTO Persona_natural (ID_cliente, Apellido_cliente)
                VALUES (%s, %s)
                """,
                (cliente_id, apellido),
            )
        else:
            self._ejecutar(
                """
                INSERT INTO Cliente_juridico (ID_cliente, Razon_social_cliente, Rif_cliente)
                VALUES (%s, %s, %s)
                """,
                (cliente_id, razon_social, rif),
            )

        return cliente_id









    def crear_cliente_con_id(self, cliente_id, nombre, apellido=None, celular=None, correo=None, direccion=None, tipo=None, rif=None, razon_social=None):
        """Crea un cliente (compatible con la estructura anterior)"""
        return self.crear_cliente(
            cliente_id=cliente_id,
            nombre=nombre,
            tipo=tipo or "natural",
            apellido=apellido,
            rif=rif,
            razon_social=razon_social,
            celular=celular,
            correo=correo,
            direccion=direccion,
        )

>>>>>>> Stashed changes
    def obtener_cliente_por_id(self, cliente_id):
        """Obtiene un cliente por su ID con datos separados"""
        datos = self._consultar(
            """
            SELECT 
                c.ID_cliente AS id,
                p.Nombre_cliente AS nombre,
                p.Apellido_cliente AS apellido,
                CONCAT(p.Nombre_cliente, ' ', p.Apellido_cliente) AS nombre_completo,
                c.Direccion_cliente AS direccion,
                c.Celular_cliente AS celular,
                c.Correo_cliente AS correo
            FROM Cliente c
            INNER JOIN Persona_natural p ON c.ID_cliente = p.ID_cliente
            WHERE c.ID_cliente = %s
            LIMIT 1
            """,
            (cliente_id,),
        )
        return datos[0] if datos else None

    def obtener_nombre_completo(self, cliente_id):
        """Obtiene solo el nombre completo del cliente"""
        datos = self._consultar(
            """
            SELECT CONCAT(p.Nombre_cliente, ' ', p.Apellido_cliente) AS nombre_completo
            FROM Cliente c
            INNER JOIN Persona_natural p ON c.ID_cliente = p.ID_cliente
            WHERE c.ID_cliente = %s
            LIMIT 1
            """,
            (cliente_id,),
        )
        return datos[0]["nombre_completo"] if datos else None

    def crear_cliente(self, cliente_id, nombre, apellido, celular=None, correo=None, direccion=None):
        """Crea un nuevo cliente (persona natural)"""
        
        # Primero insertar en la tabla Cliente
        resultado = self._ejecutar(
            """
            INSERT INTO Cliente (ID_cliente, Direccion_cliente, Celular_cliente, Correo_cliente)
            VALUES (%s, %s, %s, %s)
            """,
            (cliente_id, direccion, celular, correo),
        )
        
        if not resultado:
            return None
        
        # Insertar en Persona_natural
        self._ejecutar(
            """
            INSERT INTO Persona_natural (ID_cliente, Nombre_cliente, Apellido_cliente)
            VALUES (%s, %s, %s)
            """,
            (cliente_id, nombre, apellido)
        )
        
        return cliente_id

    def crear_cliente_con_id(self, cliente_id, nombre, apellido=None, celular=None, correo=None, direccion=None, tipo=None):
        """Crea un cliente (compatible con la estructura anterior)"""
        return self.crear_cliente(cliente_id, nombre, apellido, celular, correo, direccion)

    def actualizar_cliente(self, cliente_id_actual, nuevo_cliente_id, nombre, apellido, celular=None, correo=None, direccion=None, tipo=None):
        """Actualiza un cliente existente"""
        
        # Actualizar tabla Cliente
        self._ejecutar(
            """
            UPDATE Cliente
            SET ID_cliente = %s,
                Direccion_cliente = %s,
                Celular_cliente = %s,
                Correo_cliente = %s
            WHERE ID_cliente = %s
            """,
            (nuevo_cliente_id, direccion, celular, correo, cliente_id_actual),
        )
        
        # Actualizar Persona_natural
        return self._ejecutar(
            """
            UPDATE Persona_natural
            SET Nombre_cliente = %s,
                Apellido_cliente = %s
            WHERE ID_cliente = %s
            """,
            (nombre, apellido, nuevo_cliente_id),
        )

    def eliminar_cliente(self, cliente_id):
        """Elimina un cliente (las tablas hijas se eliminan por CASCADE)"""
        return self._ejecutar("DELETE FROM Cliente WHERE ID_cliente = %s", (cliente_id,))

    def existe_cliente(self, cliente_id):
        """Verifica si un cliente existe"""
        datos = self._consultar(
            "SELECT 1 FROM Cliente WHERE ID_cliente = %s LIMIT 1",
            (cliente_id,)
        )
        return len(datos) > 0

    def obtener_cliente_completo(self, cliente_id):
        """Obtiene un cliente con información adicional según su tipo"""
        cliente = self.obtener_cliente_por_id(cliente_id)
        if not cliente:
            return None
<<<<<<< Updated upstream
        return cliente
=======
        return cliente


GestionClientes = Cliente_juridico

>>>>>>> Stashed changes
