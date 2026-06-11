from __future__ import annotations

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.database import conectar


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
    ):
        self.id = id
        self.nombre = nombre
        self.cedula = cedula
        self.password = password
        self.rol_id = rol_id
        self.foto_perfil = foto_perfil
        self.activo = activo
        self.fecha_creacion = fecha_creacion

        self.__conexion_bd = conectar()

    def _hash_password(self, password: str) -> str:
        """Genera un hash de la contraseña"""
        return generate_password_hash(password)

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica si la contraseña coincide con el hash"""
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
            # CORREGIDO: Usar los nombres correctos de columnas
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
        finally:
            cursor.close()
            db.close()

    def verificar_empleado(self, cedula: str) -> bool:
        db = self.__conexion_bd.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            # La columna es 'ID_empleado'
            cursor.execute(
                "SELECT 1 FROM Empleado WHERE ID_empleado = %s LIMIT 1",
                (cedula,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    def verificar_cliente(self, cedula: str) -> bool:
        """Verifica si una cédula pertenece a un cliente registrado"""
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
        finally:
            cursor.close()
            db.close()

    def verificar_cedula_en_uso(self, cedula: str, usuario_id: str = None) -> bool:
        """Verifica si una cédula ya está asignada a otro usuario"""
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
        finally:
            cursor.close()
            db.close()

    def agregar_usuario(self) -> str:
        nombre = self.nombre.strip()
        cedula = self.cedula.strip()
        password = self.password.strip()
        rol_id = self.rol_id.strip()
        foto_perfil = self.foto_perfil or None

        # Validaciones
        if not nombre or not cedula or not password or not rol_id:
            return "Nombre, cédula, contraseña y rol son obligatorios."

        if len(nombre) > 50:
            return "El nombre no puede exceder los 50 caracteres."

        if len(password) < 6:
            return "La contraseña debe tener al menos 6 caracteres."

        if len(password) > 50:
            return "La contraseña no puede exceder los 50 caracteres."

        if self.verificar_usuario_por_nombre():
            return f"El nombre de usuario '{nombre}' ya existe."

        if self.verificar_cedula_en_uso(cedula):
            return f"La cédula '{cedula}' ya está asignada a otro usuario."

        # Verificar si la cédula pertenece a un empleado o cliente según el rol
        if not self.verificar_rol_y_cedula():
            return "La cédula no corresponde al tipo de rol seleccionado."

        db = self.__conexion_bd.conexion2()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            password_hash = self._hash_password(password)
            cursor.execute(
                """
                INSERT INTO usuario (nombre, cedula, password, rol_id, foto_perfil)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (nombre, cedula, password_hash, rol_id, foto_perfil),
            )
            db.commit()
            self.id = str(cursor.lastrowid)
            return f"Usuario agregado exitosamente."
        except Exception as e:
            print(f"Error al agregar usuario: {e}")
            db.rollback()
            return "Error al agregar usuario."
        finally:
            cursor.close()
            db.close()

    def actualizar_usuario(self) -> str:
        usuario_id = self.id.strip()
        nombre = self.nombre.strip()
        cedula = self.cedula.strip()
        rol_id = self.rol_id.strip()
        foto_perfil = self.foto_perfil or None
        password = self.password.strip() if self.password else None

        if not usuario_id or not nombre or not cedula or not rol_id:
            return "ID, nombre, cédula y rol son obligatorios."

        if len(nombre) > 50:
            return "El nombre no puede exceder los 50 caracteres."

        if not self.verificar_usuario_por_id():
            return f"El usuario con ID {usuario_id} no existe."

        if self.verificar_cedula_en_uso(cedula, usuario_id):
            return f"La cédula '{cedula}' ya está asignada a otro usuario."

        # Verificar si la cédula pertenece a un empleado o cliente según el rol
        if not self.verificar_rol_y_cedula():
            return "La cédula no corresponde al tipo de rol seleccionado."

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
            return "Usuario actualizado exitosamente."
        except Exception as e:
            print(f"Error al actualizar usuario: {e}")
            db.rollback()
            return "Error al actualizar usuario."
        finally:
            cursor.close()
            db.close()

    def eliminar_usuario(self) -> str:
        usuario_id = self.id.strip()

        if not usuario_id:
            return "El identificador del usuario no puede estar vacío."

        if not self.verificar_usuario_por_id():
            return f"El usuario con identificador {usuario_id} no existe."

        # Verificar que no sea el último admin
        db = self.__conexion_bd.conexion2()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor(dictionary=True)
        try:
            # Verificar si es admin y si es el único
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
                SELECT r.nombre as rol_nombre
                FROM usuario u
                INNER JOIN rol r ON r.id = u.rol_id
                WHERE u.id = %s
                """,
                (usuario_id,),
            )
            usuario_rol = cursor.fetchone()

            if usuario_rol and usuario_rol["rol_nombre"].lower() == "admin" and total_admins <= 1:
                return "No se puede eliminar el único administrador del sistema."

            cursor.execute("DELETE FROM usuario WHERE id = %s", (usuario_id,))
            db.commit()
            return "Usuario eliminado exitosamente."
        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            db.rollback()
            return "Error al eliminar usuario. Verifica que no esté en uso."
        finally:
            cursor.close()
            db.close()

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
        finally:
            cursor.close()
            db.close()

    def verificar_rol_y_cedula(self) -> bool:
        """Verifica que la cédula corresponda al tipo de rol seleccionado"""
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
                return self.verificar_cliente(self.cedula)
            else:
                return self.verificar_empleado(self.cedula)
        finally:
            cursor.close()
            db_usuarios.close()

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
                # No devolver el hash de la contraseña
                usuario.pop("password", None)
                return usuario

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
        finally:
            cursor.close()
            db.close()

    def actualizar_perfil(self, usuario_id: str, nombre: str, password: str = None, foto_perfil: str = None) -> str:
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
            return "Perfil actualizado exitosamente."
        except Exception as e:
            print(f"Error al actualizar perfil: {e}")
            db.rollback()
            return "Error al actualizar perfil."
        finally:
            cursor.close()
            db.close()