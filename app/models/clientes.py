from __future__ import annotations
from app.models.database import conectar

class Clientes():
    def __init__(self, ID_cliente=None, Direccion_cliente=None, Celular_cliente=None, Correo_cliente=None, **kwargs):
        self.ID_cliente = ID_cliente
        self.Direccion_cliente = Direccion_cliente
        self.Celular_cliente = Celular_cliente
        self.Correo_cliente = Correo_cliente
       
        self.__conexion_bd = conectar()

    """" Inicio de metodos"""

    def listar_clientes(self):
        db = self.__conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    c.ID_cliente AS id,
                    c.Nombre_cliente AS nombre,
                    c.Direccion_cliente AS direccion,
                    c.Celular_cliente AS celular,
                    c.Correo_cliente AS correo,
                    p.Apellido_cliente AS apellido,
                    j.Razon_social_cliente AS razon_social,
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

    def obtener_cliente_por_id(self, id_cliente):
        if not id_cliente:
            return None

        db = self.__conexion_bd.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    c.ID_cliente AS id,
                    c.Nombre_cliente AS nombre,
                    c.Direccion_cliente AS direccion,
                    c.Celular_cliente AS celular,
                    c.Correo_cliente AS correo,
                    p.Apellido_cliente AS apellido,
                    j.Razon_social_cliente AS razon_social,
                    j.Rif_cliente AS rif,
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
                (id_cliente,)
            )
            return cursor.fetchone()
        except Exception:
            return None
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

        db = self.__conexion_bd.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje
        
        cursor = db.cursor()
        try:
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

        db = self.__conexion_bd.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje
        
        cursor = db.cursor()
        try: 
            sql = 'CALL Crear_cliente_natural(%s, %s, %s)'
            cursor.execute(sql, (cedula, nombre, apellido))
            while cursor.nextset():
                pass
            db.commit()
            mensaje = f"El cliente '{nombre} {apellido}' se registrado exitosamente."
            return mensaje
        except Exception as e:
            mensaje = f"Error al registrar cliente: {e}"
            return mensaje 
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
        
        db = self.__conexion_bd.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje
        
        cursor = db.cursor()
        try:
            sql = """
            UPDATE Cliente
            SET Nombre_cliente = %s
            WHERE ID_cliente = %s
            """
            cursor.execute(sql, (f"{nombre} {apellido}", cedula))
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

        db = self.__conexion_bd.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje

        cursor = db.cursor()
        try:
            sql = 'CALL Crear_cliente_juridico(%s, %s)'
            cursor.execute(sql, (razon_social, rif))
            while cursor.nextset():
                pass
            db.commit()
            mensaje = f"El cliente jurídico '{razon_social}' se registró exitosamente."
            return mensaje
        except Exception as e:
            mensaje = f"Error al registrar cliente jurídico: {e}"
            return mensaje
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

        db = self.__conexion_bd.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje

        cursor = db.cursor()
        try:
            sql = """
            UPDATE Cliente
            SET Nombre_cliente = %s
            WHERE ID_cliente = %s
            """
            cursor.execute(sql, (razon_social, rif))
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


class GestionClientes(Clientes):
    """Compatibilidad con controladores que importan GestionClientes."""
    pass
