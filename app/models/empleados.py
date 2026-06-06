from __future__ import annotations

from app.models.database import conectar


class Empleados(conectar):
    def _consultar(self, query, params=None):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def _ejecutar(self, query, params=None):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor()
        try:
            cursor.execute(query, params or ())
            db.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    def listar_empleados(self):
        return self._consultar(
            """
            SELECT
                e.ID_empleado AS cedula,
                e.ID_cargo AS id_cargo,
                e.Nombre_empleado AS nombre,
                e.Apellido_empleado AS apellido,
                e.Celular_empleado AS celular,
                e.Correo_empleado AS correo,
                e.Direccion_empleado AS direccion,
                c.Nombre_cargo AS cargo_nombre,
                GROUP_CONCAT(DISTINCT esp.ID_especialidad) AS especialidades_ids,
                GROUP_CONCAT(DISTINCT esp.Nombre_especialidad) AS especialidades_nombres
            FROM Empleado e
            JOIN Cargo c ON e.ID_cargo = c.ID_cargo
            LEFT JOIN Capacitacion cap ON e.ID_empleado = cap.ID_empleado
            LEFT JOIN Especialidad esp ON cap.ID_especialidad = esp.ID_especialidad
            GROUP BY e.ID_empleado
            ORDER BY e.ID_empleado ASC
            """
        )

    def listar_empleados_cargos(self):
        return self._consultar(
            """
            SELECT
                c.Nombre_cargo,
                COUNT(e.ID_empleado) AS cantidad_personas
            FROM Cargo c
            LEFT JOIN Empleado e ON c.ID_cargo = e.ID_cargo
            GROUP BY c.ID_cargo, c.Nombre_cargo
            ORDER BY cantidad_personas DESC
            LIMIT 10
            """
        )

    def listar_tecnicos(self):
        return self.listar_empleados_cargos()

    def listar_empleados_especialidades(self):
        return self._consultar(
            """
            SELECT
                e.Nombre_especialidad,
                COUNT(c.ID_empleado) AS cantidad_personas
            FROM Especialidad e
            LEFT JOIN Capacitacion c ON e.ID_especialidad = c.ID_especialidad
            GROUP BY e.ID_especialidad, e.Nombre_especialidad
            ORDER BY cantidad_personas DESC
            LIMIT 10
            """
        )

    def listar_especialidades(self):
        return self.lista_especialidades()

    def lista_crgos(self):
        return self._consultar(
            """
            SELECT ID_cargo, Nombre_cargo
            FROM Cargo
            ORDER BY Nombre_cargo ASC
            """
        )

    def lista_especialidades(self):
        return self._consultar(
            """
            SELECT ID_especialidad, Nombre_especialidad
            FROM Especialidad
            ORDER BY Nombre_especialidad ASC
            """
        )

    def consultar_empleado(self, cedula: str):
        datos = self._consultar(
            """
            SELECT
                e.ID_empleado AS cedula,
                e.Nombre_empleado AS nombre,
                e.Apellido_empleado AS apellido,
                e.Celular_empleado AS celular,
                e.Correo_empleado AS correo,
                e.Direccion_empleado AS direccion,
                c.Nombre_cargo AS cargo
            FROM Empleado e
            JOIN Cargo c ON e.ID_cargo = c.ID_cargo
            WHERE e.ID_empleado = %s
            LIMIT 1
            """,
            (cedula,),
        )
        return datos[0] if datos else None

    def consultar_especialidades_empleado(self, cedula: str):
        datos = self._consultar(
            """
            SELECT
                esp.Nombre_especialidad AS especialidad,
                esp.ID_especialidad AS id_especialidad
            FROM Capacitacion cap
            JOIN Especialidad esp ON cap.ID_especialidad = esp.ID_especialidad
            WHERE cap.ID_empleado = %s
            ORDER BY esp.Nombre_especialidad ASC
            """,
            (cedula,),
        )
        return [fila["especialidad"] for fila in datos] if datos else []

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
    ) -> str:
        if self.verificar_empleado(cedula):
            return f"El empleado con cédula {cedula} ya existe."

        db = self.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO Empleado (
                    ID_empleado, ID_cargo, Nombre_empleado, Apellido_empleado,
                    Celular_empleado, Correo_empleado, Direccion_empleado
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (cedula, cargo_id, nombre, apellido, celular, correo, direccion),
            )

            if especialidades:
                for esp_id in especialidades:
                    try:
                        cursor.execute(
                            "INSERT INTO Capacitacion (ID_especialidad, ID_empleado) VALUES (%s, %s)",
                            (esp_id, cedula),
                        )
                    except Exception:
                        pass

            db.commit()
            return "Empleado agregado exitosamente."
        except Exception as error:
            print(f"Error al agregar empleado: {error}")
            db.rollback()
            return "Error al agregar empleado."
        finally:
            cursor.close()
            db.close()

    def agregar_especialidad(self, especialidad: str) -> str:
        if self.verificar_espesialidad(especialidad):
            return f"La especialidad '{especialidad}' ya existe."

        db = self.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO Especialidad (Nombre_especialidad) VALUES (%s)",
                (especialidad,),
            )
            db.commit()
            return f"Especialidad agregada exitosamente. ID: {cursor.lastrowid}."
        except Exception as error:
            print(f"Error al agregar especialidad: {error}")
            db.rollback()
            return "Error al agregar especialidad."
        finally:
            cursor.close()
            db.close()

    def eliminar_empleado(self, id_em: str) -> str:
        if not self.verificar_empleado(id_em):
            return f"El empleado con identificador {id_em} no existe."

        db = self.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM Capacitacion WHERE ID_empleado = %s", (id_em,))
            cursor.execute("DELETE FROM Empleado WHERE ID_empleado = %s", (id_em,))
            db.commit()
            return "Empleado eliminado exitosamente."
        except Exception as error:
            print(f"Error al eliminar empleado: {error}")
            db.rollback()
            return "Error al eliminar empleado."
        finally:
            cursor.close()
            db.close()

    def eliminar_especialidad(self, n_especialidad: str) -> str:
        if not self.verificar_espesialidad(n_especialidad):
            return f"La especialidad con identificador {n_especialidad} no existe."

        db = self.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                "DELETE FROM Especialidad WHERE Nombre_especialidad = %s",
                (n_especialidad,),
            )
            db.commit()
            return "Especialidad eliminada exitosamente."
        except Exception as error:
            print(f"Error al eliminar especialidad: {error}")
            db.rollback()
            return "Error al eliminar especialidad."
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
        if not self.verificar_empleado(id_empleado):
            return f"El empleado con identificador {id_empleado} no existe."

        db = self.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                """
                UPDATE Empleado
                SET ID_empleado = %s,
                    ID_cargo = %s,
                    Nombre_empleado = %s,
                    Apellido_empleado = %s,
                    Celular_empleado = %s,
                    Correo_empleado = %s,
                    Direccion_empleado = %s
                WHERE ID_empleado = %s
                """,
                (id_empleado, cargo_id, nombre, apellido, celular, correo, direccion, id_empleado),
            )

            if especialidades is not None:
                try:
                    cursor.execute("DELETE FROM Capacitacion WHERE ID_empleado = %s", (id_empleado,))
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
        except Exception as error:
            print(f"Error al actualizar empleado: {error}")
            db.rollback()
            return "Error al actualizar empleado."
        finally:
            cursor.close()
            db.close()

    def actualizar_cargo(self, id_cargo: int, cargo_n: str, cargo_v: str) -> str:
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
                "UPDATE Cargo SET Nombre_cargo = %s WHERE ID_cargo = %s",
                (cargo_n, id_cargo),
            )
            db.commit()
            return "Cargo modificado exitosamente."
        except Exception as error:
            print(f"Error al actualizar cargo: {error}")
            db.rollback()
            return "Error al actualizar cargo."
        finally:
            cursor.close()
            db.close()

    def actualizar_especialidad(self, id_especialidad: int, especialidad_n: str, especialidad_v: str) -> str:
        if not self.verificar_espesialidad(especialidad_v):
            return f"La especialidad con nombre {especialidad_v} no existe."

        db = self.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE Especialidad SET Nombre_especialidad = %s WHERE ID_especialidad = %s",
                (especialidad_n, id_especialidad),
            )
            db.commit()
            return "Especialidad modificada exitosamente."
        except Exception as error:
            print(f"Error al actualizar especialidad: {error}")
            db.rollback()
            return "Error al actualizar especialidad."
        finally:
            cursor.close()
            db.close()

    def verificar_empleado(self, cedula: str) -> bool:
        datos = self._consultar(
            "SELECT 1 FROM Empleado WHERE ID_empleado = %s LIMIT 1",
            (cedula,),
        )
        return bool(datos)

    def verificar_espesialidad(self, especialidad: str) -> bool:
        datos = self._consultar(
            "SELECT 1 FROM Especialidad WHERE Nombre_especialidad = %s LIMIT 1",
            (especialidad,),
        )
        return bool(datos)

    def verificar_cargo(self, cargo: str) -> bool:
        datos = self._consultar(
            "SELECT 1 FROM Cargo WHERE Nombre_cargo = %s LIMIT 1",
            (cargo,),
        )
        return bool(datos)
