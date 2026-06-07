from __future__ import annotations
from app.models.database import conectar


class Cliente:
    def __init__(self, id_cliente: str = ""):
        self.id_cliente = id_cliente
        self.__conexion_bd = conectar()

    def verificar_cliente_por_id(self) -> bool:
        """Verifica si un cliente existe"""
        if not self.id_cliente:
            return False

        db = self.__conexion_bd.conexion1()
        if not db:
            return False

        cursor = db.cursor()
        try:
            cursor.execute("SELECT 1 FROM Cliente WHERE ID_cliente = %s LIMIT 1", (self.id_cliente,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    def listar_clientes(self):
        """Lista todos los clientes (personas naturales)"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    c.ID_cliente AS id,
                    pn.Nombre_cliente AS nombre,
                    pn.Apellido_cliente AS apellido,
                    CONCAT(pn.Nombre_cliente, ' ', pn.Apellido_cliente) AS nombre_completo,
                    c.Celular_cliente AS celular,
                    c.Correo_cliente AS correo
                FROM Cliente c
                INNER JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                ORDER BY pn.Nombre_cliente ASC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def obtener_cliente_por_id(self):
        """Obtiene un cliente por su ID"""
        if not self.id_cliente:
            return None

        db = self.__conexion_bd.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    c.ID_cliente AS id,
                    c.Direccion_cliente AS direccion,
                    c.Celular_cliente AS celular,
                    c.Correo_cliente AS correo,
                    pn.Nombre_cliente AS nombre,
                    pn.Apellido_cliente AS apellido
                FROM Cliente c
                LEFT JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                WHERE c.ID_cliente = %s
                LIMIT 1
                """,
                (self.id_cliente,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()