from __future__ import annotations

from app.models.database import conectar

class Tests(conectar):

    def buscar_test(self, id_orden: int):
        db = self.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            sql = (
                "SELECT o.ID_orden , t.* FROM revision_orden o JOIN test t ON o.ID_test = t.ID_test WHERE o.ID_orden = %s"
            )
            cursor.execute(sql, (id_orden,))
            ordenes = cursor.fetchall()
        
            return ordenes
        
        finally:
            cursor.close()
            db.close()
    
    def registrar_test(self, datos, id_orden):
        """
        Registra los resultados de un test en la base de datos.
        'datos' debe ser una tupla o lista con los 21 valores en el orden correcto.
        """
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            sql = (
                "INSERT INTO test ("
                "ID_em, Num_test, Btn_power, Btn_vol, Cornetas, Mica, LCD, Tactil, Wifi, "
                "Puerto_carga, Cam_pos, Cam_del, Microfono, Flash, Btn_sil, Auricular, "
                "Senal, Sensor_proximidad, Face_id, Bluetooth, Observaciones, Fecha"
                ") VALUES ("
                "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()"
                ")"
            )
            
            cursor.execute(sql, datos)

            sql_ordenes = "INSERT INTO revision_orden (ID_orden, ID_test) VALUES (%s, %s)"
            cursor.execute(sql_ordenes, (id_orden, cursor.lastrowid))

            sql_update_orden = "UPDATE orden_e SET Estado_o = 'Revisado' WHERE ID_orden_e = %s"
           
            cursor.execute(sql_update_orden, (id_orden,))
            db.commit()  # Confirma los cambios en la base de datos
            return True
            
        except Exception as e:
            print(f"Error al registrar el test: {e}")
            db.rollback()  # Cancela la operación si hubo un error
            return False
            
        finally:
            cursor.close()
            db.close()


    