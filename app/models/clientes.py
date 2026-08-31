from __future__ import annotations
from app.models.database import conectar
from app.models.bitacora import Bitacora
import re


class Clientes():
    def __init__(self, ID_cliente=None, Direccion_cliente=None, Celular_cliente=None, 
                 Correo_cliente=None, usuario_id: str = None, **kwargs):
        self.ID_cliente = ID_cliente
        self.Direccion_cliente = Direccion_cliente
        self.Celular_cliente = Celular_cliente
        self.Correo_cliente = Correo_cliente
        self.usuario_id = usuario_id
       
        self._conexion_bd = conectar()

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
                    p.Nombre_cliente AS nombre,
                    c.Direccion_cliente AS direccion,
                    c.Celular_cliente AS celular,
                    c.Correo_cliente AS correo,
                    p.Apellido_cliente AS apellido,
                    j.Razon_social AS razon_social,
                    j.Rif_cliente AS rif,
                    c.Celular_cliente AS telefono,
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

        if not Id_cliente:
            return "El ID del cliente no puede estar vacío."
        
        es_rif = bool(re.search(r'[A-Za-z-]', Id_cliente))
        
        if es_rif:
            patron_rif = r'^[JE]-\d{8}-\d$'
            if not re.match(patron_rif, Id_cliente):
                return "El RIF debe tener el formato: J-12345678-9 o E-12345678-9"
        else:
            if not Id_cliente.isdigit():
                return "La cédula del cliente debe contener solo números."
            if len(Id_cliente) < 7 or len(Id_cliente) > 8:
                return "La cédula del cliente debe tener 7 u 8 caracteres."

        db = self._conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."
        
        cursor = db.cursor()
        try:
            nombre_cliente = Id_cliente
            cursor.execute(
                "SELECT CONCAT(p.Nombre_cliente, ' ', p.Apellido_cliente) as nombre FROM Persona_natural p WHERE p.ID_cliente = %s",
                (Id_cliente,)
            )
            row = cursor.fetchone()
            if row:
                nombre_cliente = row[0]
            else:
                cursor.execute(
                    "SELECT Razon_social FROM Cliente_juridico WHERE ID_cliente = %s",
                    (Id_cliente,)
                )
                row = cursor.fetchone()
                if row:
                    nombre_cliente = row[0]

            cursor.execute("SELECT ID_factura FROM Venta WHERE ID_cliente = %s", (Id_cliente,))
            ventas = cursor.fetchall()
            
            for venta in ventas:
                factura_id = venta[0]
                cursor.execute("DELETE FROM Metodo_pago WHERE ID_factura = %s", (factura_id,))
                db.commit()
                cursor.execute("DELETE FROM Detalle_venta WHERE ID_factura = %s", (factura_id,))
                db.commit()
            
            cursor.execute("""
                DELETE fti FROM Fotos_trade_in fti 
                INNER JOIN Trade_in t ON fti.ID_Trade_in = t.ID_Trade_in 
                WHERE t.ID_cliente = %s
            """, (Id_cliente,))
            db.commit()
            
            cursor.execute("""
                DELETE fos FROM Fotos_orden_servicio fos 
                INNER JOIN Orden_servicio os ON fos.ID_orden_servicio = os.ID_orden_servicio 
                WHERE os.ID_cliente = %s
            """, (Id_cliente,))
            db.commit()
            
            cursor.execute("""
                DELETE tri FROM Test_realizados_interaccion tri 
                INNER JOIN Interaccion i ON tri.ID_interaccion = i.ID_interaccion 
                INNER JOIN Orden_servicio os ON i.ID_orden_servicio = os.ID_orden_servicio 
                WHERE os.ID_cliente = %s
            """, (Id_cliente,))
            db.commit()
            
            cursor.execute("""
                DELETE trti FROM Test_realizados_trade_in trti 
                INNER JOIN Trade_in t ON trti.ID_Trade_in = t.ID_Trade_in 
                WHERE t.ID_cliente = %s
            """, (Id_cliente,))
            db.commit()
            
            cursor.execute("""
                DELETE t FROM Test t 
                INNER JOIN Test_realizados_interaccion tri ON t.ID_test = tri.ID_test 
                INNER JOIN Interaccion i ON tri.ID_interaccion = i.ID_interaccion 
                INNER JOIN Orden_servicio os ON i.ID_orden_servicio = os.ID_orden_servicio 
                WHERE os.ID_cliente = %s
            """, (Id_cliente,))
            db.commit()
            
            cursor.execute("""
                DELETE t FROM Test t 
                INNER JOIN Test_realizados_trade_in trti ON t.ID_test = trti.ID_test 
                INNER JOIN Trade_in tr ON trti.ID_Trade_in = tr.ID_Trade_in 
                WHERE tr.ID_cliente = %s
            """, (Id_cliente,))
            db.commit()
            
            cursor.execute("""
                DELETE i FROM Interaccion i 
                INNER JOIN Orden_servicio os ON i.ID_orden_servicio = os.ID_orden_servicio 
                WHERE os.ID_cliente = %s
            """, (Id_cliente,))
            db.commit()
            
            cursor.execute("""
                DELETE ru FROM Repuestos_usados ru 
                INNER JOIN Orden_servicio os ON ru.ID_orden_servicio = os.ID_orden_servicio 
                WHERE os.ID_cliente = %s
            """, (Id_cliente,))
            db.commit()
            
            cursor.execute("""
                DELETE ps FROM Pago_servicio ps 
                INNER JOIN Orden_servicio os ON ps.ID_orden_servicio = os.ID_orden_servicio 
                WHERE os.ID_cliente = %s
            """, (Id_cliente,))
            db.commit()
            
            cursor.execute("DELETE FROM Lista_compra WHERE ID_cliente = %s", (Id_cliente,))
            db.commit()
            cursor.execute("DELETE FROM Trade_in WHERE ID_cliente = %s", (Id_cliente,))
            db.commit()
            cursor.execute("DELETE FROM Orden_servicio WHERE ID_cliente = %s", (Id_cliente,))
            db.commit()
            cursor.execute("DELETE FROM Venta WHERE ID_cliente = %s", (Id_cliente,))
            db.commit()
            cursor.execute("DELETE FROM Persona_natural WHERE ID_cliente = %s", (Id_cliente,))
            db.commit()
            cursor.execute("DELETE FROM Cliente_juridico WHERE ID_cliente = %s", (Id_cliente,))
            db.commit()
            cursor.execute("DELETE FROM Cliente WHERE ID_cliente = %s", (Id_cliente,))
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Eliminar cliente",
                    descripcion=f"Se eliminó el cliente ID: {Id_cliente} - Nombre: {nombre_cliente}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Clientes"
                )
                bitacora.registrar()
            
            return f"El cliente '{nombre_cliente}' con ID '{Id_cliente}' ha sido eliminado exitosamente."
        except Exception as e:
            db.rollback()
            if "foreign key constraint fails" in str(e).lower():
                match = re.search(r'FOREIGN KEY \(`(\w+)`\) REFERENCES `(\w+)`', str(e))
                if match:
                    columna = match.group(1)
                    tabla = match.group(2)
                    return f"No se puede eliminar el cliente porque tiene registros relacionados en la tabla '{tabla}' (columna '{columna}')."
                else:
                    return "No se puede eliminar el cliente porque tiene registros relacionados en otras tablas."
            else:
                return f"Error al eliminar cliente: {e}"
        finally:
            cursor.close()
            db.close()

    def obtener_cliente_por_id(self, cliente_id=None):
        """
        Obtiene un cliente por su ID (cédula para persona natural)
        """
        id_buscar = cliente_id or self.ID_cliente
        if not id_buscar:
            return None
        
        id_buscar = str(id_buscar).strip()
        
        # Normalizar para búsqueda
        if re.search(r'[A-Za-z]', id_buscar):
            id_buscar_sin_guiones = id_buscar.replace("-", "").upper()
            id_buscar_con_guiones = id_buscar
        else:
            id_buscar_sin_guiones = id_buscar
            id_buscar_con_guiones = id_buscar
        
        db = self._conexion_bd.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            # Buscar primero en Persona_natural
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
                WHERE c.ID_cliente = %s OR c.ID_cliente = %s
                LIMIT 1
                """,
                (id_buscar_sin_guiones, id_buscar_con_guiones)
            )
            resultado = cursor.fetchone()
            
            if resultado:
                return resultado
            
            # Si no es persona natural, buscar en Cliente_juridico
            cursor.execute(
                """
                SELECT
                    c.ID_cliente AS id,
                    j.Razon_social AS razon_social,
                    j.Rif_cliente AS rif,
                    c.Direccion_cliente AS direccion,
                    c.Celular_cliente AS celular,
                    c.Correo_cliente AS correo,
                    'juridico' AS tipo
                FROM Cliente c
                INNER JOIN Cliente_juridico j ON c.ID_cliente = j.ID_cliente
                WHERE c.ID_cliente = %s OR c.ID_cliente = %s
                   OR j.Rif_cliente = %s OR j.Rif_cliente = %s
                LIMIT 1
                """,
                (id_buscar_sin_guiones, id_buscar_con_guiones, id_buscar_con_guiones, id_buscar_sin_guiones)
            )
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener cliente por ID: {e}")
            return None
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
        
        id_buscar = str(id_buscar).strip()
        
        # Normalizar para búsqueda
        if re.search(r'[A-Za-z]', id_buscar):
            id_buscar_sin_guiones = id_buscar.replace("-", "").upper()
            id_buscar_con_guiones = id_buscar
        else:
            id_buscar_sin_guiones = id_buscar
            id_buscar_con_guiones = id_buscar
        
        db = self._conexion_bd.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            # ============================================
            # PRIMERO: Buscar en la tabla Cliente
            # ============================================
            # Intentar primero con el ID con guiones (formato original)
            cursor.execute(
                "SELECT * FROM Cliente WHERE ID_cliente = %s",
                (id_buscar_con_guiones,)
            )
            cliente_base = cursor.fetchone()
            
            # Si no se encuentra, intentar sin guiones
            if not cliente_base:
                cursor.execute(
                    "SELECT * FROM Cliente WHERE ID_cliente = %s",
                    (id_buscar_sin_guiones,)
                )
                cliente_base = cursor.fetchone()
            
            # Si aún no se encuentra, buscar en Rif_cliente de Cliente_juridico
            if not cliente_base and re.search(r'[A-Za-z]', id_buscar):
                cursor.execute(
                    """
                    SELECT c.* FROM Cliente c
                    INNER JOIN Cliente_juridico j ON c.ID_cliente = j.ID_cliente
                    WHERE j.Rif_cliente = %s OR j.Rif_cliente = %s
                    """,
                    (id_buscar_con_guiones, id_buscar_sin_guiones)
                )
                cliente_base = cursor.fetchone()
            
            if not cliente_base:
                return None
            
            cliente_id_real = cliente_base["ID_cliente"]
            
            # ============================================
            # SEGUNDO: Verificar si es Persona Natural
            # ============================================
            cursor.execute(
                "SELECT Nombre_cliente, Apellido_cliente FROM Persona_natural WHERE ID_cliente = %s",
                (cliente_id_real,)
            )
            persona = cursor.fetchone()
            
            if persona:
                return {
                    "id": str(cliente_base["ID_cliente"]),
                    "direccion": cliente_base.get("Direccion_cliente"),
                    "celular": cliente_base.get("Celular_cliente"),
                    "correo": cliente_base.get("Correo_cliente"),
                    "nombre": persona.get("Nombre_cliente"),
                    "apellido": persona.get("Apellido_cliente"),
                    "razon_social": None,
                    "rif": None,
                    "tipo": "natural"
                }
            
            # ============================================
            # TERCERO: Verificar si es Cliente Jurídico
            # ============================================
            cursor.execute(
                "SELECT Razon_social, Rif_cliente FROM Cliente_juridico WHERE ID_cliente = %s",
                (cliente_id_real,)
            )
            juridico = cursor.fetchone()
            
            if juridico:
                return {
                    "id": str(cliente_base["ID_cliente"]),
                    "direccion": cliente_base.get("Direccion_cliente"),
                    "celular": cliente_base.get("Celular_cliente"),
                    "correo": cliente_base.get("Correo_cliente"),
                    "nombre": None,
                    "apellido": None,
                    "razon_social": juridico.get("Razon_social"),
                    "rif": juridico.get("Rif_cliente"),
                    "tipo": "juridico"
                }
            
            # ============================================
            # CUARTO: Si no tiene tipo específico
            # ============================================
            return {
                "id": str(cliente_base["ID_cliente"]),
                "direccion": cliente_base.get("Direccion_cliente"),
                "celular": cliente_base.get("Celular_cliente"),
                "correo": cliente_base.get("Correo_cliente"),
                "nombre": None,
                "apellido": None,
                "razon_social": None,
                "rif": None,
                "tipo": "desconocido"
            }
        except Exception as e:
            print(f"Error al obtener datos completos del cliente: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            cursor.close()
            db.close()
    
    def crear_cliente(self, cliente_id: int, nombre: str, apellido: str, celular: str, 
                      correo: str = None, direccion: str = None) -> bool:
        from app.models.clientes import Persona_natural
        
        if not cliente_id or not nombre or not apellido or not celular:
            return False
        
        persona = Persona_natural(
            Cedula_cliente=str(cliente_id),
            Nombre_cliente=nombre,
            Apellido_cliente=apellido,
            Telefono_cliente=celular,
            Correo_cliente=correo,
            Direccion_cliente=direccion,
            usuario_id=self.usuario_id
        )
        
        resultado = persona.registrar_persona_natural()
        return "exitosamente" in resultado.lower()
    
    def verificar_cliente_existe(self, cliente_id: int) -> bool:
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
    
    def listar_clientes_naturales(self):
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
        if not cliente_id:
            return "El ID del cliente es obligatorio."
        
        db = self._conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."
        
        cursor = db.cursor()
        try:
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
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Actualizar cliente",
                    descripcion=f"Se actualizó el cliente ID: {cliente_id}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Clientes"
                )
                bitacora.registrar()
            
            return "Cliente actualizado exitosamente."
        except Exception as e:
            db.rollback()
            print(f"Error al actualizar datos del cliente: {e}")
            return f"Error al actualizar cliente: {e}"
        finally:
            cursor.close()
            db.close()


class Persona_natural(Clientes):
    def __init__(
        self,
        Cedula_cliente=None,
        Apellido_cliente=None,
        Nombre_cliente=None,
        Direccion_cliente=None,
        Telefono_cliente=None,
        Correo_cliente=None,
        usuario_id: str = None,
        **kwargs,
    ):
        super().__init__(
            ID_cliente=Cedula_cliente,
            Direccion_cliente=Direccion_cliente,
            Celular_cliente=Telefono_cliente,
            Correo_cliente=Correo_cliente,
            usuario_id=usuario_id,
        )
        self.Cedula_cliente = Cedula_cliente
        self.Apellido_cliente = Apellido_cliente
        self.Nombre_cliente = Nombre_cliente

    def registrar_persona_natural(self) -> str:
        cedula = self.Cedula_cliente.strip()
        apellido = self.Apellido_cliente.strip()
        nombre = self.Nombre_cliente.strip()

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
        if len(cedula) < 7 or len(cedula) > 8:
            return "La cédula del cliente debe tener 7 u 8 caracteres."
        # Validar correo máximo 120 caracteres
        if self.Correo_cliente and len(self.Correo_cliente) > 120:
            return "El correo electrónico no puede exceder los 120 caracteres."
        # Validar dirección máximo 40 caracteres
        if self.Direccion_cliente and len(self.Direccion_cliente) > 40:
            return "La dirección no puede exceder los 40 caracteres."
        
        db = self._conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."
        
        cursor = db.cursor()
        try:
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
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Registrar cliente natural",
                    descripcion=f"Se registró el cliente natural: {cedula} - {nombre} {apellido}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Clientes"
                )
                bitacora.registrar()
            
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
        if len(cedula) < 7 or len(cedula) > 8:
            return "La cédula del cliente debe tener 7 u 8 caracteres."
        # Validar correo máximo 120 caracteres
        if self.Correo_cliente and len(self.Correo_cliente) > 120:
            return "El correo electrónico no puede exceder los 120 caracteres."
        # Validar dirección máximo 40 caracteres
        if self.Direccion_cliente and len(self.Direccion_cliente) > 40:
            return "La dirección no puede exceder los 40 caracteres."
        
        db = self._conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."
        
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
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Actualizar cliente natural",
                    descripcion=f"Se actualizó el cliente natural: {cedula} - {nombre} {apellido}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Clientes"
                )
                bitacora.registrar()
            
            return f"El cliente '{nombre} {apellido}' se actualizó exitosamente."
        except Exception as e:
            print(f"Error al actualizar cliente: {e}")
            db.rollback()
            return f"Error al actualizar cliente: {e}"
        finally:
            cursor.close()
            db.close()


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
        usuario_id: str = None,
        **kwargs,
    ):
        codigo = Id_cliente or Rif_cliente or RIF
        super().__init__(
            ID_cliente=codigo,
            Direccion_cliente=Direccion_cliente,
            Celular_cliente=Telefono_cliente,
            Correo_cliente=Correo_cliente,
            usuario_id=usuario_id,
        )
        self.Id_cliente = codigo
        self.Razon_social = Razon_social
        self.Rif_cliente = Rif_cliente or RIF

    def registrar_cliente_juridico(self) -> str:
        razon_social = self.Razon_social.strip()
        rif = self.Rif_cliente.strip()
        
        patron_rif = r'^[JE]-\d{8}-\d$'
        if not re.match(patron_rif, rif):
            return "El RIF debe tener el formato: J-12345678-9 o E-12345678-9"
        
        if not razon_social:
            return "La razón social del cliente no puede estar vacía."
        
        patron_razon_social = r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\.\-&]+$'
        if not re.match(patron_razon_social, razon_social):
            return "La razón social solo puede contener letras, números, puntos, guiones, espacios y &."
        
        if len(razon_social) > 60:
            return "La razón social del cliente no puede exceder los 60 caracteres."
        if len(rif) != 12:
            return f"El RIF debe tener exactamente 12 caracteres (actual: {len(rif)})"
        if not self.Celular_cliente:
            return "El teléfono del cliente es obligatorio."
        if not re.match(r"^\d{11}$", self.Celular_cliente):
            return "El teléfono debe tener exactamente 11 dígitos numéricos."
        # Validar correo máximo 120 caracteres
        if self.Correo_cliente and len(self.Correo_cliente) > 120:
            return "El correo electrónico no puede exceder los 120 caracteres."
        # Validar dirección máximo 40 caracteres
        if self.Direccion_cliente and len(self.Direccion_cliente) > 40:
            return "La dirección no puede exceder los 40 caracteres."
        if self.Correo_cliente and not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", self.Correo_cliente):
            return "El correo electrónico no es válido."

        db = self._conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            # Guardar el RIF con guiones como ID_cliente
            rif_guardar = rif
            
            # Verificar si ya existe
            cursor.execute("SELECT 1 FROM Cliente WHERE ID_cliente = %s", (rif_guardar,))
            if cursor.fetchone():
                return f"El cliente jurídico con RIF '{rif}' ya existe."

            cursor.execute(
                "INSERT INTO Cliente (ID_cliente, Direccion_cliente, Celular_cliente, Correo_cliente) VALUES (%s, %s, %s, %s)",
                (rif_guardar, self.Direccion_cliente or None, self.Celular_cliente or None, self.Correo_cliente or None)
            )
            cursor.execute(
                "INSERT INTO Cliente_juridico (ID_cliente, Razon_social, Rif_cliente) VALUES (%s, %s, %s)",
                (rif_guardar, razon_social, rif_guardar)
            )
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Registrar cliente jurídico",
                    descripcion=f"Se registró el cliente jurídico: {rif_guardar} - {razon_social}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Clientes"
                )
                bitacora.registrar()
            
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
        
        patron_rif = r'^[JE]-\d{8}-\d$'
        if not re.match(patron_rif, rif):
            return "El RIF debe tener el formato: J-12345678-9 o E-12345678-9"

        if not razon_social:
            return "La razón social del cliente no puede estar vacía."
        
        patron_razon_social = r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\.\-&]+$'
        if not re.match(patron_razon_social, razon_social):
            return "La razón social solo puede contener letras, números, puntos, guiones, espacios y &."
        
        if len(razon_social) > 60:
            return "La razón social del cliente no puede exceder los 60 caracteres."
        if not rif:
            return "El RIF del cliente no puede estar vacío."
        if len(rif) != 12:
            return f"El RIF debe tener exactamente 12 caracteres (actual: {len(rif)})"
        if self.Celular_cliente and not re.match(r"^\d{11}$", self.Celular_cliente):
            return "El teléfono debe tener exactamente 11 dígitos numéricos."
        # Validar correo máximo 120 caracteres
        if self.Correo_cliente and len(self.Correo_cliente) > 120:
            return "El correo electrónico no puede exceder los 120 caracteres."
        # Validar dirección máximo 40 caracteres
        if self.Direccion_cliente and len(self.Direccion_cliente) > 40:
            return "La dirección no puede exceder los 40 caracteres."
        if self.Correo_cliente and not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", self.Correo_cliente):
            return "El correo electrónico no es válido."

        db = self._conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            rif_guardar = rif
            
            cursor.execute(
                "UPDATE Cliente SET Direccion_cliente = %s, Celular_cliente = %s, Correo_cliente = %s WHERE ID_cliente = %s",
                (self.Direccion_cliente or None, self.Celular_cliente or None, self.Correo_cliente or None, rif_guardar)
            )
            cursor.execute(
                "UPDATE Cliente_juridico SET Razon_social = %s, Rif_cliente = %s WHERE ID_cliente = %s",
                (razon_social, rif_guardar, rif_guardar)
            )
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Actualizar cliente jurídico",
                    descripcion=f"Se actualizó el cliente jurídico: {rif_guardar} - {razon_social}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Clientes"
                )
                bitacora.registrar()
            
            return f"El cliente jurídico '{razon_social}' se actualizó exitosamente."
        except Exception as e:
            print(f"Error al actualizar cliente jurídico: {e}")
            db.rollback()
            return f"Error al actualizar cliente jurídico: {e}"
        finally:
            cursor.close()
            db.close()