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

   