from app.models.database import conectar


class GestionClientes(conectar):
    def _consultar(self, query, params=None):
        db = self.conexion1()  # conexion1 apunta a itucaccesoriobd
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
        db = self.conexion1()  # conexion1 apunta a itucaccesoriobd
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
        """Lista todos los clientes"""
        return self._consultar(
            """
            SELECT
                ID_cliente AS id,
                Nombre_cliente AS nombre,
                Direccion_cliente AS direccion,
                Celular_cliente AS celular,
                Correo_cliente AS correo
            FROM Cliente
            ORDER BY ID_cliente DESC
            """
        )

    def obtener_cliente_por_id(self, cliente_id):
        """Obtiene un cliente por su ID"""
        datos = self._consultar(
            """
            SELECT
                ID_cliente AS id,
                Nombre_cliente AS nombre,
                Direccion_cliente AS direccion,
                Celular_cliente AS celular,
                Correo_cliente AS correo
            FROM Cliente
            WHERE ID_cliente = %s
            LIMIT 1
            """,
            (cliente_id,),
        )
        return datos[0] if datos else None

    def crear_cliente(self, cliente_id, nombre, celular=None, correo=None, direccion=None):
        """Crea un nuevo cliente (persona natural o jurídica según el ID)"""
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
        
        # Determinar si es persona natural o jurídica basado en el ID
        # Si el ID es numérico (solo números), es persona natural
        # Si tiene letras, es jurídico
        if str(cliente_id).isdigit():
            self._ejecutar(
                """
                INSERT INTO Persona_natural (ID_cliente, Cedula_persona)
                VALUES (%s, %s)
                """,
                (cliente_id, cliente_id)
            )
        else:
            # Para cliente jurídico, usar Razon_social = nombre
            self._ejecutar(
                """
                INSERT INTO Cliente_juridico (ID_cliente, Razon_social)
                VALUES (%s, %s)
                """,
                (cliente_id, nombre)
            )
        
        return cliente_id

    def crear_cliente_con_id(self, cliente_id, nombre, apellido=None, celular=None, correo=None, direccion=None, tipo=None):
        """Crea un cliente (compatible con la estructura anterior)
        Nota: La tabla Cliente no tiene campos separados para nombre/apellido
        así que concatenamos nombre y apellido"""
        
        nombre_completo = nombre
        if apellido:
            nombre_completo = f"{nombre} {apellido}"
        
        return self.crear_cliente(cliente_id, nombre_completo, celular, correo, direccion)

    def actualizar_cliente(self, cliente_id_actual, nuevo_cliente_id, nombre, apellido=None, celular=None, correo=None, direccion=None, tipo=None):
        """Actualiza un cliente existente"""
        nombre_completo = nombre
        if apellido:
            nombre_completo = f"{nombre} {apellido}"
        
        return self._ejecutar(
            """
            UPDATE Cliente
            SET ID_cliente = %s,
                Nombre_cliente = %s,
                Direccion_cliente = %s,
                Celular_cliente = %s,
                Correo_cliente = %s
            WHERE ID_cliente = %s
            """,
            (nuevo_cliente_id, nombre_completo, direccion, celular, correo, cliente_id_actual),
        )

    def eliminar_cliente(self, cliente_id):
        """Elimina un cliente (las tablas hijas se eliminan por CASCADE)"""
        return self._ejecutar("DELETE FROM Cliente WHERE ID_cliente = %s", (cliente_id,))

    def obtener_cliente_completo(self, cliente_id):
        """Obtiene un cliente con información adicional según su tipo"""
        cliente = self.obtener_cliente_por_id(cliente_id)
        if not cliente:
            return None
        
        # Verificar si es persona natural
        persona = self._consultar(
            "SELECT Cedula_persona FROM Persona_natural WHERE ID_cliente = %s",
            (cliente_id,)
        )
        
        if persona:
            cliente['tipo'] = 'natural'
            cliente['cedula'] = persona[0]['Cedula_persona']
            return cliente
        
        # Verificar si es jurídico
        juridico = self._consultar(
            "SELECT Razon_social FROM Cliente_juridico WHERE ID_cliente = %s",
            (cliente_id,)
        )
        
        if juridico:
            cliente['tipo'] = 'juridico'
            cliente['razon_social'] = juridico[0]['Razon_social']
        
        return cliente