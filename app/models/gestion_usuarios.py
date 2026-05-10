from app.models.database import conectar


class GestionUsuarios(conectar):
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

    def listar_usuarios(self):
        return self._consultar(
            """
            SELECT
                u.id,
                u.nombre,
                u.cedula_personal,
                u.rol_id,
                r.nombre AS rol_nombre,
                u.fecha_creacion,
                u.foto_perfil
            FROM usuario u
            INNER JOIN rol r ON r.id = u.rol_id
            ORDER BY u.id DESC
            """
        )

    def crear_usuario(self, nombre, cedula_personal, password, rol_id, foto_perfil=None):
        return self._ejecutar(
            """
            INSERT INTO usuario (nombre, cedula_personal, password, rol_id, foto_perfil)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (nombre, cedula_personal, password, rol_id, foto_perfil),
        )

    def actualizar_usuario(self, usuario_id, nombre, cedula_personal, rol_id, foto_perfil=None):
        return self._ejecutar(
            """
            UPDATE usuario
            SET nombre = %s,
                cedula_personal = %s,
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
                cedula_personal = %s,
                password = %s,
                rol_id = %s,
                foto_perfil = %s
            WHERE id = %s
            """,
            (nombre, cedula_personal, password, rol_id, foto_perfil, usuario_id),
        )

    def eliminar_usuario(self, usuario_id):
        return self._ejecutar("DELETE FROM usuario WHERE id = %s", (usuario_id,))

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

    def listar_permisos(self):
        return self._consultar(
            """
            SELECT
                p.rol_id,
                r.nombre AS rol_nombre,
                p.modulo_id,
                m.nombre AS modulo_nombre,
                p.registrar,
                p.modificar,
                p.eliminar
            FROM permiso p
            INNER JOIN rol r ON r.id = p.rol_id
            INNER JOIN modulo m ON m.id = p.modulo_id
            ORDER BY r.nombre, m.nombre
            """
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

    def eliminar_permiso(self, rol_id, modulo_id):
        return self._ejecutar(
            "DELETE FROM permiso WHERE rol_id = %s AND modulo_id = %s",
            (rol_id, modulo_id),
        )
