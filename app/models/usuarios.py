from app.models.database import conectar

class Usuarios(conectar):

    def _consulta_usuario_base(self):
        return (
            "SELECT usuario.id, usuario.nombre, usuario.cedula AS cedula_personal, "
            "usuario.password, usuario.rol_id, usuario.activo, usuario.fecha_creacion, "
            "usuario.foto_perfil, usuario.ultima_actualizacion, rol.nombre AS nombre_rol "
            "FROM usuario "
            "JOIN rol ON usuario.rol_id = rol.id"
        )

    def consultar_usuario(self):
        db = self.conexion2()
        if db:
            cursor = db.cursor(dictionary=True)
            try:
                query = self._consulta_usuario_base() + " ORDER BY usuario.fecha_creacion DESC, usuario.id DESC"
                cursor.execute(query)
                resultados = cursor.fetchall()
                return resultados
            finally:
                cursor.close()
                db.close()
        else:
            return None

    def validar(self, nombre, password):
        db = self.conexion2()
        if db:
            cursor = db.cursor(dictionary=True)
            try:
                query = self._consulta_usuario_base() + " WHERE usuario.nombre = %s AND usuario.password = %s"
                cursor.execute(query, (nombre, password))
                resultados = cursor.fetchall()
                return resultados
            finally:
                cursor.close()
                db.close()
        else:
            return None
        

