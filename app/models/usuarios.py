from app.models.database import conectar


class Usuarios(conectar):
    def validar(self, nombre, password):
        db = self.conexion2()
        if db:
            cursor = db.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT usuario.*, usuario.cedula AS cedula_personal, rol.nombre AS nombre_rol"
                    " FROM usuario"
                    " JOIN rol ON usuario.rol_id = rol.id"
                    " WHERE usuario.nombre = %s AND usuario.password = %s",
                    (nombre, password),
                )
                resultados = cursor.fetchall()
                return resultados
            finally:
                cursor.close()
                db.close()
        else:
            return None

    def _consultar(self, query, params=None):
        db = self.conexion2()
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
        db = self.conexion2()
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

    # ==================== EMPLEADOS ====================

    def listar_empleados(self):
        db = self.conexion1()
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

    def verificar_empleado(self, cedula):
        db = self.conexion1()
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

    # ==================== USUARIOS ====================

    def listar_usuarios(self):
        return self._consultar(
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

    def crear_usuario(self, nombre, cedula_personal, password, rol_id, foto_perfil=None):
        db = self.conexion2()
        if not db:
            return None

        cursor = db.cursor()
        try:
            cursor.callproc(
                "sp_registrar_usuario_con_prefijo",
                [nombre, cedula_personal, password, rol_id, foto_perfil],
            )

            db.commit()
            for resultado in cursor.stored_results():
                fila = resultado.fetchone()
                if fila:
                    if isinstance(fila, dict):
                        return fila.get("id_generado")
                    return fila[0]

            return None
        finally:
            cursor.close()
            db.close()

    def actualizar_usuario(self, usuario_id, nombre, cedula_personal, rol_id, foto_perfil=None):
        return self._ejecutar(
            """
            UPDATE usuario
            SET nombre = %s,
                cedula = %s,
                rol_id = %s,
                foto_perfil = %s
            WHERE id = %s
            """,
            (nombre, cedula_personal, rol_id, foto_perfil, usuario_id),
        )

    def actualizar_usuario_con_password(self, usuario_id, nombre, cedula_personal, password, rol_id, foto_perfil=None):
        return self._ejecutar(
            """
            UPDATE usuario
            SET nombre = %s,
                cedula = %s,
                password = %s,
                rol_id = %s,
                foto_perfil = %s
            WHERE id = %s
            """,
            (nombre, cedula_personal, password, rol_id, foto_perfil, usuario_id),
        )

    def eliminar_usuario(self, usuario_id):
        return self._ejecutar("DELETE FROM usuario WHERE id = %s", (usuario_id,))

    def obtener_usuario_por_id(self, usuario_id):
        datos = self._consultar(
            """
            SELECT
                u.id,
                u.nombre,
                u.cedula AS cedula_personal,
                u.rol_id,
                u.foto_perfil,
                r.nombre AS rol_nombre
            FROM usuario u
            INNER JOIN rol r ON r.id = u.rol_id
            WHERE u.id = %s
            LIMIT 1
            """,
            (usuario_id,),
        )
        return datos[0] if datos else None

    def actualizar_perfil_actual(self, usuario_id, nombre, password=None, foto_perfil=None):
        if password:
            return self._ejecutar(
                """
                UPDATE usuario
                SET nombre = %s,
                    password = %s,
                    foto_perfil = %s
                WHERE id = %s
                """,
                (nombre, password, foto_perfil, usuario_id),
            )

        return self._ejecutar(
            """
            UPDATE usuario
            SET nombre = %s,
                foto_perfil = %s
            WHERE id = %s
            """,
            (nombre, foto_perfil, usuario_id),
        )

    # ==================== ROLES ====================

    def listar_roles(self):
        return self._consultar(
            """
            SELECT id, nombre, descripcion
            FROM rol
            ORDER BY nombre
            """
        )

    def crear_rol(self, nombre, descripcion):
        return self._ejecutar(
            "INSERT INTO rol (nombre, descripcion) VALUES (%s, %s)",
            (nombre, descripcion),
        )

    def actualizar_rol(self, rol_id, nombre, descripcion):
        return self._ejecutar(
            "UPDATE rol SET nombre = %s, descripcion = %s WHERE id = %s",
            (nombre, descripcion, rol_id),
        )

    def eliminar_rol(self, rol_id):
        return self._ejecutar("DELETE FROM rol WHERE id = %s", (rol_id,))

    def obtener_rol_por_nombre(self, nombre_rol):
        datos = self._consultar(
            """
            SELECT id, nombre
            FROM rol
            WHERE LOWER(nombre) = LOWER(%s)
            LIMIT 1
            """,
            (nombre_rol,),
        )
        return datos[0] if datos else None

    # ==================== MÓDULOS ====================

    def listar_modulos(self):
        return self._consultar(
            """
            SELECT id, nombre, descripcion
            FROM modulo
            ORDER BY nombre
            """
        )

    def crear_modulo(self, nombre, descripcion):
        return self._ejecutar(
            "INSERT INTO modulo (nombre, descripcion) VALUES (%s, %s)",
            (nombre, descripcion),
        )

    def actualizar_modulo(self, modulo_id, nombre, descripcion):
        return self._ejecutar(
            "UPDATE modulo SET nombre = %s, descripcion = %s WHERE id = %s",
            (nombre, descripcion, modulo_id),
        )

    def eliminar_modulo(self, modulo_id):
        return self._ejecutar("DELETE FROM modulo WHERE id = %s", (modulo_id,))

    # ==================== PERMISOS ====================

    def listar_permisos_por_rol(self, rol_id):
        """Obtiene todos los permisos de un rol específico"""
        return self._consultar(
            """
            SELECT
                p.rol_id,
                p.modulo_id,
                m.nombre AS modulo_nombre,
                m.descripcion AS modulo_descripcion,
                p.consultar,
                p.registrar,
                p.modificar,
                p.eliminar
            FROM permiso p
            INNER JOIN modulo m ON m.id = p.modulo_id
            WHERE p.rol_id = %s
            ORDER BY m.nombre
            """,
            (rol_id,)
        )

    def guardar_permiso(self, rol_id, modulo_id, registrar, modificar, eliminar):
        return self._ejecutar(
            """
            INSERT INTO permiso (rol_id, modulo_id, registrar, modificar, eliminar)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                registrar = VALUES(registrar),
                modificar = VALUES(modificar),
                eliminar = VALUES(eliminar)
            """,
            (rol_id, modulo_id, registrar, modificar, eliminar),
        )