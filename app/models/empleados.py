from __future__ import annotations

from datetime import date

from app.models.database import conectar

class Empleados(conectar):
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
                    e.ID_cargo AS id_cargo,
                    e.Nombre_empleado AS nombre,
                    e.Apellido_empleado AS apellido,
                    e.Celular_empleado AS celular,
                    e.Correo_empleado AS correo,
                    e.Direccion_empleado AS direccion,
                    c.N_cargo AS cargo_nombre,
                    GROUP_CONCAT(DISTINCT esp.ID_especialidad) AS especialidades_ids,
                    GROUP_CONCAT(DISTINCT esp.N_especialidad) AS especialidades_nombres
                FROM Empleado e
                JOIN cargo c ON e.ID_cargo = c.ID_cargo
                LEFT JOIN capacitacion cap ON e.ID_empleado = cap.ID_empleado
                LEFT JOIN especialidad esp ON cap.ID_especialidad = esp.ID_especialidad
                GROUP BY e.ID_empleado
                ORDER BY e.ID_empleado ASC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def listar_tecnicos(self):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    e.ID_empleado AS id,
                    e.Nombre_empleado AS nombre,
                    e.Apellido_empleado AS apellido,
                    c.N_cargo AS cargo
                FROM Empleado e
                JOIN cargo c ON e.ID_cargo = c.ID_cargo
                WHERE LOWER(c.N_cargo) = 'tecnico'
                ORDER BY e.Nombre_empleado ASC, e.Apellido_empleado ASC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()
    


    def listar_especialidades(self):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    ID_especialidad AS id,
                    N_especialidad AS nombre
                FROM Especialidad
                ORDER BY ID_especialidad ASC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def agregar_empleado(
        self,
        cedula: str,
        cargo_id: str,
        nombre: str,
        apellido: str,
        celular: str,
        correo: str,
        direccion: str,
        especialidades: list | None = None,
    ) -> bool:
        # Solo insertar si el empleado NO existe
        if self.verificar_empleado(cedula):
            mensaje = f"El empleado con cédula la {cedula} ya existe."
            return mensaje

        db = self.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje

        cursor = db.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO empleado (ID_empleado, ID_cargo, Nombre_empleado, Apellido_empleado, Celular_empleado, Correo_empleado, Direccion_empleado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (cedula, cargo_id, nombre, apellido, celular, correo, direccion),
            )

            # insert especialidades associations if provided
            if especialidades:
                for esp_id in especialidades:
                    try:
                        cursor.execute(
                            "INSERT INTO capacitacion (ID_especialidad, ID_empleado) VALUES (%s, %s)",
                            (esp_id, cedula),
                        )
                    except Exception:
                        # skip individual inserts but continue
                        pass

            db.commit()
            mensaje = "Empleado agregado exitosamente."
            return mensaje
        except Exception as e:
            print(f"Error al agregar empleado: {e}")
            db.rollback()
            mensaje = "Error al agregar empleado."
            return mensaje
        finally:
            cursor.close()
            db.close()



    def agregar_especialidad(self, especialidad: str) -> str:       # ID_espesialidad es AUTO_INCREMENT, así que solo se inserta el nombre.     

        if self.verificar_espesialidad(especialidad):
            mensaje = f"La especialidad '{especialidad}' ya existe."
            return mensaje
        
        db = self.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje

        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO Especialidad (N_especialidad) VALUES (%s)",
                (especialidad,),
            )
            db.commit()
            mensaje = f"Especialidad agregada exitosamente. ID: {cursor.lastrowid}."
            return mensaje
        except Exception as e:
            print(f"Error al agregar especialidad: {e}")
            db.rollback()
            mensaje = "Error al agregar especialidad."
            return mensaje
        finally:
            cursor.close()
            db.close()

    
    def eliminar_empleado(self, id_em: str) -> str:
        
        if not self.verificar_empleado(id_em):
            return f"El empleado con identificador {id_em} no existe."

        db = self.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje

        cursor = db.cursor()
        try:
            cursor.execute(
                "DELETE FROM Empleado WHERE ID_empleado = %s",
                (id_em,),
            )
            db.commit()
            mensaje = "Empleado eliminado exitosamente."
            return mensaje
        except Exception as e:
            print(f"Error al eliminar empleado: {e}")
            db.rollback()
            mensaje = "Error al eliminar empleado."
            return mensaje
        finally:
            cursor.close()
            db.close()



    def eliminar_especialidad(self, n_especialidad: str) -> str:
        # verificar existencia
        if not self.verificar_espesialidad(n_especialidad):
            return f"La especialidad con identificador {n_especialidad} no existe."

        db = self.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje

        cursor = db.cursor()
        try:
            cursor.execute(
                "DELETE FROM Especialidad WHERE N_especialidad = %s",
                (n_especialidad,),
            )
            db.commit()
            mensaje = "Especialidad eliminada exitosamente."
            return mensaje
        except Exception as e:
            print(f"Error al eliminar especialidad: {e}")
            db.rollback()
            mensaje = "Error al eliminar especialidad."
            return mensaje
        finally:
            cursor.close()
            db.close()
    
    def actualizar_empleado(
        self,
        id_empleado: str,
        cargo_id: str,
        nombre: str,
        apellido: str,
        celular: str,
        correo: str,
        direccion: str,
        especialidades: list | None = None,
    ) -> str:
        # verificar existencia del registro original
        if not self.verificar_empleado(id_empleado):
            return f"El empleado con identificador {id_empleado} no existe."

        db = self.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                """
                UPDATE empleado
                SET ID_empleado = %s, ID_cargo = %s, Nombre_empleado = %s, Apellido_empleado = %s, Celular_empleado = %s, Correo_empleado = %s, Direccion_empleado = %s
                WHERE ID_empleado = %s
                """,
                (id_empleado, cargo_id, nombre, apellido, celular, correo, direccion, id_empleado),
            )
            # update specialties associations if provided
            if especialidades is not None:
                try:
                    cursor.execute(
                        "DELETE FROM Capacitacion WHERE ID_empleado = %s",
                        (id_empleado,),
                    )
                except Exception:
                    pass

                for esp_id in especialidades:
                    try:
                        cursor.execute(
                            "INSERT INTO Capacitacion (ID_especialidad, ID_empleado) VALUES (%s, %s)",
                            (esp_id, id_empleado),
                        )
                    except Exception:
                        pass

            db.commit()
            return "Empleado actualizado exitosamente."
        except Exception as e:
            print(f"Error al actualizar empleado: {e}")
            db.rollback()
            return "Error al actualizar empleado."
        finally:
            cursor.close()
            db.close()

    def actualizar_cargo(self, id_cargo: int, cargo_n: str, cargo_v: str) -> str:
        # verificar existencia
        if not self.verificar_cargo(cargo_v):
            return f"El cargo con identificador {cargo_v} no existe."
        
        if cargo_v == "Tecnico":
            return False

        db = self.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE cargo SET N_cargo = %s WHERE ID_cargo = %s",
                (cargo_n, id_cargo),
            )
            db.commit()
            return "Cargo modificado exitosamente."
        except Exception as e:
            print(f"Error al actualizar cargo: {e}")
            db.rollback()
            return "Error al actualizar cargo."
        finally:
            cursor.close()
            db.close()
    
    def actualizar_especialidad(self, id_especialidad: int, especialidad_n: str, especialidad_v: str) -> str:
        # verificar existencia
        if not self.verificar_espesialidad(especialidad_v):
            return f"La especialidad con nombre {especialidad_v} no existe."

        db = self.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE especialidad SET N_especialidad = %s WHERE ID_especialidad = %s",
                (especialidad_n, id_especialidad),
            )
            db.commit()
            return "Especialidad modificada exitosamente."
        except Exception as e:
            print(f"Error al actualizar especialidad: {e}")
            db.rollback()
            return "Error al actualizar especialidad."
        finally:
            cursor.close()
            db.close()
            

    def verificar_empleado(self, cedula: str) -> bool:
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


    def verificar_espesialidad(self, especialidad: str) -> bool:
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM Especialidad WHERE N_especialidad = %s LIMIT 1",
                (especialidad,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()
   
