from __future__ import annotations

from app.models.database import conectar


class Permiso:
    def __init__(self, rol_id: str = "", modulo_id: str = ""):
        self.rol_id = rol_id
        self.modulo_id = modulo_id
        self.__conexion_bd = conectar()

    def listar_permisos_por_rol(self, rol_id: str = None):
        id_buscar = rol_id or self.rol_id
        if not id_buscar:
            return None

        db = self.__conexion_bd.conexion2()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    p.rol_id,
                    p.modulo_id,
                    m.nombre AS modulo_nombre,
                    m.descripcion AS modulo_descripcion,
                    COALESCE(p.consultar, 0) AS consultar,
                    COALESCE(p.registrar, 0) AS registrar,
                    COALESCE(p.modificar, 0) AS modificar,
                    COALESCE(p.eliminar, 0) AS eliminar
                FROM permiso p
                INNER JOIN modulo m ON m.id = p.modulo_id
                WHERE p.rol_id = %s
                ORDER BY m.nombre
                """,
                (id_buscar,)
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def listar_permisos_completos_por_rol(self, rol_id: str = None):
        """
        Obtiene todos los módulos con sus permisos para un rol.
        La regla es:
        - Si tiene al menos un permiso activo (registrar, modificar, eliminar), consultar = True
        - Si no tiene ningún permiso activo, consultar = False
        """
        id_buscar = rol_id or self.rol_id
        if not id_buscar:
            return None

        db = self.__conexion_bd.conexion2()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            # Obtener todos los módulos
            cursor.execute("SELECT id, nombre, descripcion FROM modulo ORDER BY nombre")
            modulos = cursor.fetchall()

            # Obtener permisos existentes para el rol
            cursor.execute(
                """
                SELECT modulo_id, registrar, modificar, eliminar
                FROM permiso
                WHERE rol_id = %s
                """,
                (id_buscar,)
            )
            permisos_existentes = {p["modulo_id"]: p for p in cursor.fetchall()}

            # Combinar resultados aplicando la regla de negocio
            resultados = []
            for modulo in modulos:
                permiso = permisos_existentes.get(modulo["id"], {})
                registrar = permiso.get("registrar", False)
                modificar = permiso.get("modificar", False)
                eliminar = permiso.get("eliminar", False)
                
                # Regla: si tiene al menos un permiso, consultar = True, de lo contrario False
                tiene_permisos_activos = registrar or modificar or eliminar
                consultar = tiene_permisos_activos
                
                resultados.append({
                    "modulo_id": modulo["id"],
                    "modulo_nombre": modulo["nombre"],
                    "modulo_descripcion": modulo.get("descripcion", ""),
                    "consultar": consultar,
                    "registrar": registrar,
                    "modificar": modificar,
                    "eliminar": eliminar,
                })

            return resultados
        finally:
            cursor.close()
            db.close()

    def guardar_permiso(self, rol_id: str, modulo_id: str, registrar: bool = False,
                        modificar: bool = False, eliminar: bool = False) -> str:
        """
        Guarda los permisos de un rol para un módulo.
        NOTA: El permiso de consultar se calcula automáticamente según la regla:
        consultar = registrar OR modificar OR eliminar
        """
        if not rol_id or not modulo_id:
            return "Rol y módulo son obligatorios."

        # Calcular consultar según la regla de negocio
        consultar = registrar or modificar or eliminar

        db = self.__conexion_bd.conexion2()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            # Verificar si existe el permiso
            cursor.execute(
                "SELECT 1 FROM permiso WHERE rol_id = %s AND modulo_id = %s LIMIT 1",
                (rol_id, modulo_id)
            )
            existe = cursor.fetchone() is not None

            if existe:
                cursor.execute(
                    """
                    UPDATE permiso
                    SET registrar = %s, modificar = %s, eliminar = %s, consultar = %s
                    WHERE rol_id = %s AND modulo_id = %s
                    """,
                    (registrar, modificar, eliminar, consultar, rol_id, modulo_id)
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO permiso (rol_id, modulo_id, registrar, modificar, eliminar, consultar)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (rol_id, modulo_id, registrar, modificar, eliminar, consultar)
                )
            db.commit()
            return "Permiso guardado exitosamente."
        except Exception as e:
            print(f"Error al guardar permiso: {e}")
            db.rollback()
            return "Error al guardar permiso."
        finally:
            cursor.close()
            db.close()

    def guardar_permisos_masivos(self, rol_id: str, permisos: list) -> tuple:
        """
        Guarda múltiples permisos de forma masiva.
        
        Args:
            rol_id: ID del rol
            permisos: Lista de diccionarios con modulo_id, registrar, modificar, eliminar
        
        Returns:
            tuple: (exitosos, errores)
        """
        if not rol_id:
            return 0, ["Rol es obligatorio"]

        db = self.__conexion_bd.conexion2()
        if not db:
            return 0, ["Error al conectar a la base de datos."]

        cursor = db.cursor()
        exitosos = 0
        errores = []

        try:
            for permiso in permisos:
                modulo_id = permiso.get("modulo_id")
                if not modulo_id:
                    errores.append("Módulo ID faltante en uno de los permisos")
                    continue

                registrar = permiso.get("registrar", False)
                modificar = permiso.get("modificar", False)
                eliminar = permiso.get("eliminar", False)
                consultar = registrar or modificar or eliminar  # Regla de negocio

                # Verificar si existe el permiso
                cursor.execute(
                    "SELECT 1 FROM permiso WHERE rol_id = %s AND modulo_id = %s LIMIT 1",
                    (rol_id, modulo_id)
                )
                existe = cursor.fetchone() is not None

                if existe:
                    cursor.execute(
                        """
                        UPDATE permiso
                        SET registrar = %s, modificar = %s, eliminar = %s, consultar = %s
                        WHERE rol_id = %s AND modulo_id = %s
                        """,
                        (registrar, modificar, eliminar, consultar, rol_id, modulo_id)
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO permiso (rol_id, modulo_id, registrar, modificar, eliminar, consultar)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (rol_id, modulo_id, registrar, modificar, eliminar, consultar)
                    )
                exitosos += 1

            db.commit()
            return exitosos, errores
        except Exception as e:
            db.rollback()
            print(f"Error al guardar permisos masivos: {e}")
            return 0, [str(e)]
        finally:
            cursor.close()
            db.close()

    def eliminar_permiso(self, rol_id: str, modulo_id: str) -> str:
        if not rol_id or not modulo_id:
            return "Rol y módulo son obligatorios."

        db = self.__conexion_bd.conexion2()
        if not db:
            return "Error al conectar a la base de datos."

        cursor = db.cursor()
        try:
            cursor.execute(
                "DELETE FROM permiso WHERE rol_id = %s AND modulo_id = %s",
                (rol_id, modulo_id)
            )
            db.commit()
            return "Permiso eliminado exitosamente."
        except Exception as e:
            print(f"Error al eliminar permiso: {e}")
            db.rollback()
            return "Error al eliminar permiso."
        finally:
            cursor.close()
            db.close()

    def verificar_permiso(self, rol_id: str, modulo_nombre: str, permiso_tipo: str) -> bool:
        """
        Verifica si un rol tiene un permiso específico en un módulo.
        
        Reglas:
        - Si permiso_tipo es 'consultar': retorna True si tiene al menos un permiso activo
        - Para otros permisos: retorna el valor específico
        
        Args:
            rol_id (str): ID del rol
            modulo_nombre (str): Nombre del módulo
            permiso_tipo (str): Tipo de permiso ('consultar', 'registrar', 'modificar', 'eliminar')
        
        Returns:
            bool: True si tiene el permiso, False si no
        """
        db = self.__conexion_bd.conexion2()
        if not db:
            return False

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT p.registrar, p.modificar, p.eliminar
                FROM permiso p
                INNER JOIN modulo m ON m.id = p.modulo_id
                WHERE p.rol_id = %s AND m.nombre = %s
                LIMIT 1
                """,
                (rol_id, modulo_nombre)
            )
            resultado = cursor.fetchone()
            
            if not resultado:
                # Si no hay registro, no tiene ningún permiso
                return False
            
            registrar = resultado.get("registrar", False)
            modificar = resultado.get("modificar", False)
            eliminar = resultado.get("eliminar", False)
            
            # Para consultar: tiene permiso si tiene al menos un permiso activo
            if permiso_tipo == "consultar":
                return registrar or modificar or eliminar
            
            # Para los demás: retornar el valor específico
            return resultado.get(permiso_tipo, False)
        finally:
            cursor.close()
            db.close()

    def obtener_permisos_usuario(self, usuario_id: str):
        """
        Obtiene todos los permisos de un usuario aplicando la regla de negocio.
        
        Args:
            usuario_id (str): ID del usuario
        
        Returns:
            list: Lista de permisos del usuario
        """
        db = self.__conexion_bd.conexion2()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT 
                    m.nombre AS modulo_nombre,
                    COALESCE(p.registrar, 0) AS registrar,
                    COALESCE(p.modificar, 0) AS modificar,
                    COALESCE(p.eliminar, 0) AS eliminar
                FROM modulo m
                LEFT JOIN permiso p ON p.modulo_id = m.id AND p.rol_id = (
                    SELECT rol_id FROM usuario WHERE id = %s
                )
                ORDER BY m.nombre
                """,
                (usuario_id,)
            )
            resultados = cursor.fetchall()
            
            # Aplicar regla de negocio: consultar = tiene al menos un permiso activo
            for resultado in resultados:
                tiene_permisos = resultado["registrar"] or resultado["modificar"] or resultado["eliminar"]
                resultado["consultar"] = tiene_permisos
            
            return resultados
        finally:
            cursor.close()
            db.close()