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
                    e.Nombre_empleado AS nombre,
                    e.Apellido_empleado AS apellido,
                    c.Nombre_cargo AS cargo
                FROM Empleado e
                JOIN Cargo c ON e.ID_cargo = c.ID_cargo
                LEFT JOIN Capacitacion cap ON e.ID_empleado = cap.ID_empleado
                LEFT JOIN Especialidad esp ON cap.ID_especialidad = esp.ID_especialidad
                GROUP BY e.ID_empleado
                ORDER BY e.ID_empleado ASC
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
                INSERT INTO Empleado (ID_empleado, ID_cargo, Nombre_empleado, Apellido_empleado, Celular_empleado, Correo_empleado, Direccion_empleado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (cedula, cargo_id, nombre, apellido, celular, correo, direccion),
            )

            # insert especialidades associations if provided
            if especialidades:
                for esp_id in especialidades:
                    try:
                        cursor.execute(
                            "INSERT INTO Capacitacion (ID_especialidad, ID_empleado) VALUES (%s, %s)",
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
                SET ID_em = %s, ID_cargo = %s, Nombre_em = %s, Apellido_em = %s, Celular_em = %s, Correo_em = %s, Direccion_em = %s
                WHERE ID_em = %s
                """,
                (id_empleado, cargo_id, nombre, apellido, celular, correo, direccion, id_empleado),
            )
            # update specialties associations if provided
            if especialidades is not None:
                try:
                    cursor.execute(
                        "DELETE FROM capacitacion WHERE ID_em = %s",
                        (id_empleado,),
                    )
                except Exception:
                    pass

                for esp_id in especialidades:
                    try:
                        cursor.execute(
                            "INSERT INTO capacitacion (ID_especialidad, ID_em) VALUES (%s, %s)",
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

   
