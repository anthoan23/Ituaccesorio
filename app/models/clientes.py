from __future__ import annotations
from app.models.database import conectar

class Clientes():
    def __init__(self, ID_cliente=None, Direccion_cliente=None, Celular_cliente=None, Correo_cliente=None, **kwargs):
        self.ID_cliente = ID_cliente
        self.Direccion_cliente = Direccion_cliente
        self.Celular_cliente = Celular_cliente
        self.Correo_cliente = Correo_cliente
       
        self._conexion_bd = conectar()

    """" Inicio de metodos"""

    def listar_clientes(self):
        db = self._conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    c.ID_cliente AS id,
                    COALESCE(CONCAT(p.Nombre_cliente, ' ', p.Apellido_cliente), j.Razon_social) AS nombre,
                    c.Direccion_cliente AS direccion,
                    c.Celular_cliente AS celular,
                    c.Correo_cliente AS correo,
                    p.Apellido_cliente AS apellido,
                    j.Razon_social AS razon_social,
                    j.Rif_cliente AS rif,
                    CASE
                        WHEN p.ID_cliente IS NOT NULL THEN 'natural'
                        WHEN j.ID_cliente IS NOT NULL THEN 'juridico'
                        ELSE 'natural'
                    END AS tipo
                FROM Cliente c
                LEFT JOIN Persona_natural p ON c.ID_cliente = p.ID_cliente
                LEFT JOIN Cliente_juridico j ON c.ID_cliente = j.ID_cliente
                WHERE p.ID_cliente IS NOT NULL OR j.ID_cliente IS NOT NULL
                ORDER BY c.ID_cliente ASC
                """
            )
            return cursor.fetchall()
        except Exception as e:
            return f"Error en consulta: {e}"
        finally:
            cursor.close()
            db.close()

    def eliminar_cliente(self) -> str:
        Id_cliente = self.ID_cliente.strip()

        #Inicio de validaciones

        if not Id_cliente:
            mensaje = "La cedula del cliente no puede estar vacío."
            return mensaje
        
        if not Id_cliente.isdigit():
            mensaje = "La cedula del cliente debe contener solo números."
            return mensaje
        
        if len(Id_cliente) > 8:
            mensaje = "La cedula del cliente no puede exceder los 8 caracteres."
            return mensaje
    
        #Final de validaciones

        db = self._conexion_bd.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje
        
        cursor = db.cursor()
        try: 
            sql = "DELETE FROM Persona_natural WHERE ID_cliente = %s"
            cursor.execute(sql, (Id_cliente,))
            db.commit()

            sql = "DELETE FROM Cliente_juridico WHERE ID_cliente = %s"
            cursor.execute(sql, (Id_cliente,))
            db.commit()

            sql = "DELETE FROM Cliente WHERE ID_cliente = %s"
            cursor.execute(sql, (Id_cliente,))
            db.commit()
            mensaje = f"El cliente de cédula '{Id_cliente}' ha sido eliminado exitosamente."
            return mensaje
        except Exception as e:
            mensaje = f"Error al eliminar cliente: {e}"
            return mensaje
        finally:
            cursor.close()
            db.close()
        
    """Fin de metodos"""

    """Nuevos métodos añadidos por Eduin"""
    
    def obtener_cliente_por_id(self, cliente_id=None):
        """
        Obtiene un cliente por su ID (cédula para persona natural)
        """
        id_buscar = cliente_id or self.ID_cliente
        if not id_buscar:
            return None
        
        db = self._conexion_bd.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    c.ID_cliente AS id,
                    p.Nombre_cliente AS nombre,
                    p.Apellido_cliente AS apellido,
                    CONCAT(p.Nombre_cliente, ' ', p.Apellido_cliente) AS nombre_completo,
                    c.Direccion_cliente AS direccion,
                    c.Celular_cliente AS celular,
                    c.Correo_cliente AS correo,
                    'natural' AS tipo
                FROM Cliente c
                INNER JOIN Persona_natural p ON c.ID_cliente = p.ID_cliente
                WHERE c.ID_cliente = %s
                LIMIT 1
                """,
                (str(id_buscar),)
            )
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener cliente por ID: {e}")
            return None
        finally:
            cursor.close()
            db.close()
    
    def crear_cliente(self, cliente_id: int, nombre: str, apellido: str, celular: str, 
                      correo: str = None, direccion: str = None) -> bool:
        """
        Crea un nuevo cliente como persona natural(para el login)
        """
        from app.models.clientes import Persona_natural
        
        if not cliente_id or not nombre or not apellido or not celular:
            return False
        
        persona = Persona_natural(
            Cedula_cliente=str(cliente_id),
            Nombre_cliente=nombre,
            Apellido_cliente=apellido,
            Telefono_cliente=celular,
            Correo_cliente=correo,
            Direccion_cliente=direccion
        )
        
        resultado = persona.registrar_persona_natural()
        return "exitosamente" in resultado.lower()
    
    def verificar_cliente_existe(self, cliente_id: int) -> bool:
        """
        Verifica si un cliente existe en la base de datos
        """
        db = self._conexion_bd.conexion1()
        if not db:
            return False
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM Cliente WHERE ID_cliente = %s LIMIT 1",
                (str(cliente_id),)
            )
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error al verificar cliente: {e}")
            return False
        finally:
            cursor.close()
            db.close()
    
    def obtener_datos_cliente_completo(self, cliente_id: int = None):
        """
        Obtiene todos los datos de un cliente incluyendo información específica según su tipo
        """
        id_buscar = cliente_id or self.ID_cliente
        if not id_buscar:
            return None
        
        db = self._conexion_bd.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    c.ID_cliente AS id,
                    c.Direccion_cliente AS direccion,
                    c.Celular_cliente AS celular,
                    c.Correo_cliente AS correo,
                    p.Nombre_cliente AS nombre,
                    p.Apellido_cliente AS apellido,
                    NULL AS razon_social,
                    NULL AS rif,
                    'natural' AS tipo
                FROM Cliente c
                INNER JOIN Persona_natural p ON c.ID_cliente = p.ID_cliente
                WHERE c.ID_cliente = %s
                
                UNION ALL
                
                SELECT
                    c.ID_cliente AS id,
                    c.Direccion_cliente AS direccion,
                    c.Celular_cliente AS celular,
                    c.Correo_cliente AS correo,
                    NULL AS nombre,
                    NULL AS apellido,
                    j.Razon_social AS razon_social,
                    j.Rif_cliente AS rif,
                    'juridico' AS tipo
                FROM Cliente c
                INNER JOIN Cliente_juridico j ON c.ID_cliente = j.ID_cliente
                WHERE c.ID_cliente = %s
                """,
                (str(id_buscar), str(id_buscar))
            )
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener datos completos del cliente: {e}")
            return None
        finally:
            cursor.close()
            db.close()
    
    def listar_clientes_naturales(self):
        """
        Lista solo los clientes personas naturales
        """
        db = self._conexion_bd.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    c.ID_cliente AS cedula,
                    CONCAT(p.Nombre_cliente, ' ', p.Apellido_cliente) AS nombre_completo,
                    p.Nombre_cliente AS nombre,
                    p.Apellido_cliente AS apellido,
                    c.Celular_cliente AS celular,
                    c.Correo_cliente AS correo,
                    c.Direccion_cliente AS direccion
                FROM Cliente c
                INNER JOIN Persona_natural p ON c.ID_cliente = p.ID_cliente
                ORDER BY p.Nombre_cliente ASC
                """
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar clientes naturales: {e}")
            return None
        finally:
            cursor.close()
            db.close()
    
    def actualizar_datos_cliente(self, cliente_id: int, nombre: str = None, apellido: str = None,
                                  celular: str = None, correo: str = None, direccion: str = None) -> str:
        """
        Actualiza los datos de un cliente existente
        """
        if not cliente_id:
            return "El ID del cliente es obligatorio."
        
        db = self._conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."
        
        cursor = db.cursor()
        try:
            # Actualizar tabla Cliente
            if celular or correo or direccion:
                updates = []
                params = []
                
                if celular is not None:
                    updates.append("Celular_cliente = %s")
                    params.append(celular)
                if correo is not None:
                    updates.append("Correo_cliente = %s")
                    params.append(correo)
                if direccion is not None:
                    updates.append("Direccion_cliente = %s")
                    params.append(direccion)
                
                if updates:
                    params.append(str(cliente_id))
                    cursor.execute(
                        f"UPDATE Cliente SET {', '.join(updates)} WHERE ID_cliente = %s",
                        params
                    )
            
            # Actualizar tabla Persona_natural si es persona natural
            if nombre or apellido:
                cursor.execute(
                    "SELECT 1 FROM Persona_natural WHERE ID_cliente = %s",
                    (str(cliente_id),)
                )
                if cursor.fetchone():
                    updates = []
                    params = []
                    
                    if nombre is not None:
                        updates.append("Nombre_cliente = %s")
                        params.append(nombre)
                    if apellido is not None:
                        updates.append("Apellido_cliente = %s")
                        params.append(apellido)
                    
                    if updates:
                        params.append(str(cliente_id))
                        cursor.execute(
                            f"UPDATE Persona_natural SET {', '.join(updates)} WHERE ID_cliente = %s",
                            params
                        )
            
            db.commit()
            return "Cliente actualizado exitosamente."
        except Exception as e:
            db.rollback()
            print(f"Error al actualizar datos del cliente: {e}")
            return f"Error al actualizar cliente: {e}"
        finally:
            cursor.close()
            db.close()
"""Fin de los añadios de Eduin"""
class Persona_natural(Clientes):
    def __init__(
        self,
        Cedula_cliente=None,
        Apellido_cliente=None,
        Nombre_cliente=None,
        Direccion_cliente=None,
        Telefono_cliente=None,
        Correo_cliente=None,
        **kwargs,
    ):
        super().__init__(
            ID_cliente=Cedula_cliente,
            Direccion_cliente=Direccion_cliente,
            Celular_cliente=Telefono_cliente,
            Correo_cliente=Correo_cliente,
        )
        self.Cedula_cliente = Cedula_cliente
        self.Apellido_cliente = Apellido_cliente
        self.Nombre_cliente = Nombre_cliente
        
    """ Inicio de metodos"""

    def registrar_persona_natural(self) -> str:
        cedula = self.Cedula_cliente.strip()
        apellido = self.Apellido_cliente.strip()
        nombre = self.Nombre_cliente.strip()

        #Inicio de validaciones

        if not cedula:
            return "La cédula del cliente no puede estar vacía."
        
        if not apellido:
            return "El apellido del cliente no puede estar vacío."
        
        if not nombre:
            return "El nombre del cliente no puede estar vacío."
        
        if not cedula.isdigit():
            return "La cédula del cliente debe contener solo números."
        
        if len(nombre) > 20:
            return "El nombre del cliente no puede exceder los 20 caracteres."
        
        if len(apellido) > 20:
            return "El apellido del cliente no puede exceder los 20 caracteres."
        
        if len(cedula) > 8:
            return "La cédula del cliente no puede exceder los 8 caracteres."
        
        db = self._conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."
        
        cursor = db.cursor()
        try:
            # Verificar existencia previa del cliente
            cursor.execute("SELECT 1 FROM Cliente WHERE ID_cliente = %s", (cedula,))
            if cursor.fetchone():
                return f"El cliente con cédula '{cedula}' ya existe."

            cursor.execute(
                "INSERT INTO Cliente (ID_cliente, Direccion_cliente, Celular_cliente, Correo_cliente) VALUES (%s, %s, %s, %s)",
                (cedula, self.Direccion_cliente or None, self.Celular_cliente or None, self.Correo_cliente or None)
            )
            cursor.execute(
                "INSERT INTO Persona_natural (ID_cliente, Apellido_cliente, Nombre_cliente) VALUES (%s, %s, %s)",
                (cedula, apellido, nombre)
            )
            db.commit()
            return f"El cliente '{nombre} {apellido}' se registró exitosamente."
        except Exception as e:
            db.rollback()
            return f"Error al registrar cliente: {e}"
        finally:
            cursor.close()
            db.close()
    
    def actualizar_persona_natural(self):
        cedula = self.Cedula_cliente.strip()
        apellido = self.Apellido_cliente.strip()
        nombre = self.Nombre_cliente.strip()

        #Inicio de validaciones

        if not cedula:
            mensaje = "La cédula del cliente no puede estar vacía."
            return mensaje
        
        if not apellido:
            mensaje = "El apellido del cliente no puede estar vacío."
            return mensaje
        
        if not nombre:
            mensaje = "El nombre del cliente no puede estar vacío."
            return mensaje
        
        if not cedula.isdigit():
            mensaje = "La cédula del cliente debe contener solo números."
            return mensaje
        
        if len(nombre) > 20:
            mensaje = "El nombre del cliente no puede exceder los 20 caracteres."
            return mensaje
        
        if len(apellido) > 20:
            mensaje = "El apellido del cliente no puede exceder los 20 caracteres."
            return mensaje
        
        if len(cedula) > 8:
            mensaje = "La cédula del cliente no puede exceder los 8 caracteres."
            return mensaje
        
        #final de validaciones
        
        db = self._conexion_bd.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE Cliente SET Direccion_cliente = %s, Celular_cliente = %s, Correo_cliente = %s WHERE ID_cliente = %s",
                (self.Direccion_cliente or None, self.Celular_cliente or None, self.Correo_cliente or None, cedula)
            )
            cursor.execute(
                "UPDATE Persona_natural SET Nombre_cliente = %s, Apellido_cliente = %s WHERE ID_cliente = %s",
                (nombre, apellido, cedula)
            )
            db.commit()
            mensaje = f"El cliente '{nombre} {apellido}' se actualizó exitosamente."
            return mensaje
        except Exception as e:
            print(f"Error al actualizar cliente: {e}")
            db.rollback()
            return f"Error al actualizar cliente: {e}"
        finally:
            cursor.close()
            db.close()

    """Fin de metodos"""


class Cliente_juridico(Clientes):
    def __init__(
        self,
        Id_cliente=None,
        Razon_social=None,
        Rif_cliente=None,
        RIF=None,
        Direccion_cliente=None,
        Telefono_cliente=None,
        Correo_cliente=None,
        **kwargs,
    ):
        codigo = Id_cliente or Rif_cliente or RIF
        super().__init__(
            ID_cliente=codigo,
            Direccion_cliente=Direccion_cliente,
            Celular_cliente=Telefono_cliente,
            Correo_cliente=Correo_cliente,
        )
        self.Id_cliente = codigo
        self.Razon_social = Razon_social
        self.Rif_cliente = Rif_cliente or RIF
       
    """ Inicio de metodos"""

    def registrar_cliente_juridico(self) -> str:
        razon_social = self.Razon_social.strip()
        rif = self.Rif_cliente.strip()

        #Inicio de validaciones
        
        if not razon_social:
            return "La razón social del cliente no puede estar vacía."
        
        if len(razon_social) > 50:
            return "La razón social del cliente no puede exceder los 50 caracteres."
        
        if not rif:
            return "El RIF del cliente no puede estar vacío."
        
        if not rif.isalnum():
            return "El RIF del cliente debe contener solo caracteres alfanuméricos."
        
        if len(rif) > 9:
            return "El RIF del cliente no puede exceder los 9 caracteres."
 
        db = self._conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute("SELECT 1 FROM Cliente WHERE ID_cliente = %s", (rif,))
            if cursor.fetchone():
                return f"El cliente jurídico con RIF '{rif}' ya existe."

            cursor.execute(
                "INSERT INTO Cliente (ID_cliente, Direccion_cliente, Celular_cliente, Correo_cliente) VALUES (%s, %s, %s, %s)",
                (rif, self.Direccion_cliente or None, self.Celular_cliente or None, self.Correo_cliente or None)
            )
            cursor.execute(
                "INSERT INTO Cliente_juridico (ID_cliente, Razon_social, Rif_cliente) VALUES (%s, %s, %s)",
                (rif, razon_social, rif)
            )
            db.commit()
            return f"El cliente jurídico '{razon_social}' se registró exitosamente."
        except Exception as e:
            db.rollback()
            return f"Error al registrar cliente jurídico: {e}"
        finally:
            cursor.close()
            db.close()

    def actualizar_cliente_juridico(self):
        razon_social = self.Razon_social.strip()
        rif = self.Rif_cliente.strip()

        #Inicio de validaciones
        
        if not razon_social:
            mensaje = "La razón social del cliente no puede estar vacía."
            return mensaje
        
        if len(razon_social) > 50:
            mensaje = "La razón social del cliente no puede exceder los 50 caracteres."
            return mensaje
        
        if not rif:
            mensaje = "El RIF del cliente no puede estar vacío."
            return mensaje
        
        if not rif.isalnum():
            mensaje = "El RIF del cliente debe contener solo caracteres alfanuméricos."
            return mensaje
        
        if len(rif) > 9:
            mensaje = "El RIF del cliente no puede exceder los 9 caracteres."
            return mensaje
 
        #Final de validaciones

        db = self._conexion_bd.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje

        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE Cliente SET Direccion_cliente = %s, Celular_cliente = %s, Correo_cliente = %s WHERE ID_cliente = %s",
                (self.Direccion_cliente or None, self.Celular_cliente or None, self.Correo_cliente or None, rif)
            )
            cursor.execute(
                "UPDATE Cliente_juridico SET Razon_social = %s, Rif_cliente = %s WHERE ID_cliente = %s",
                (razon_social, rif, rif)
            )
            db.commit()
            mensaje = f"El cliente jurídico '{razon_social}' se actualizó exitosamente."
            return mensaje
        except Exception as e:
            print(f"Error al actualizar cliente jurídico: {e}")
            db.rollback()
            return f"Error al actualizar cliente jurídico: {e}"
        finally:
            cursor.close()
            db.close()

    """Fin de metodos"""