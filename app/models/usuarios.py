from __future__ import annotations

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.database import conectar
from app.models.bitacora import Bitacora
from app.utils.validators import (
    validar_solo_letras,
    validar_numero,
    validar_contraseña,
)
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
        return generate_password_hash(password)

    def _verify_password(self, password: str, password_hash: str) -> bool:
        return check_password_hash(password_hash, password)

    # ==================== VALIDACIONES ====================

    def _validar_datos_usuario(self, requiere_password: bool = True, requiere_rol: bool = True) -> str | None:
        """
        Valida nombre, cédula, password (opcional) y rol_id contra el esquema.
        Normaliza los campos a str en self.
        """
        nombre = str(self.nombre).strip() if self.nombre is not None else ""
        # usuario.nombre varchar(50)
        error = validar_solo_letras(nombre, 1, 50, "Nombre", permitir_espacios=True)
        if error:
            return error
        self.nombre = nombre

        cedula = str(self.cedula).strip() if self.cedula is not None else ""
        # usuario.cedula int NOT NULL (cédula VE 6–8 dígitos)
        error = validar_numero(cedula, 6, 8, "Cédula")
        if error:
            return error
        self.cedula = cedula

        if requiere_password:
            password = str(self.password).strip() if self.password else ""
            if not password:
                return "La contraseña es obligatoria."
            # usuario.password varchar(255); mínimo 6 por política
            error = validar_contraseña(password, 6, 50, "Contraseña")
            if error:
                return error
            self.password = password
        elif self.password:
            password = str(self.password).strip()
            error = validar_contraseña(password, 6, 50, "Contraseña")
            if error:
                return error
            self.password = password

        if requiere_rol:
            rol_id = str(self.rol_id).strip() if self.rol_id is not None else ""
            if not rol_id:
                return "El rol es obligatorio."
            # usuario.rol_id int
            error = validar_numero(rol_id, 1, 10, "Rol")
            if error:
                return error
            self.rol_id = rol_id

        if self.foto_perfil:
            foto = str(self.foto_perfil)
            # usuario.foto_perfil varchar(100)
            if len(foto) > 100:
                return "La ruta de la foto de perfil no puede exceder 100 caracteres."

        return None

    def _validar_perfil(self) -> str | None:
        nombre = str(self.nombre).strip() if self.nombre is not None else ""
        error = validar_solo_letras(nombre, 1, 50, "Nombre", permitir_espacios=True)
        if error:
            return error
        self.nombre = nombre

        if self.password:
            password = str(self.password).strip()
            error = validar_contraseña(password, 6, 50, "Contraseña")
            if error:
                return error
            self.password = password

        if self.foto_perfil:
            foto = str(self.foto_perfil)
            if len(foto) > 100:
                return "La ruta de la foto de perfil no puede exceder 100 caracteres."

        return None

    # ==================== CONSULTAS ====================

    def listar_usuarios(self):
        db = self.__conexion_bd.conexion2()
        if not db:
            return None
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
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
            """)
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
            cursor.execute("""
                SELECT
                    e.ID_empleado AS cedula,
                    e.Nombre_empleado AS nombre,
                    e.Apellido_empleado AS apellido,
                    CONCAT(e.Nombre_empleado, ' ', e.Apellido_empleado) AS nombre_completo
                FROM Empleado e
                ORDER BY e.ID_empleado ASC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"[ERROR] listar_empleados: {e}")
            traceback.print_exc()
            return None
        finally:
            cursor.close()
            db.close()

    def listar_clientes(self):
        db = self.__conexion_bd.conexion1()
        if not db:
            return None
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    pn.ID_cliente AS cedula,
                    CONCAT(pn.Nombre_cliente, ' ', pn.Apellido_cliente) AS nombre_completo,
                    c.Celular_cliente AS celular,
                    c.Correo_cliente AS correo
                FROM Persona_natural pn
                INNER JOIN Cliente c ON c.ID_cliente = pn.ID_cliente
                ORDER BY pn.ID_cliente ASC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"[ERROR] listar_clientes: {e}")
            traceback.print_exc()
            return None
        finally:
            cursor.close()
            db.close()

    def verificar_empleado(self, cedula: str) -> bool:
        try:
            db = self.__conexion_bd.conexion1()
            if not db:
                return False
            cursor = db.cursor()
            try:
                cursor.execute(
                    "SELECT 1 FROM Empleado WHERE ID_empleado = %s LIMIT 1",
                    (cedula,),
                )
                return cursor.fetchone() is not None
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"[ERROR] verificar_empleado: {e}")
            traceback.print_exc()
            return False

    def verificar_cliente(self, cedula: str) -> bool:
        try:
            db = self.__conexion_bd.conexion1()
            if not db:
                return False
            cursor = db.cursor()
            try:
                cursor.execute(
                    "SELECT 1 FROM Persona_natural WHERE ID_cliente = %s LIMIT 1",
                    (cedula,),
                )
                return cursor.fetchone() is not None
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
        Verifica que la cédula corresponda al tipo de rol.
        - Si el rol es 'cliente', se permite (puede ser un cliente nuevo).
        - Si es empleado, debe existir en la tabla Empleado.
        """
        try:
            if not self.cedula or not self.rol_id:
                return False

            db_usuarios = self.__conexion_bd.conexion2()
            if not db_usuarios:
                return False

            cursor = db_usuarios.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT nombre FROM rol WHERE id = %s",
                    (self.rol_id,),
                )
                rol = cursor.fetchone()
                if not rol:
                    return False

                nombre_rol = rol["nombre"].lower()

                if nombre_rol == "cliente":
                    return True
                return self.verificar_empleado(self.cedula)
            finally:
                cursor.close()
                db_usuarios.close()
        except Exception as e:
            print(f"[ERROR] verificar_rol_y_cedula: {e}")
            traceback.print_exc()
            return False

    # ==================== MUTACIONES ====================

    def agregar_usuario(self) -> str:
        try:
            error = self._validar_datos_usuario(requiere_password=True, requiere_rol=True)
            if error:
                return error

            if self.verificar_usuario_por_nombre():
                return f"El nombre de usuario '{self.nombre}' ya existe."

            if self.verificar_cedula_en_uso(self.cedula):
                return f"La cédula '{self.cedula}' ya está asignada a otro usuario."

            if not self.verificar_rol_y_cedula():
                return "La cédula no corresponde al tipo de rol seleccionado."

            db = self.__conexion_bd.conexion2()
            if not db:
                return "Error al conectar a la base de datos."

            cursor = db.cursor()
            try:
                cursor.execute("SELECT MAX(id) FROM usuario")
                result = cursor.fetchone()
                ultimo_id = result[0] if result else None

                if ultimo_id:
                    try:
                        numero = int(ultimo_id.split('-')[1]) + 1
                        nuevo_id = f"USR-{numero:03d}"
                    except (IndexError, ValueError):
                        cursor.execute(
                            "SELECT MAX(CAST(SUBSTRING(id, 5) AS UNSIGNED)) FROM usuario WHERE id LIKE 'USR-%'"
                        )
                        result_max = cursor.fetchone()
                        max_num = result_max[0] if result_max and result_max[0] else 0
                        nuevo_id = f"USR-{max_num + 1:03d}"
                else:
                    nuevo_id = "USR-001"

                password_hash = self._hash_password(self.password)

                cursor.execute(
                    """
                    INSERT INTO usuario (id, nombre, cedula, password, rol_id, activo, foto_perfil)
                    VALUES (%s, %s, %s, %s, %s, 1, %s)
                    """,
                    (nuevo_id, self.nombre, self.cedula, password_hash, self.rol_id, self.foto_perfil or None),
                )
                db.commit()
                self.id = nuevo_id

                if self.usuario_id:
                    Bitacora(
                        accion="Crear usuario",
                        descripcion=f"Se creó el usuario: {self.nombre} - Cédula: {self.cedula} - Rol ID: {self.rol_id}",
                        usuario_id=self.usuario_id,
                        modulo_nombre="Usuarios"
                    ).registrar()

                return "Usuario agregado exitosamente."
            except Exception as e:
                print(f"[ERROR] Error en INSERT de usuario: {e}")
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
            usuario_id = str(self.id).strip() if self.id else ""
            if not usuario_id:
                return "El ID del usuario es obligatorio."

            error = self._validar_datos_usuario(requiere_password=False, requiere_rol=True)
            if error:
                return error

            if not self.verificar_usuario_por_id():
                return f"El usuario con ID {usuario_id} no existe."

            if self.verificar_cedula_en_uso(self.cedula, usuario_id):
                return f"La cédula '{self.cedula}' ya está asignada a otro usuario."

            if not self.verificar_rol_y_cedula():
                return "La cédula no corresponde al tipo de rol seleccionado."

            db = self.__conexion_bd.conexion2()
            if not db:
                return "Error al conectar a la base de datos."

            cursor = db.cursor()
            try:
                if self.password:
                    password_hash = self._hash_password(self.password)
                    cursor.execute(
                        """
                        UPDATE usuario
                        SET nombre = %s, cedula = %s, password = %s, rol_id = %s, foto_perfil = %s
                        WHERE id = %s
                        """,
                        (self.nombre, self.cedula, password_hash, self.rol_id, self.foto_perfil or None, usuario_id),
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE usuario
                        SET nombre = %s, cedula = %s, rol_id = %s, foto_perfil = %s
                        WHERE id = %s
                        """,
                        (self.nombre, self.cedula, self.rol_id, self.foto_perfil or None, usuario_id),
                    )
                db.commit()

                if self.usuario_id:
                    Bitacora(
                        accion="Actualizar usuario",
                        descripcion=f"Se actualizó el usuario ID: {usuario_id} - Nuevo nombre: {self.nombre} - Rol ID: {self.rol_id}",
                        usuario_id=self.usuario_id,
                        modulo_nombre="Usuarios"
                    ).registrar()

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
            usuario_id = str(self.id).strip() if self.id else ""
            if not usuario_id:
                return "El identificador del usuario no puede estar vacío."

            if not self.verificar_usuario_por_id():
                return f"El usuario con identificador {usuario_id} no existe."

            db = self.__conexion_bd.conexion2()
            if not db:
                return "Error al conectar a la base de datos."

            cursor = db.cursor(dictionary=True)
            try:
                cursor.execute("""
                    SELECT COUNT(*) as total
                    FROM usuario u
                    INNER JOIN rol r ON r.id = u.rol_id
                    WHERE r.nombre = 'admin'
                """)
                result = cursor.fetchone()
                total_admins = result["total"] if result else 0

                cursor.execute("""
                    SELECT r.nombre as rol_nombre, u.nombre as usuario_nombre
                    FROM usuario u
                    INNER JOIN rol r ON r.id = u.rol_id
                    WHERE u.id = %s
                """, (usuario_id,))
                usuario_rol = cursor.fetchone()

                if usuario_rol and usuario_rol["rol_nombre"].lower() == "admin" and total_admins <= 1:
                    return "No se puede eliminar el único administrador del sistema."

                nombre_usuario = usuario_rol["usuario_nombre"] if usuario_rol else "N/A"

                cursor.execute("DELETE FROM usuario WHERE id = %s", (usuario_id,))
                db.commit()

                if self.usuario_id:
                    Bitacora(
                        accion="Eliminar usuario",
                        descripcion=f"Se eliminó el usuario ID: {usuario_id} - Nombre: {nombre_usuario}",
                        usuario_id=self.usuario_id,
                        modulo_nombre="Usuarios"
                    ).registrar()

                return "Usuario eliminado exitosamente."
            except Exception as e:
                print(f"[ERROR] Error al eliminar usuario: {e}")
                traceback.print_exc()
                db.rollback()
                return "Error al eliminar usuario. Verifica que no esté en uso."
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"[ERROR] Error en eliminar_usuario: {e}")
            traceback.print_exc()
            return f"Error en eliminar_usuario: {str(e)}"

    def obtener_rol_por_nombre(self, nombre_rol: str = None):
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
        db = self.__conexion_bd.conexion2()
        if not db:
            return None
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT u.id, u.nombre, u.cedula, u.password, u.rol_id, u.foto_perfil, r.nombre AS rol_nombre
                FROM usuario u
                INNER JOIN rol r ON u.rol_id = r.id
                WHERE u.nombre = %s AND u.activo = 1
            """, (nombre,))
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
            cursor.execute("""
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
            """, (id_buscar,))
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
            self.nombre = nombre
            self.password = password or ""
            self.foto_perfil = foto_perfil or ""

            if not usuario_id:
                return "El ID del usuario es obligatorio."

            error = self._validar_perfil()
            if error:
                return error

            db = self.__conexion_bd.conexion2()
            if not db:
                return "Error al conectar a la base de datos."

            cursor = db.cursor()
            try:
                if self.password:
                    password_hash = self._hash_password(self.password)
                    cursor.execute(
                        """
                        UPDATE usuario
                        SET nombre = %s, password = %s, foto_perfil = %s
                        WHERE id = %s
                        """,
                        (self.nombre, password_hash, self.foto_perfil or None, usuario_id),
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE usuario
                        SET nombre = %s, foto_perfil = %s
                        WHERE id = %s
                        """,
                        (self.nombre, self.foto_perfil or None, usuario_id),
                    )
                db.commit()

                if self.usuario_id:
                    Bitacora(
                        accion="Actualizar perfil",
                        descripcion="Usuario actualizó su perfil",
                        usuario_id=self.usuario_id,
                        modulo_nombre="Usuarios"
                    ).registrar()

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