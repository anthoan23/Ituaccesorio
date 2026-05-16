from app.models.database import conectar

class Usuarios(conectar):

    def validar(self, nombre, password):
        db = self.conexion2()
        if db:
            cursor = db.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT usuario.*, rol.nombre AS nombre_rol"
                    " FROM usuario"
                    " JOIN rol ON usuario.rol_id = rol.id"
                    " WHERE usuario.nombre = %s AND usuario.password = %s",
                    (nombre, password)
                )
                resultados = cursor.fetchall()
                return resultados
            finally:
                cursor.close()
                db.close()
        else:
            return None

