from app.models.database import conectar

class Prueba_bd(conectar):
    def prueba_consultar_bd1(self):
        db = self.conexion1()
        if db:
            cursor = db.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM cliente")
                resultados = cursor.fetchall()
                return resultados
            finally:
                cursor.close()
                db.close()
        else:
            return None
    
    def prueba_agregar_bd1(self, id, nombre, apellido, celular, correo, direccion, tipo):
        db = self.conexion1()
        if db:
            cursor = db.cursor()
            try:
                sql = "INSERT INTO cliente (ID_c, Nombre_c, Apellido_c, Celular_c, Correo_c, Direccion_c, Tipo_c) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                valores = (id, nombre, apellido, celular, correo, direccion, tipo)
                cursor.execute(sql, valores)
                db.commit()
                return True
            finally:
                cursor.close()
                db.close()
        else:
            return False

    def prueba_editar_bd1(self, id, nombre, apellido, celular, correo, direccion, tipo):
        db = self.conexion1()
        if db:
            cursor = db.cursor()
            try:
                sql = (
                    "UPDATE cliente SET Nombre_c = %s, Apellido_c = %s, Celular_c = %s, "
                    "Correo_c = %s, Direccion_c = %s, Tipo_c = %s WHERE ID_c = %s"
                )
                valores = (nombre, apellido, celular, correo, direccion, tipo, id)
                cursor.execute(sql, valores)
                db.commit()
                return cursor.rowcount > 0
            finally:
                cursor.close()
                db.close()
        else:
            return False
        
    def prueba_eliminar_bd1(self, id):
        db = self.conexion1()
        if db:
            cursor = db.cursor()
            try:
                sql = "DELETE FROM cliente WHERE ID_c = %s"
                cursor.execute(sql, (id,))
                db.commit()
                return cursor.rowcount > 0
            finally:
                cursor.close()
                db.close()
        else:
            return False
        
    def prueba_consultar_bd2(self):
        db = self.conexion2()
        if db:
            cursor = db.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM modulo")
                resultados = cursor.fetchall()
                return resultados
            finally:
                cursor.close()
                db.close()
        else:
            return None

    def prueba_agregar_bd2(self, nombre, descripcion):
        db = self.conexion2()
        if db:
            cursor = db.cursor()
            try:
                sql = "INSERT INTO modulo (nombre, descripcion) VALUES (%s, %s)"
                valores = (nombre, descripcion)
                cursor.execute(sql, valores)
                db.commit()
                return True
            finally:
                cursor.close()
                db.close()
        else:
            return False

    def prueba_editar_bd2(self, id, nombre, descripcion):
        db = self.conexion2()
        if db:
            cursor = db.cursor()
            try:
                sql = "UPDATE modulo SET nombre = %s, descripcion = %s WHERE id = %s"
                valores = (nombre, descripcion, id)
                cursor.execute(sql, valores)
                db.commit()
                return cursor.rowcount > 0
            finally:
                cursor.close()
                db.close()
        else:
            return False

    def prueba_eliminar_bd2(self, id):
        db = self.conexion2()
        if db:
            cursor = db.cursor()
            try:
                sql = "DELETE FROM modulo WHERE id = %s"
                cursor.execute(sql, (id,))
                db.commit()
                return cursor.rowcount > 0
            finally:
                cursor.close()
                db.close()
        else:
            return False
        
