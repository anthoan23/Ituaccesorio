from __future__ import annotations

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.database import conectar
from app.models.bitacora import Bitacora
import traceback


class Usuarios:
    def __init__(
        self,
        id: str = "",
        nombre: str = "",
        cedula: str = "",
        password: str = "",
        rol_id: str = "",
        foto_perfil: str = "",
        activo: bool = True,
        fecha_creacion: datetime = None,
        usuario_id: str = None,
    ):
        self.id = id
        self.nombre = nombre
        self.cedula = cedula
        self.password = password
        self.rol_id = rol_id
        self.foto_perfil = foto_perfil
        self.activo = activo
        self.fecha_creacion = fecha_creacion
        self.usuario_id = usuario_id

        self.__conexion_bd = conectar()

    def _hash_password(self, password: str) -> str:
        """Genera un hash de la contrasena"""
        return generate_password_hash(password)

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica si la contrasena coincide con el hash"""
        return check_password_hash(password_hash, password)

    def listar_usuarios(self):
        db = self.__conexion_bd.conexion2()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    u.id,
                    u.nombre,
                    u.cedula AS cedula_personal,
                    u.rol_id,
                    r.nombre AS rol_nombre,
                    u.activo,
                    u.fecha_creacion,
                    u.foto_perfil
                FROM usuario u
                INNER JOIN rol r ON r.id = u.rol_id
                ORDER BY u.fecha_creacion DESC, u.id DESC
                """
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"[ERROR] listar_usuarios: {e}")
            traceback.print_exc()
            return None
        finally:
            cursor.close()
            db.close()

    def listar_empleados(self):
        db = self.__conexion_bd.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    e.ID_empleado AS cedula,
                    e.Nombre_empleado AS nombre,
                    e.Apellido_empleado AS apellido,
                    CONCAT(e.Nombre_empleado, ' ', e.Apellido_empleado) AS nombre_completo
                FROM Empleado e
                ORDER BY e.ID_empleado ASC
                """
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"[ERROR] listar_empleados: {e}")
            traceback.print_exc()
            return None
        finally:
            cursor.close()
            db.close()

    def listar_clientes(self):
        """Lista todos los clientes (personas naturales)"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    pn.ID_cliente AS cedula,
                    CONCAT(pn.Nombre_cliente, ' ', pn.Apellido_cliente) AS nombre_completo,
                    c.Celular_cliente AS celular,
                    c.Correo_cliente AS correo
                FROM Persona_natural pn
                INNER JOIN Cliente c ON c.ID_cliente = pn.ID_cliente
                ORDER BY pn.ID_cliente ASC
                """
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"[ERROR] listar_clientes: {e}")
            traceback.print_exc()
            return None
        finally:
            cursor.close()
            db.close()

    def verificar_empleado(self, cedula: str) -> bool:
        """Verifica si una cedula pertenece a un empleado registrado"""
        try:
            db = self.__conexion_bd.conexion1()
            if not db:
                print("[DEBUG] verificar_empleado: no se pudo conectar")
                return False

            cursor = db.cursor()
            try:
                cursor.execute(
                    "SELECT 1 FROM Empleado WHERE ID_empleado = %s LIMIT 1",
                    (cedula,),
                )
                existe = cursor.fetchone() is not None
                return existe
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"[ERROR] verificar_empleado: {e}")
            traceback.print_exc()
            return False

    def verificar_cliente(self, cedula: str) -> bool:
        """Verifica si una cedula pertenece a un cliente registrado"""
        try:
            db = self.__conexion_bd.conexion1()
            if not db:
                print("[DEBUG] verificar_cliente: no se pudo conectar")
                return False

            cursor = db.cursor()
            try:
                cursor.execute(
                    "SELECT 1 FROM Persona_natural WHERE ID_cliente = %s LIMIT 1",
                    (cedula,),
                )
                existe = cursor.fetchone() is not None
                return existe
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"[ERROR] verificar_cliente: {e}")
            traceback.print_exc()
            return False

    def verificar_usuario_por_id(self) -> bool:
        if not self.id:
            return False

        db = self.__conexion_bd.conexion2()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM usuario WHERE id = %s LIMIT 1",
                (self.id,),
            )
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"[ERROR] verificar_usuario_por_id: {e}")
            traceback.print_exc()
            return False
        finally:
            cursor.close()
            db.close()

    def verificar_usuario_por_nombre(self) -> bool:
        if not self.nombre:
            return False

        db = self.__conexion_bd.conexion2()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM usuario WHERE nombre = %s LIMIT 1",
                (self.nombre,),
            )
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"[ERROR] verificar_usuario_por_nombre: {e}")
            traceback.print_exc()
            return False
        finally:
            cursor.close()
            db.close()

    def verificar_cedula_en_uso(self, cedula: str, usuario_id: str = None) -> bool:
        """Verifica si una cedula ya esta asignada a otro usuario"""
        db = self.__conexion_bd.conexion2()
        if not db:
            return False

        cursor = db.cursor()
        try:
            if usuario_id:
                cursor.execute(
                    "SELECT 1 FROM usuario WHERE cedula = %s AND id != %s LIMIT 1",
                    (cedula, usuario_id),
                )
            else:
                cursor.execute(
                    "SELECT 1 FROM usuario WHERE cedula = %s LIMIT 1",
                    (cedula,),
                )
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"[ERROR] verificar_cedula_en_uso: {e}")
            traceback.print_exc()
            return False
        finally:
            cursor.close()
            db.close()

    def verificar_rol_y_cedula(self) -> bool:
        """
        Verifica que la cedula corresponda al tipo de rol seleccionado
        Para clientes, permite el registro aunque no exista en Persona_natural
        """
        try:
            if not self.cedula or not self.rol_id:
                print("[DEBUG] verificar_rol_y_cedula: cedula o rol_id vacio")
                return False

            db_usuarios = self.__conexion_bd.conexion2()
            if not db_usuarios:
                print("[DEBUG] verificar_rol_y_cedula: no se pudo conectar")
                return False

            cursor = db_usuarios.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT nombre FROM rol WHERE id = %s",
                    (self.rol_id,),
                )
                rol = cursor.fetchone()
                if not rol:
                    print(f"[DEBUG] verificar_rol_y_cedula: rol no encontrado para id {self.rol_id}")
                    return False

                nombre_rol = rol["nombre"].lower()
                print(f"[DEBUG] verificar_rol_y_cedula: rol = {nombre_rol}, cedula = {self.cedula}")

                if nombre_rol == "cliente":
                    # Para clientes, siempre permitimos porque puede ser nuevo registro
                    print("[DEBUG] verificar_rol_y_cedula: cliente, permitido")
                    return True
                else:
                    # Para empleados, verificamos que exista en Empleado
                    resultado = self.verificar_empleado(self.cedula)
                    print(f"[DEBUG] verificar_rol_y_cedula: es empleado? {resultado}")
                    return resultado
            finally:
                cursor.close()
                db_usuarios.close()
        except Exception as e:
            print(f"[ERROR] verificar_rol_y_cedula: {e}")
            traceback.print_exc()
            return False

    def agregar_usuario(self) -> str:
        try:
            nombre = self.nombre.strip()
            cedula = self.cedula.strip()
            password = self.password.strip()
            rol_id = self.rol_id.strip()
            foto_perfil = self.foto_perfil or None

            # Validaciones
            if not nombre or not cedula or not password or not rol_id:
                return "Nombre, cedula, contrasena y rol son obligatorios."

            if len(nombre) > 50:
                return "El nombre no puede exceder los 50 caracteres."

            if len(password) < 6:
                return "La contrasena debe tener al menos 6 caracteres."

            if len(password) > 50:
                return "La contrasena no puede exceder los 50 caracteres."

            # Verificar si el usuario ya existe
            if self.verificar_usuario_por_nombre():
                return f"El nombre de usuario '{nombre}' ya existe."

            if self.verificar_cedula_en_uso(cedula):
                return f"La cedula '{cedula}' ya esta asignada a otro usuario."

            # Verificar si la cedula corresponde al rol
            if not self.verificar_rol_y_cedula():
                return "La cedula no corresponde al tipo de rol seleccionado."

            db = self.__conexion_bd.conexion2()
            if not db:
                return "Error al conectar a la base de datos."

            cursor = db.cursor()
            try:
                # Generar nuevo ID para el usuario
                cursor.execute("SELECT MAX(id) FROM usuario")
                result = cursor.fetchone()
                ultimo_id = result[0] if result else None
                
                if ultimo_id:
                    try:
                        numero = int(ultimo_id.split('-')[1]) + 1
                        nuevo_id = f"USR-{numero:03d}"
                    except (IndexError, ValueError):
                        # Si el formato no es USR-XXX, buscar el maximo numerico
                        cursor.execute("SELECT MAX(CAST(SUBSTRING(id, 5) AS UNSIGNED)) FROM usuario WHERE id LIKE 'USR-%'")
                        result_max = cursor.fetchone()
                        max_num = result_max[0] if result_max and result_max[0] else 0
                        nuevo_id = f"USR-{max_num + 1:03d}"
                else:
                    nuevo_id = "USR-001"
                
                print(f"[DEBUG] Generando ID: {nuevo_id} para usuario {nombre}")
                
                password_hash = self._hash_password(password)
                
                # Insertar usuario
                cursor.execute(
                    """
                    INSERT INTO usuario (id, nombre, cedula, password, rol_id, activo, foto_perfil)
                    VALUES (%s, %s, %s, %s, %s, 1, %s)
                    """,
                    (nuevo_id, nombre, cedula, password_hash, rol_id, foto_perfil),
                )
                db.commit()
                self.id = nuevo_id
                
                # Registrar en bitacora
                if self.usuario_id:
                    bitacora = Bitacora(
                        accion="Crear usuario",
                        descripcion=f"Se creo el usuario: {nombre} - Cedula: {cedula} - Rol ID: {rol_id}",
                        usuario_id=self.usuario_id,
                        modulo_nombre="Usuarios"
                    )
                    bitacora.registrar()
                
                print(f"[DEBUG] Usuario creado exitosamente: {nuevo_id}")
                return "Usuario agregado exitosamente."
                
            except Exception as e:
                print(f"[ERROR] Error en INSERT de usuario: {e}")
                print(f"[ERROR] Datos: id={nuevo_id}, nombre={nombre}, cedula={cedula}, rol_id={rol_id}")
                traceback.print_exc()
                db.rollback()
                return f"Error al agregar usuario: {str(e)}"
            finally:
                cursor.close()
                db.close()
                
        except Exception as e:
            print(f"[ERROR] Error en agregar_usuario: {e}")
            traceback.print_exc()
            return f"Error en agregar_usuario: {str(e)}"

    def actualizar_usuario(self) -> str:
        try:
            usuario_id = self.id.strip()
            nombre = self.nombre.strip()
            cedula = self.cedula.strip()
            rol_id = self.rol_id.strip()
            foto_perfil = self.foto_perfil or None
            password = self.password.strip() if self.password else None

            if not usuario_id or not nombre or not cedula or not rol_id:
                return "ID, nombre, cedula y rol son obligatorios."

            if len(nombre) > 50:
                return "El nombre no puede exceder los 50 caracteres."

            if not self.verificar_usuario_por_id():
                return f"El usuario con ID {usuario_id} no existe."

            if self.verificar_cedula_en_uso(cedula, usuario_id):
                return f"La cedula '{cedula}' ya esta asignada a otro usuario."

            # Verificar si la cedula corresponde al rol
            if not self.verificar_rol_y_cedula():
                return "La cedula no corresponde al tipo de rol seleccionado."

            db = self.__conexion_bd.conexion2()
            if not db:
                return "Error al conectar a la base de datos."

            cursor = db.cursor()
            try:
                if password:
                    password_hash = self._hash_password(password)
                    cursor.execute(
                        """
                        UPDATE usuario
                        SET nombre = %s, cedula = %s, password = %s, rol_id = %s, foto_perfil = %s
                        WHERE id = %s
                        """,
                        (nombre, cedula, password_hash, rol_id, foto_perfil, usuario_id),
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE usuario
                        SET nombre = %s, cedula = %s, rol_id = %s, foto_perfil = %s
                        WHERE id = %s
                        """,
                        (nombre, cedula, rol_id, foto_perfil, usuario_id),
                    )
                db.commit()
                
                # Registrar en bitacora
                if self.usuario_id:
                    bitacora = Bitacora(
                        accion="Actualizar usuario",
                        descripcion=f"Se actualizo el usuario ID: {usuario_id} - Nuevo nombre: {nombre} - Rol ID: {rol_id}",
                        usuario_id=self.usuario_id,
                        modulo_nombre="Usuarios"
                    )
                    bitacora.registrar()
                
                return "Usuario actualizado exitosamente."
            except Exception as e:
                print(f"[ERROR] Error al actualizar usuario: {e}")
                traceback.print_exc()
                db.rollback()
                return "Error al actualizar usuario."
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"[ERROR] Error en actualizar_usuario: {e}")
            traceback.print_exc()
            return f"Error en actualizar_usuario: {str(e)}"

    def eliminar_usuario(self) -> str:
        try:
            usuario_id = self.id.strip()

            if not usuario_id:
                return "El identificador del usuario no puede estar vacio."

            if not self.verificar_usuario_por_id():
                return f"El usuario con identificador {usuario_id} no existe."

            db = self.__conexion_bd.conexion2()
            if not db:
                return "Error al conectar a la base de datos."

            cursor = db.cursor(dictionary=True)
            try:
                # Verificar si es admin y si es el unico
                cursor.execute(
                    """
                    SELECT COUNT(*) as total
                    FROM usuario u
                    INNER JOIN rol r ON r.id = u.rol_id
                    WHERE r.nombre = 'admin'
                    """
                )
                result = cursor.fetchone()
                total_admins = result["total"] if result else 0

                cursor.execute(
                    """
                    SELECT r.nombre as rol_nombre, u.nombre as usuario_nombre
                    FROM usuario u
                    INNER JOIN rol r ON r.id = u.rol_id
                    WHERE u.id = %s
                    """,
                    (usuario_id,),
                )
                usuario_rol = cursor.fetchone()

                if usuario_rol and usuario_rol["rol_nombre"].lower() == "admin" and total_admins <= 1:
                    return "No se puede eliminar el unico administrador del sistema."

                nombre_usuario = usuario_rol["usuario_nombre"] if usuario_rol else "N/A"

                cursor.execute("DELETE FROM usuario WHERE id = %s", (usuario_id,))
                db.commit()
                
                # Registrar en bitacora
                if self.usuario_id:
                    bitacora = Bitacora(
                        accion="Eliminar usuario",
                        descripcion=f"Se elimino el usuario ID: {usuario_id} - Nombre: {nombre_usuario}",
                        usuario_id=self.usuario_id,
                        modulo_nombre="Usuarios"
                    )
                    bitacora.registrar()
                
                return "Usuario eliminado exitosamente."
            except Exception as e:
                print(f"[ERROR] Error al eliminar usuario: {e}")
                traceback.print_exc()
                db.rollback()
                return "Error al eliminar usuario. Verifica que no este en uso."
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"[ERROR] Error en eliminar_usuario: {e}")
            traceback.print_exc()
            return f"Error en eliminar_usuario: {str(e)}"

    def obtener_rol_por_nombre(self, nombre_rol: str = None):
        """Obtiene un rol por su nombre"""
        nombre_buscar = nombre_rol or self.nombre
        if not nombre_buscar:
            return None
        
        db = self.__conexion_bd.conexion2()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, nombre, descripcion FROM rol WHERE nombre = %s LIMIT 1",
                (nombre_buscar,)
            )
            return cursor.fetchone()
        except Exception as e:
            print(f"[ERROR] obtener_rol_por_nombre: {e}")
            traceback.print_exc()
            return None
        finally:
            cursor.close()
            db.close()

    def validar_login(self, nombre: str, password: str):
        """Valida las credenciales de un usuario"""
        db = self.__conexion_bd.conexion2()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT u.id, u.nombre, u.cedula, u.password, u.rol_id, u.foto_perfil, r.nombre AS rol_nombre
                FROM usuario u
                INNER JOIN rol r ON u.rol_id = r.id
                WHERE u.nombre = %s AND u.activo = 1
                """,
                (nombre,),
            )
            usuario = cursor.fetchone()

            if usuario and self._verify_password(password, usuario.get("password", "")):
                usuario.pop("password", None)
                return usuario

            return None
        except Exception as e:
            print(f"[ERROR] validar_login: {e}")
            traceback.print_exc()
            return None
        finally:
            cursor.close()
            db.close()

    def obtener_usuario_por_id(self, usuario_id: str = None):
        id_buscar = usuario_id or self.id
        if not id_buscar:
            return None

        db = self.__conexion_bd.conexion2()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    u.id,
                    u.nombre,
                    u.cedula AS cedula_personal,
                    u.rol_id,
                    u.foto_perfil,
                    u.activo,
                    u.fecha_creacion,
                    r.nombre AS rol_nombre
                FROM usuario u
                INNER JOIN rol r ON r.id = u.rol_id
                WHERE u.id = %s
                LIMIT 1
                """,
                (id_buscar,),
            )
            return cursor.fetchone()
        except Exception as e:
            print(f"[ERROR] obtener_usuario_por_id: {e}")
            traceback.print_exc()
            return None
        finally:
            cursor.close()
            db.close()

    def actualizar_perfil(self, usuario_id: str, nombre: str, password: str = None, foto_perfil: str = None) -> str:
        try:
            if not usuario_id or not nombre:
                return "ID y nombre son obligatorios."

            if len(nombre) > 50:
                return "El nombre no puede exceder los 50 caracteres."

            db = self.__conexion_bd.conexion2()
            if not db:
                return "Error al conectar a la base de datos."

            cursor = db.cursor()
            try:
                if password:
                    password_hash = self._hash_password(password)
                    cursor.execute(
                        """
                        UPDATE usuario
                        SET nombre = %s, password = %s, foto_perfil = %s
                        WHERE id = %s
                        """,
                        (nombre, password_hash, foto_perfil, usuario_id),
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE usuario
                        SET nombre = %s, foto_perfil = %s
                        WHERE id = %s
                        """,
                        (nombre, foto_perfil, usuario_id),
                    )
                db.commit()
                
                # Registrar en bitacora
                if self.usuario_id:
                    bitacora = Bitacora(
                        accion="Actualizar perfil",
                        descripcion=f"Usuario actualizo su perfil",
                        usuario_id=self.usuario_id,
                        modulo_nombre="Usuarios"
                    )
                    bitacora.registrar()
                
                return "Perfil actualizado exitosamente."
            except Exception as e:
                print(f"[ERROR] Error al actualizar perfil: {e}")
                traceback.print_exc()
                db.rollback()
                return "Error al actualizar perfil."
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"[ERROR] Error en actualizar_perfil: {e}")
            traceback.print_exc()
            return f"Error en actualizar_perfil: {str(e)}"