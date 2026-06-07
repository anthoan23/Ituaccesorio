from __future__ import annotations
from datetime import date
from app.models.database import conectar


class Empleados():
    
    def __init__(self, 
                 id_empleado: str = "",
                 id_cargo: str = "",
                 nombre_empleado: str = "",
                 apellido_empleado: str = "",
                 celular_empleado: str = "",
                 correo_empleado: str = "",
                 direccion_empleado: str = "",
                 especialidades: list | None = None):
        
        self.id_empleado = id_empleado
        self.id_cargo = id_cargo
        self.nombre_empleado = nombre_empleado
        self.apellido_empleado = apellido_empleado
        self.celular_empleado = celular_empleado
        self.correo_empleado = correo_empleado
        self.direccion_empleado = direccion_empleado
        self.especialidades = especialidades if especialidades is not None else []
        
        self.__conexion_bd = conectar()
    
    def listar_empleados(self):
        db = self.__conexion_bd.conexion1()
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
                ORDER BY e.ID_empleado ASC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def listar_cargos(self):
        """Lista todos los cargos disponibles"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT ID_cargo AS id, Nombre_cargo AS nombre, Descripcion_cargo AS descripcion
                FROM Cargo
                ORDER BY Nombre_cargo ASC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def listar_especialidades(self):
        """Lista todas las especialidades disponibles"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT ID_especialidad AS id, Nombre_especialidad AS nombre, Descripcion_especialidad AS descripcion
                FROM Especialidad
                ORDER BY Nombre_especialidad ASC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def listar_empleados_por_cargo(self):
        """Obtiene cantidad de empleados por cargo para gráficos"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT 
                    c.Nombre_cargo AS nombre,
                    COUNT(e.ID_empleado) AS cantidad
                FROM Cargo c
                LEFT JOIN Empleado e ON e.ID_cargo = c.ID_cargo
                GROUP BY c.ID_cargo, c.Nombre_cargo
                ORDER BY cantidad DESC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def listar_empleados_por_especialidad(self):
        """Obtiene cantidad de empleados por especialidad para gráficos"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT 
                    esp.Nombre_especialidad AS nombre,
                    COUNT(cap.ID_empleado) AS cantidad
                FROM Especialidad esp
                LEFT JOIN Capacitacion cap ON cap.ID_especialidad = esp.ID_especialidad
                GROUP BY esp.ID_especialidad, esp.Nombre_especialidad
                ORDER BY cantidad DESC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def consultar_empleado(self):
        """Obtiene un empleado por su cédula (usa el atributo id_empleado)"""
        cedula = self.id_empleado.strip()
        
        if not cedula:
            return None
            
        db = self.__conexion_bd.conexion1()
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
                    e.Celular_empleado AS celular,
                    e.Correo_empleado AS correo,
                    e.Direccion_empleado AS direccion,
                    c.ID_cargo AS cargo_id,
                    c.Nombre_cargo AS cargo
                FROM Empleado e
                JOIN Cargo c ON e.ID_cargo = c.ID_cargo
                WHERE e.ID_empleado = %s
                LIMIT 1
                """,
                (cedula,)
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()

    def consultar_especialidades_empleado(self):
        """Obtiene las especialidades de un empleado (usa el atributo id_empleado)"""
        cedula = self.id_empleado.strip()
        
        if not cedula:
            return None
            
        db = self.__conexion_bd.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT 
                    esp.ID_especialidad AS id,
                    esp.Nombre_especialidad AS nombre,
                    esp.Descripcion_especialidad AS descripcion
                FROM Capacitacion cap
                JOIN Especialidad esp ON cap.ID_especialidad = esp.ID_especialidad
                WHERE cap.ID_empleado = %s
                ORDER BY esp.Nombre_especialidad ASC
                """,
                (cedula,)
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def verificar_empleado(self) -> bool:
        """Verifica si un empleado existe (usa el atributo id_empleado)"""
        cedula = self.id_empleado.strip()
        
        if not cedula:
            return False
            
        db = self.__conexion_bd.conexion1()
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

    def agregar_empleado(self) -> str:
        """Agrega un nuevo empleado usando los atributos de la instancia"""
        # Usar los atributos de la instancia
        cedula = self.id_empleado.strip()
        cargo_id = self.id_cargo.strip()
        nombre = self.nombre_empleado.strip()
        apellido = self.apellido_empleado.strip()
        celular = self.celular_empleado.strip()
        correo = self.correo_empleado.strip()
        direccion = self.direccion_empleado.strip()
        especialidades = self.especialidades

        # Validaciones
        if not cedula or not cargo_id or not nombre or not apellido:
            return "La cédula, cargo, nombre y apellido son obligatorios."

        if self.verificar_empleado():
            return f"El empleado con cédula {cedula} ya existe."

        db = self.__conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO Empleado (ID_empleado, ID_cargo, Nombre_empleado, Apellido_empleado, Celular_empleado, Correo_empleado, Direccion_empleado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
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
        except Exception as e:
            print(f"Error al agregar empleado: {e}")
            db.rollback()
            return "Error al agregar empleado."
        finally:
            cursor.close()
            db.close()

    def actualizar_empleado(self) -> str:
        """Actualiza un empleado existente usando los atributos de la instancia"""
        # Usar los atributos de la instancia
        id_empleado = self.id_empleado.strip()
        cargo_id = self.id_cargo.strip()
        nombre = self.nombre_empleado.strip()
        apellido = self.apellido_empleado.strip()
        celular = self.celular_empleado.strip()
        correo = self.correo_empleado.strip()
        direccion = self.direccion_empleado.strip()
        especialidades = self.especialidades

        # Validaciones
        if not id_empleado:
            return "El identificador del empleado es obligatorio."

        if not self.verificar_empleado():
            return f"El empleado con identificador {id_empleado} no existe."

        db = self.__conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                """
                UPDATE Empleado
                SET ID_cargo = %s,
                    Nombre_empleado = %s,
                    Apellido_empleado = %s,
                    Celular_empleado = %s,
                    Correo_empleado = %s,
                    Direccion_empleado = %s
                WHERE ID_empleado = %s
                """,
                (cargo_id, nombre, apellido, celular, correo, direccion, id_empleado),
            )

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

    def eliminar_empleado(self) -> str:
        """Elimina un empleado usando el atributo id_empleado"""
        id_empleado = self.id_empleado.strip()

        if not id_empleado:
            return "El identificador del empleado no puede estar vacío."

        if not self.verificar_empleado():
            return f"El empleado con identificador {id_empleado} no existe."

        db = self.__conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            # Primero eliminar las capacitaciones
            cursor.execute(
                "DELETE FROM Capacitacion WHERE ID_empleado = %s",
                (id_empleado,),
            )
            # Luego eliminar el empleado
            cursor.execute(
                "DELETE FROM Empleado WHERE ID_empleado = %s",
                (id_empleado,),
            )
            db.commit()
            return "Empleado eliminado exitosamente."
        except Exception as e:
            print(f"Error al eliminar empleado: {e}")
            db.rollback()
            return "Error al eliminar empleado."
        finally:
            cursor.close()
            db.close()

    def listar_tecnicos(self):
        """Lista empleados con cargo Técnico"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    e.ID_empleado AS id,
                    e.Nombre_empleado AS nombre,
                    e.Apellido_empleado AS apellido
                FROM Empleado e
                JOIN Cargo c ON e.ID_cargo = c.ID_cargo
                WHERE LOWER(c.Nombre_cargo) = 'técnico'
                ORDER BY e.Nombre_empleado ASC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()