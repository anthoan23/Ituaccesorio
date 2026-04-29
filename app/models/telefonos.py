from app.models.database import conectar

class Telefonos(conectar):
    def obtener_telefonos(self):
        db = self.conexion1()
        if db:
            cursor = db.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM telefonos")
                resultados = cursor.fetchall()
                return resultados
            finally:
                cursor.close()
                db.close()
        else:
            return None
        
    def agregar_telefono(self, cod_telefono, marca, modelo):
        db = self.conexion1()
        if db:
            cursor = db.cursor()
            try:
                sql = "INSERT INTO telefonos (cod_telefono, marca, modelo) VALUES (%s, %s, %s)"
                valores = (cod_telefono, marca, modelo)
                cursor.execute(sql, valores)
                db.commit()
                return True
            finally:
                cursor.close()
                db.close()
        else:
            return False
        
    def eliminar_telefono(self, cod_telefono):
        db = self.conexion1()
        if db:
            cursor = db.cursor()
            try:
                sql = "DELETE FROM telefonos WHERE cod_telefono = %s"
                cursor.execute(sql, (cod_telefono,))
                db.commit()
                return cursor.rowcount > 0
            finally:
                cursor.close()
                db.close()
        else:
            return False
        
    def actualizar_telefono(self, cod_telefono, marca, modelo):
        db = self.conexion1()
        if db:
            cursor = db.cursor()
            try:
                sql = "UPDATE telefonos SET marca = %s, modelo = %s WHERE cod_telefono = %s"
                valores = (marca, modelo, cod_telefono)
                cursor.execute(sql, valores)
                db.commit()
                return cursor.rowcount > 0
            finally:
                cursor.close()
                db.close()
        else:
            return False

