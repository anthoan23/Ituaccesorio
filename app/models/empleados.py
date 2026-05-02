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
                    e.ID_em AS cedula,
                    e.Nombre_em AS nombre,
                    e.Apellido_em AS apellido,
                    e.Celular_em AS celular,
                    e.Correo_em AS correo,
                    e.Direccion_em AS direccion,
                    c.N_cargo AS rol
                FROM empleado e
                LEFT JOIN empleado_cargo ec ON ec.ID_em = e.ID_em
                LEFT JOIN cargo c ON c.ID_cargo = ec.ID_cargo
                ORDER BY e.ID_em ASC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def obtener_empleados_recientes(self, limite: int = 5):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    e.ID_em AS cedula,
                    e.Nombre_em AS nombre,
                    e.Apellido_em AS apellido,
                    e.Celular_em AS celular,
                    e.Correo_em AS correo,
                    e.Direccion_em AS direccion,
                    c.N_cargo AS rol
                FROM empleado e
                LEFT JOIN empleado_cargo ec ON ec.ID_em = e.ID_em
                LEFT JOIN cargo c ON c.ID_cargo = ec.ID_cargo
                ORDER BY e.ID_em DESC
                LIMIT %s
                """,
                (int(limite),),
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def crear_empleado(self, id_em: int, nombre, apellido, celular, correo, direccion, rol=None):
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO empleado (ID_em, Nombre_em, Apellido_em, Celular_em, Correo_em, Direccion_em) VALUES (%s, %s, %s, %s, %s, %s)",
                (id_em, nombre, apellido, celular, correo, direccion),
            )

            cargo_id = self._asegurar_cargo(cursor, rol)
            if cargo_id is not None:
                self._asignar_cargo(cursor, id_em, cargo_id)

            db.commit()
            return True
        finally:
            cursor.close()
            db.close()

    def actualizar_empleado(self, id_em: int, nombre, apellido, celular, correo, direccion, rol=None):
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE empleado SET Nombre_em=%s, Apellido_em=%s, Celular_em=%s, Correo_em=%s, Direccion_em=%s WHERE ID_em=%s",
                (nombre, apellido, celular, correo, direccion, id_em),
            )

            cargo_id = self._asegurar_cargo(cursor, rol)
            if cargo_id is not None:
                self._asignar_cargo(cursor, id_em, cargo_id)
            elif rol in (None, ""):
                cursor.execute("DELETE FROM empleado_cargo WHERE ID_em=%s", (id_em,))

            db.commit()
            return cursor.rowcount > 0 or cargo_id is not None
        finally:
            cursor.close()
            db.close()

    def eliminar_empleado(self, id_em: int):
        db = self.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM empleado_cargo WHERE ID_em=%s", (id_em,))
            cursor.execute("DELETE FROM empleado WHERE ID_em=%s", (id_em,))
            db.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            db.close()

    def _asegurar_cargo(self, cursor, rol):
        rol_text = (rol or "").strip()
        if not rol_text:
            return None

        cursor.execute("SELECT ID_cargo FROM cargo WHERE N_cargo=%s", (rol_text,))
        row = cursor.fetchone()
        if row:
            return row[0]

        cursor.execute("INSERT INTO cargo (N_cargo) VALUES (%s)", (rol_text,))
        return cursor.lastrowid

    def _asignar_cargo(self, cursor, id_em: int, cargo_id: int):
        anio = date.today().year
        cursor.execute("DELETE FROM empleado_cargo WHERE ID_em=%s", (id_em,))
        cursor.execute(
            "INSERT INTO empleado_cargo (ID_cargo, ID_em, A_cargo) VALUES (%s, %s, %s)",
            (cargo_id, id_em, anio),
        )
