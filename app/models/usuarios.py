from app.models.database import conectar

class Usuarios(conectar):

    def validar(self, nombre, password):
        db = self.conexion2()
        if db:
            cursor = db.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM usuario WHERE nombre = %s AND password = %s", (nombre, password))
                resultados = cursor.fetchall()
                return resultados
            finally:
                cursor.close()
                db.close()
        else:
            return None
        

