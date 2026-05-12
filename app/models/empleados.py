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
                    ID_em AS cedula,
                    Nombre_em AS nombre,
                    Apellido_em AS apellido,
                    Celular_em AS celular,
                    Correo_em AS correo,
                    Direccion_em AS direccion
                FROM empleado
                ORDER BY ID_em ASC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()
    
    def listar_cargos(self):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    ID_cargo AS id,
                    N_cargo AS nombre
                FROM cargo
                ORDER BY ID_cargo ASC
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
                FROM especialidad
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
        nombre: str,
        apellido: str,
        celular: str,
        correo: str,
        direccion: str,
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
                INSERT INTO empleado (ID_em, Nombre_em, Apellido_em, Celular_em, Correo_em, Direccion_em)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (cedula, nombre, apellido, celular, correo, direccion),
            )
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

    def agregar_cargo(self, cargo: str) -> str:
        # ID_cargo es AUTO_INCREMENT, así que solo se inserta el nombre.
        if self.verificar_cargo(cargo):
            mensaje = f"El cargo '{cargo}' ya existe."
            return mensaje

        db = self.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje

        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO cargo (N_cargo) VALUES (%s)",
                (cargo,),
            )
            db.commit()
            mensaje = f"Cargo agregado exitosamente. ID: {cursor.lastrowid}."
            return mensaje
        except Exception as e:
            print(f"Error al agregar cargo: {e}")
            db.rollback()
            mensaje = "Error al agregar cargo."
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
                "INSERT INTO especialidad (N_especialidad) VALUES (%s)",
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
                "DELETE FROM empleado WHERE ID_em = %s",
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

    def eliminar_cargo(self, n_cargo: str) -> str:
        # verificar existencia (aceptamos id o nombre en la función verificar)
        if not self.verificar_cargo(n_cargo):
            return f"El cargo con identificador {n_cargo} no existe."

        db = self.conexion1()
        if not db:
            mensaje = "Error al conectar a la base de datos."
            return mensaje

        cursor = db.cursor()
        try:
            cursor.execute(
                "DELETE FROM cargo WHERE N_cargo = %s",
                (n_cargo,),
            )
            db.commit()
            mensaje = "Cargo eliminado exitosamente."
            return mensaje
        except Exception as e:
            print(f"Error al eliminar cargo: {e}")
            db.rollback()
            mensaje = "Error al eliminar cargo."
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
                "DELETE FROM especialidad WHERE N_especialidad = %s",
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
        nombre: str,
        apellido: str,
        celular: str,
        correo: str,
        direccion: str,
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
                SET ID_em = %s, Nombre_em = %s, Apellido_em = %s, Celular_em = %s, Correo_em = %s, Direccion_em = %s
                WHERE ID_em = %s
                """,
                (id_empleado, nombre, apellido, celular, correo, direccion, id_empleado),
            )
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
                "SELECT 1 FROM empleado WHERE ID_em = %s LIMIT 1",
                (cedula,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    def verificar_cargo(self, cargo: str) -> bool:
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM cargo WHERE N_cargo = %s LIMIT 1",
                (cargo,),
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
                "SELECT 1 FROM especialidad WHERE N_especialidad = %s LIMIT 1",
                (especialidad,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()
   