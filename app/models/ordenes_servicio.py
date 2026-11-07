from __future__ import annotations
from app.utils.validators import validar_texto_numero
from app.models.database import conectar
from datetime import datetime
import re


class Orden_servicio():
    def __init__(self, ID_orden_servicio: int = None, Estado_orden_servicio: str = None, Descripcion_reparacion: str = None, Costo_reparacion: float = None, Nota_orden_servicio: str = None, Fecha_entrada = None, Fecha_salida = None, ID_foto_orden_servicio: str = None, Foto_orden_servicio = None, ID_empleado: int = None, lista_repuestos=None):
        self.ID_orden_servicio = ID_orden_servicio
        self.Estado_orden_servicio = Estado_orden_servicio
        self.Descripcion_reparacion = Descripcion_reparacion
        self.Costo_reparacion = Costo_reparacion
        self.Nota_orden_servicio = Nota_orden_servicio
        self.ID_empleado = ID_empleado
        self.Fecha_entrada = Fecha_entrada
        self.Fecha_salida = Fecha_salida
        self.ID_foto_orden_servicio = ID_foto_orden_servicio
        self.Foto_orden_servicio = Foto_orden_servicio
        self.lista_repuestos = lista_repuestos

        self._conexion = conectar()

    # ============================================
    # MÉTODOS DE VALIDACIÓN (Lógica en el modelo)
    # ============================================
    @staticmethod
    def _validar_email(email):
        if not email:
            return None
        patron = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(patron, email):
            return "El correo electrónico no es válido."
        return None

    @staticmethod
    def _validar_rif(rif):
        if not rif:
            return "El RIF es obligatorio."
        rif_limpio = rif.replace("-", "").upper()
        if not re.match(r'^[JE]\d{9}$', rif_limpio):
            return "El RIF debe tener el formato J-12345678-9 o E-12345678-9."
        return None

    # ============================================

    def listar_modelos_telefonos(self) -> list:
        db = self._conexion.conexion1()
        if not db:
            print("[ERROR] Error al conectar con la base de datos.")
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    p.ID_producto AS id,
                    p.Nombre_producto AS nombre,
                    cp.Nombre_Clase AS clase_nombre
                FROM Producto p
                INNER JOIN Clase_producto cp ON p.ID_Clase = cp.ID_Clase
                WHERE cp.Nombre_Clase LIKE '%Telefono%' 
                   OR cp.ID_Clase = '1'
                ORDER BY p.Nombre_producto
            """)
            modelos = cursor.fetchall()
            print(f"[DEBUG] Modelos de teléfonos encontrados: {len(modelos)}")
            return modelos
        except Exception as e:
            print(f"[ERROR] Error al listar modelos de teléfonos: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def listar_ordenes_servicio(self):
        db = self._conexion.conexion1()
        if not db:
            return "Error al conectar con la base de datos."
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    os.ID_orden_servicio AS id_orden,
                    os.Estado_orden_servicio AS estado,
                    os.Descripcion_reparacion AS descripcion,
                    os.Costo_reparacion AS costo,
                    os.Nota_orden_servicio AS nota,
                    os.Fecha_entrada AS fecha_e,
                    os.Fecha_salida AS fecha_s
                FROM Orden_servicio os
                JOIN Equipo e ON os.ID_equipo = e.ID_equipo
                JOIN Fotos_orden_servicio fot ON os.ID_orden_servicio = fot.ID_orden_servicio
                ORDER BY os.ID_orden_servicio DESC
                """
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar órdenes de servicio: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def listar_ordenes_taller(self):
        db = self._conexion.conexion1()
        if not db:
            return "Error al conectar con la base de datos."
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    os.ID_orden_servicio AS id_orden,
                    os.Estado_orden_servicio AS estado,
                    os.ID_cliente as id_cliente,
                    CASE 
                        WHEN pn.ID_cliente IS NOT NULL THEN CONCAT(pn.Nombre_cliente, ' ', pn.Apellido_cliente)
                        WHEN cj.ID_cliente IS NOT NULL THEN cj.Razon_social
                        ELSE 'Cliente no especificado'
                    END AS nombre_cliente,
                    p.Nombre_producto AS modelo,
                    os.Descripcion_reparacion AS descripcion,       
                    os.Fecha_entrada AS fecha_e      
                FROM Orden_servicio os
                INNER JOIN Equipo e ON os.ID_equipo = e.ID_equipo
                INNER JOIN Cliente c ON os.ID_cliente = c.ID_cliente
                LEFT JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente_juridico cj ON c.ID_cliente = cj.ID_cliente
                INNER JOIN Producto p ON e.ID_producto = p.ID_producto
                WHERE os.Estado_orden_servicio IN ('Pendiente', 'En proceso')
                ORDER BY os.ID_orden_servicio DESC;
                """
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar órdenes de taller: {e}")
            return []
        finally:
            cursor.close()
            db.close()
        
    def listar_ordenes_tecnico(self):
        empleado_id = self.ID_empleado
        db = self._conexion.conexion1()
        if not db:
            return "Error al conectar con la base de datos."
        
        cursor = db.cursor(dictionary=True)
        try:
            sql ="""
                SELECT 
                o.ID_orden_servicio AS id_orden,                 
                p.Nombre_producto AS modelo,
                o.Descripcion_reparacion AS descripcion,       
                o.Fecha_entrada AS fecha_e 
                FROM Orden_servicio o 
                INNER JOIN Equipo e ON o.ID_equipo = e.ID_equipo
                INNER JOIN Producto p ON e.ID_producto = p.ID_producto
                INNER JOIN Interaccion i ON o.ID_orden_servicio = i.ID_orden_servicio
                where o.Estado_orden_servicio = 'Asignada' And i.Accion =  'Asignada' and i.ID_empleado = %s
                """
            cursor.execute(sql, (empleado_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar órdenes de taller: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def consultar_orden(self):
        id_orden = self.ID_orden_servicio

        validar_id_orden = validar_texto_numero(id_orden, 1, 10, "ID dela orden")
        if validar_id_orden:
            return validar_id_orden

        db = self._conexion.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = """ SELECT o.*, 
                p.Nombre_producto AS Modelo, 
                o.Estado_orden_servicio AS Estado,
                CASE 
                        WHEN pn.ID_cliente IS NOT NULL THEN CONCAT(pn.Nombre_cliente, ' ', pn.Apellido_cliente)
                        WHEN cj.ID_cliente IS NOT NULL THEN cj.Razon_social
                        ELSE 'Cliente no especificado'
                    END AS nombre_cliente,
                o.Descripcion_reparacion AS Descripcion,
                o.Nota_orden_servicio AS Nota
                FROM Orden_servicio o 
                JOIN Equipo e ON o.ID_equipo = e.ID_equipo 
                JOIN Cliente c ON o.ID_cliente = c.ID_cliente
                JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente_juridico cj ON c.ID_cliente = cj.ID_cliente
                WHERE o.ID_orden_servicio = %s"""
            
            cursor.execute(sql, (id_orden,))
            orden = cursor.fetchone()
            
            if not orden:
                return None
            
            sql_fotos = "SELECT * FROM Fotos_orden_servicio WHERE ID_orden_servicio = %s"
            cursor.execute(sql_fotos, (id_orden,))
            fotos = cursor.fetchall()
            
            orden['fotos'] = fotos if fotos else []
            
            return orden
            
        except Exception as e:
            print(f"Error al consultar la orden: {e}")
            return None
        finally:
            cursor.close()
            db.close()

    def empleados_asignados(self, id_orden: int):
        db = self._conexion.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                "SELECT i.Accion, e.* "
                "FROM Interaccion i JOIN Empleado e ON i.ID_empleado = e.ID_empleado "
                "WHERE i.ID_orden_servicio = %s"
            )
            cursor.execute(sql, (id_orden,))
            empleados = cursor.fetchall()
            return empleados
        finally:
            cursor.close()
            db.close()

    def verificar_foto_existe_por_id(self) -> bool:
        id_foto = self.ID_foto_orden_servicio
        if not id_foto:
            return False
            
        db = self._conexion.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM Fotos_orden_servicio WHERE ID_foto_orden_servicio = %s LIMIT 1",
                (id_foto.strip(),)
            )
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error al verificar foto por ID: {e}")
            return False
        finally:
            cursor.close()
            db.close()

    def eliminar_foto_orden_servicio(self) -> dict:
        id_foto = self.ID_foto_orden_servicio
        
        if not id_foto:
            return {"success": False, "error": "El ID de la foto es obligatorio"}
        
        db = self._conexion.conexion1()
        if not db:
            return {"success": False, "error": "Error al conectar con la base de datos."}
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT Foto_orden_servicio, ID_orden_servicio FROM Fotos_orden_servicio WHERE ID_foto_orden_servicio = %s",
                (id_foto,)
            )
            foto = cursor.fetchone()
            
            if not foto:
                return {"success": False, "error": f"No se encontró una foto con ID {id_foto}"}
            
            ruta_foto = foto.get('Foto_orden_servicio')
            id_orden = foto.get('ID_orden_servicio')
            
            cursor.execute(
                "DELETE FROM Fotos_orden_servicio WHERE ID_foto_orden_servicio = %s",
                (id_foto,)
            )
            db.commit()
            
            return {
                "success": True,
                "mensaje": f"La foto con ID {id_foto} se eliminó exitosamente",
                "ruta_foto": ruta_foto,
                "id_orden": id_orden
            }
        except Exception as e:
            db.rollback()
            print(f"Error al eliminar la foto: {e}")
            return {"success": False, "error": f"Error al eliminar la foto: {str(e)}"}
        finally:
            cursor.close()
            db.close()

    def registrar_fotos(self,) -> dict:
        id_orden = self.ID_orden_servicio
        lista_rutas = self.Foto_orden_servicio
        
        db = self._conexion.conexion1()
        if not db:
            return {"success": False, "error": "Error al conectar con la base de datos."}
        
        cursor = db.cursor()
        try:
            import json
            json_fotos = json.dumps(lista_rutas)
            cursor.callproc('sp_registrar_fotos_orden', (id_orden, json_fotos))
            
            resultado = None
            for result in cursor.stored_results():
                resultado = result.fetchall()
            
            db.commit()
            
            return {
                "success": True,
                "mensaje": f"{len(lista_rutas)} fotos registradas exitosamente",
                "data": resultado
            }
        except Exception as e:
            db.rollback()
            print(f"Error al registrar fotos: {e}")
            error_msg = str(e)
            if "MESSAGE_TEXT" in error_msg:
                match = re.search(r"MESSAGE_TEXT: (.*?)(?:,|$)", error_msg)
                if match:
                    error_msg = match.group(1).strip()
            return {"success": False, "error": f"Error al registrar fotos: {error_msg}"}
        finally:
            cursor.close()
            db.close()

    def asignar_orden_empleado(self):
        db = self._conexion.conexion1()
        if not db:
            return False
        
        cursor = db.cursor()
        try:
            sql = "CALL sp_asignar_orden_servicio(%s, %s);"
            cursor.execute(sql, (self.ID_orden_servicio, self.ID_empleado))
            
            while cursor.nextset():
                try:
                    cursor.fetchall()
                except:
                    pass
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error al asignar la orden al empleado: {e}")
            return False
        finally:
            cursor.close()
            db.close()

    def liberar_orden_empleado(self):
        db = self._conexion.conexion1()
        if not db:
            return False
        
        cursor = db.cursor()
        try:
            sql = "CALL sp_liberar_orden_servicio(%s, %s);"
            cursor.execute(sql, (self.ID_orden_servicio, self.ID_empleado))
            
            while cursor.nextset():
                try:
                    cursor.fetchall()
                except:
                    pass
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error al liberar la orden del empleado: {e}")
            return False
        finally:
            cursor.close()
            db.close()

    def registrar_reparacion(self):
        validar_descripcion = validar_texto_numero(self.Descripcion_reparacion, 0, 300, "Desdescripcion ")
        if validar_descripcion:
            return {"success": False, "error": validar_descripcion}

        db = self._conexion.conexion1()
        if not db:
            return {"error": "Error de conexión a la base de datos"}
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = "CALL sp_registrar_reparacion(%s, %s, %s, %s);"
            cursor.execute(sql, (
                self.ID_orden_servicio,
                self.ID_empleado,
                self.Descripcion_reparacion,
                self.lista_repuestos
            ))
            
            resultado = cursor.fetchone()
            
            while cursor.nextset():
                try:
                    cursor.fetchall()
                except:
                    pass
            
            db.commit()
            
            if resultado and isinstance(resultado, dict):
                mensaje = resultado.get('mensaje') or resultado.get('Mensaje') or resultado.get('resultado')
                if mensaje and "exitosamente" in str(mensaje).lower():
                    return {"success": True, "mensaje": mensaje, "data": resultado}
                else:
                    return {"error": mensaje if mensaje else "Error desconocido", "data": resultado}
            else:
                return {"success": True, "mensaje": "Reparación registrada exitosamente"}
                
        except Exception as e:
            db.rollback()
            print(f"Error al registrar la reparación: {e}")
            return {"error": f"Error en la base de datos: {str(e)}"}
        finally:
            cursor.close()
            db.close()

    # ============================================
    # MÉTODO PARA CREAR ORDEN DE SERVICIO (Validaciones trasladadas)
    # ============================================
    def crear_orden(self, id_cliente: str, id_equipo: str, id_modelo: str,
                    descripcion: str, nota: str = None, modelo_custom: str = None,
                    color: str = None, capacidad: str = None, tipo_cliente: str = "natural") -> str:
        
        # 1. VALIDACIONES DE NEGOCIO EN EL MODELO
        if not id_cliente:
            raise Exception("El ID del cliente es obligatorio.")
        
        id_cliente_val = str(id_cliente).strip()
        
        if tipo_cliente == "natural":
            if not id_cliente_val.isdigit():
                raise Exception("La cédula debe contener solo números.")
            if len(id_cliente_val) < 7 or len(id_cliente_val) > 8:
                raise Exception("La cédula debe tener 7 u 8 dígitos.")
        else:
            error_rif = self._validar_rif(id_cliente_val)
            if error_rif:
                raise Exception(error_rif)
        
        if not descripcion:
            raise Exception("La descripción del problema es obligatoria.")
        if len(descripcion) > 300:
            raise Exception("La descripción no puede exceder 300 caracteres.")
        
        if not id_equipo:
            raise Exception("El IMEI del equipo es obligatorio.")
        if not id_equipo.isdigit():
            raise Exception("El IMEI debe ser un número.")
        if len(id_equipo) != 15:
            raise Exception("El IMEI debe tener exactamente 15 dígitos.")
            
        if not color:
            raise Exception("El color del equipo es obligatorio.")
        if not capacidad:
            raise Exception("La capacidad del equipo es obligatoria.")
            
        if not id_modelo and not modelo_custom:
            raise Exception("Debes seleccionar un modelo o escribir uno personalizado.")

        db = self._conexion.conexion1()
        if not db:
            raise Exception("Error al conectar con la base de datos.")
        
        cursor = db.cursor(dictionary=True)
        try:
            # 2. Verificar que el cliente existe
            cliente_encontrado = False
            cliente_id_real = id_cliente
            
            if '-' in id_cliente:
                id_sin_guiones = id_cliente.replace("-", "").upper()
                cursor.execute(
                    "SELECT ID_cliente FROM Cliente WHERE ID_cliente = %s OR ID_cliente = %s",
                    (id_cliente, id_sin_guiones)
                )
                row = cursor.fetchone()
                if row:
                    cliente_encontrado = True
                    cliente_id_real = row['ID_cliente']
            else:
                if re.search(r'[A-Za-z]', id_cliente) and len(id_cliente) == 10 and id_cliente[0] in 'JE':
                    id_con_guiones = f"{id_cliente[0]}-{id_cliente[1:9]}-{id_cliente[9]}"
                    cursor.execute(
                        "SELECT ID_cliente FROM Cliente WHERE ID_cliente = %s OR ID_cliente = %s",
                        (id_cliente, id_con_guiones)
                    )
                    row = cursor.fetchone()
                    if row:
                        cliente_encontrado = True
                        cliente_id_real = row['ID_cliente']
                else:
                    cursor.execute(
                        "SELECT ID_cliente FROM Cliente WHERE ID_cliente = %s",
                        (id_cliente,)
                    )
                    row = cursor.fetchone()
                    if row:
                        cliente_encontrado = True
                        cliente_id_real = row['ID_cliente']
            
            if not cliente_encontrado:
                cursor.execute(
                    "SELECT ID_cliente FROM Cliente_juridico WHERE Rif_cliente = %s",
                    (id_cliente,)
                )
                row = cursor.fetchone()
                if row:
                    cliente_encontrado = True
                    cliente_id_real = row['ID_cliente']
            
            if not cliente_encontrado and '-' in id_cliente:
                id_sin_guiones = id_cliente.replace("-", "").upper()
                cursor.execute(
                    "SELECT ID_cliente FROM Cliente_juridico WHERE Rif_cliente = %s",
                    (id_sin_guiones,)
                )
                row = cursor.fetchone()
                if row:
                    cliente_encontrado = True
                    cliente_id_real = row['ID_cliente']
            
            if not cliente_encontrado:
                raise Exception(f"El cliente con ID {id_cliente} no existe en la base de datos.")
            
            id_cliente_guardar = cliente_id_real
            
            # 3. Verificar que el equipo existe
            cursor.execute(
                "SELECT ID_equipo FROM Equipo WHERE ID_equipo = %s",
                (id_equipo,)
            )
            equipo = cursor.fetchone()
            if not equipo:
                raise Exception(f"El equipo con IMEI {id_equipo} no existe en la base de datos.")
            
            # 4. Verificar que el modelo existe
            if id_modelo:
                cursor.execute(
                    "SELECT ID_producto FROM Producto WHERE ID_producto = %s",
                    (id_modelo,)
                )
                modelo = cursor.fetchone()
                if not modelo:
                    raise Exception(f"El modelo con ID {id_modelo} no existe en la base de datos.")
            
            # 5. Generar nuevo ID para la orden
            cursor.execute("SELECT MAX(ID_orden_servicio) as max_id FROM Orden_servicio")
            result = cursor.fetchone()
            ultimo_id = result['max_id'] if result else None
            
            if ultimo_id is None:
                siguiente_numero = 1
            else:
                siguiente_numero = int(ultimo_id[2:]) + 1
            
            nuevo_id = f"OS{str(siguiente_numero).zfill(7)}"
            
            # 6. Insertar la orden de servicio
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            sql = """
                INSERT INTO Orden_servicio 
                (ID_orden_servicio, ID_equipo, ID_cliente, Estado_orden_servicio, 
                 Descripcion_reparacion, Nota_orden_servicio, Fecha_entrada)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                nuevo_id,
                id_equipo,
                id_cliente_guardar,
                'Pendiente',
                descripcion,
                nota,
                fecha_actual
            ))
            
            # 7. Registrar la interacción inicial
            cursor.execute("SELECT MAX(ID_interaccion) as max_id FROM Interaccion")
            result = cursor.fetchone()
            ultimo_id_int = result['max_id'] if result else None
            
            if ultimo_id_int is None:
                siguiente_num_int = 1
            else:
                siguiente_num_int = int(ultimo_id_int[3:]) + 1
            
            nuevo_id_int = f"INT{str(siguiente_num_int).zfill(6)}"
            
            cursor.execute(
                "INSERT INTO Interaccion (ID_interaccion, ID_orden_servicio, ID_empleado, Accion) VALUES (%s, %s, %s, %s)",
                (nuevo_id_int, nuevo_id, self.ID_empleado, 'Pendiente')
            )
            
            # 8. Confirmar la transacción
            db.commit()
            
            print(f"[MODEL] Orden creada exitosamente: {nuevo_id}")
            return nuevo_id
            
        except Exception as e:
            db.rollback()
            print(f"[MODEL] Error al crear orden: {e}")
            raise e
        finally:
            cursor.close()
            db.close()

    def listado_ordenes_servicio(self, estados=None):
        db = self._conexion.conexion1()
        if not db:
            print("Error al conectar con la base de datos.")
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = """
                SELECT 
                    os.ID_orden_servicio AS ID_orden,
                    os.Estado_orden_servicio AS Estado,
                    os.Descripcion_reparacion AS Des_cliente,
                    os.Costo_reparacion AS Costo,
                    os.Nota_orden_servicio AS Nota,
                    os.Fecha_entrada AS Fecha_e,
                    os.Fecha_salida AS Fecha_s,
                    os.ID_cliente AS ID_cliente,
                    c.Direccion_cliente AS Direccion_cliente,
                    c.Celular_cliente AS Celular_cliente,
                    c.Correo_cliente AS Correo_cliente,
                    pn.Nombre_cliente AS Nombre_cliente,
                    pn.Apellido_cliente AS Apellido_cliente,
                    cj.Razon_social AS Razon_social,
                    CASE 
                        WHEN pn.ID_cliente IS NOT NULL THEN CONCAT(pn.Nombre_cliente, ' ', pn.Apellido_cliente)
                        WHEN cj.ID_cliente IS NOT NULL THEN cj.Razon_social
                        ELSE 'Cliente no especificado'
                    END AS Nombre_completo,
                    e.ID_equipo AS Equipo,
                    e.Color AS Color,
                    e.Capacidad AS Capacidad,
                    prod.Nombre_producto AS Modelo,
                    mp.Nombre_marca AS Marca,
                    cp.Nombre_Clase AS Clase
                FROM Orden_servicio os
                INNER JOIN Cliente c ON os.ID_cliente = c.ID_cliente
                LEFT JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente_juridico cj ON c.ID_cliente = cj.ID_cliente
                INNER JOIN Equipo e ON os.ID_equipo = e.ID_equipo
                INNER JOIN Producto prod ON e.ID_producto = prod.ID_producto
                INNER JOIN Marca_producto mp ON prod.ID_marca = mp.ID_marca
                INNER JOIN Clase_producto cp ON prod.ID_Clase = cp.ID_Clase
            """
            
            params = []
            if estados:
                placeholders = ','.join(['%s'] * len(estados))
                sql += f" WHERE os.Estado_orden_servicio IN ({placeholders})"
                params.extend(estados)
            
            sql += " ORDER BY os.ID_orden_servicio DESC"
            
            cursor.execute(sql, params)
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Error al listar órdenes de servicio: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def detalles_orden(self, id_orden: str) -> dict:
        db = self._conexion.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = """
                SELECT 
                    os.ID_orden_servicio AS ID_orden,
                    os.Estado_orden_servicio AS Estado,
                    os.Descripcion_reparacion AS Des_cliente,
                    os.Costo_reparacion AS Costo_reparacion,
                    os.Nota_orden_servicio AS Nota,
                    os.Fecha_entrada AS Fecha_e,
                    os.Fecha_salida AS Fecha_s,
                    os.ID_cliente AS ID_cliente,
                    c.Direccion_cliente AS Direccion_cliente,
                    c.Celular_cliente AS Celular_cliente,
                    c.Correo_cliente AS Correo_cliente,
                    pn.Nombre_cliente AS Nombre_cliente,
                    pn.Apellido_cliente AS Apellido_cliente,
                    cj.Razon_social AS Razon_social,
                    CASE 
                        WHEN pn.ID_cliente IS NOT NULL THEN CONCAT(pn.Nombre_cliente, ' ', pn.Apellido_cliente)
                        WHEN cj.ID_cliente IS NOT NULL THEN cj.Razon_social
                        ELSE 'Cliente no especificado'
                    END AS Nombre_completo,
                    e.ID_equipo AS Equipo,
                    e.Color AS Color,
                    e.Capacidad AS Capacidad,
                    e.Clave AS Clave,
                    e.Patron AS Patron,
                    prod.ID_producto AS ID_producto,
                    prod.Nombre_producto AS Modelo,
                    prod.Descripcion AS Descripcion_producto,
                    mp.Nombre_marca AS Marca,
                    cp.Nombre_Clase AS Clase
                FROM Orden_servicio os
                INNER JOIN Cliente c ON os.ID_cliente = c.ID_cliente
                LEFT JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente_juridico cj ON c.ID_cliente = cj.ID_cliente
                INNER JOIN Equipo e ON os.ID_equipo = e.ID_equipo
                INNER JOIN Producto prod ON e.ID_producto = prod.ID_producto
                INNER JOIN Marca_producto mp ON prod.ID_marca = mp.ID_marca
                INNER JOIN Clase_producto cp ON prod.ID_Clase = cp.ID_Clase
                WHERE os.ID_orden_servicio = %s
            """
            cursor.execute(sql, (id_orden,))
            return cursor.fetchone()
            
        except Exception as e:
            print(f"Error al obtener detalles de la orden: {e}")
            return None
        finally:
            cursor.close()
            db.close()

    def fotos_orden(self, id_orden: str) -> list:
        db = self._conexion.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT ID_foto_orden_servicio AS id, Foto_orden_servicio AS foto FROM Fotos_orden_servicio WHERE ID_orden_servicio = %s",
                (id_orden,)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener fotos de la orden: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def actualizar_estado(self, id_orden: str, nuevo_estado: str) -> bool:
        db = self._conexion.conexion1()
        if not db:
            return False
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE Orden_servicio SET Estado_orden_servicio = %s WHERE ID_orden_servicio = %s",
                (nuevo_estado, id_orden)
            )
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            db.rollback()
            print(f"Error al actualizar estado: {e}")
            return False
        finally:
            cursor.close()
            db.close()

    def eliminar_orden(self, id_orden: str) -> bool:
        db = self._conexion.conexion1()
        if not db:
            return False
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT Estado_orden_servicio FROM Orden_servicio WHERE ID_orden_servicio = %s",
                (id_orden,)
            )
            result = cursor.fetchone()
            if not result:
                return False
            
            estado = result[0] if isinstance(result, tuple) else result.get('Estado_orden_servicio')
            if estado.lower() != 'pendiente':
                print(f"No se puede eliminar la orden {id_orden} porque está en estado '{estado}'")
                return False
            
            cursor.execute("DELETE FROM Fotos_orden_servicio WHERE ID_orden_servicio = %s", (id_orden,))
            cursor.execute("DELETE FROM Interaccion WHERE ID_orden_servicio = %s", (id_orden,))
            cursor.execute("DELETE FROM Orden_servicio WHERE ID_orden_servicio = %s", (id_orden,))
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error al eliminar la orden: {e}")
            return False
        finally:
            cursor.close()
            db.close()

    def agregar_foto_orden_servicio(self) -> str:
        db = self._conexion.conexion1()
        if not db:
            return "Error al conectar con la base de datos."
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO Fotos_orden_servicio (ID_foto_orden_servicio, ID_orden_servicio, Foto_orden_servicio) VALUES (%s, %s, %s)",
                (self.ID_foto_orden_servicio, self.ID_orden_servicio, self.Foto_orden_servicio)
            )
            db.commit()
            return f"Foto registrada exitosamente con ID {self.ID_foto_orden_servicio}"
        except Exception as e:
            db.rollback()
            print(f"Error al agregar foto: {e}")
            return f"Error al registrar la foto: {str(e)}"
        finally:
            cursor.close()
            db.close()

    def ordenes_asignadas_tecnico(self) -> list:
        empleado_id = self.ID_empleado
        db = self._conexion.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = """
                SELECT 
                    os.ID_orden_servicio AS ID_orden,
                    os.Estado_orden_servicio AS Estado,
                    os.Descripcion_reparacion AS Descripcion,
                    os.Fecha_entrada AS Fecha_e,
                    CASE 
                        WHEN pn.ID_cliente IS NOT NULL THEN CONCAT(pn.Nombre_cliente, ' ', pn.Apellido_cliente)
                        WHEN cj.ID_cliente IS NOT NULL THEN cj.Razon_social
                        ELSE 'Cliente no especificado'
                    END AS Nombre_cliente,
                    prod.Nombre_producto AS modelo,
                    i.Accion AS Accion
                FROM Orden_servicio os
                INNER JOIN Cliente c ON os.ID_cliente = c.ID_cliente
                LEFT JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente_juridico cj ON c.ID_cliente = cj.ID_cliente
                INNER JOIN Equipo e ON os.ID_equipo = e.ID_equipo
                INNER JOIN Producto prod ON e.ID_producto = prod.ID_producto
                INNER JOIN Interaccion i ON os.ID_orden_servicio = i.ID_orden_servicio
                WHERE os.Estado_orden_servicio IN ('Asignada', 'En proceso') 
                AND i.Accion = 'Asignada' 
                AND i.ID_empleado = %s
                ORDER BY os.Fecha_entrada DESC
            """
            cursor.execute(sql, (empleado_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar órdenes del técnico: {e}")
            return []
        finally:
            cursor.close()
            db.close()