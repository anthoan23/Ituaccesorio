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

    def agregar_especialidad(self, especialidad: str) -> str:
        # ID_espesialidad es AUTO_INCREMENT, así que solo se inserta el nombre.
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

    def verificar_empleado(self, cedula: str) -> str:
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM empleado WHERE ID_em = %s",
                (cedula,),
            )
            result = cursor.fetchone()
            return result[0] > 0
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
                "SELECT COUNT(*) FROM cargo WHERE N_cargo = %s",
                (cargo,),
            )
            result = cursor.fetchone()
            return result[0] > 0
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
                "SELECT COUNT(*) FROM especialidad WHERE N_especialidad = %s",
                (especialidad,),
            )
            result = cursor.fetchone()
            return result[0] > 0
        finally:
            cursor.close()
            db.close()
   