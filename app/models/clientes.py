from __future__ import annotations
from app.models.database import conectar
from typing import Dict, Any, List, Optional

class GestionClientes:
    """Modelo para gestión de clientes"""

    def __init__(self):
        self.__conexion_bd = conectar()

    def listar_clientes(self) -> List[Dict[str, Any]]:
        """Listar todos los clientes (personas naturales)"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    c.ID_cliente AS ID_c,
                    pn.Nombre_cliente AS nombre,
                    pn.Apellido_cliente AS apellido,
                    c.Direccion_cliente AS direccion,
                    c.Celular_cliente AS celular,
                    c.Correo_cliente AS correo
                FROM Cliente c
                JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                ORDER BY pn.Nombre_cliente ASC
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def obtener_cliente_por_id(self, cliente_id: str) -> Optional[Dict[str, Any]]:
        """Obtener un cliente por su ID"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    c.ID_cliente AS ID_c,
                    pn.Nombre_cliente AS nombre,
                    pn.Apellido_cliente AS apellido,
                    c.Direccion_cliente AS direccion,
                    c.Celular_cliente AS celular,
                    c.Correo_cliente AS correo
                FROM Cliente c
                JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                WHERE c.ID_cliente = %s
            """, (cliente_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()

    def buscar_cliente(self, termino: str) -> List[Dict[str, Any]]:
        """Buscar clientes por nombre, apellido o ID"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    c.ID_cliente AS ID_c,
                    pn.Nombre_cliente AS nombre,
                    pn.Apellido_cliente AS apellido,
                    c.Celular_cliente AS celular
                FROM Cliente c
                JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente
                WHERE c.ID_cliente LIKE %s 
                   OR pn.Nombre_cliente LIKE %s 
                   OR pn.Apellido_cliente LIKE %s
                LIMIT 20
            """, (f"%{termino}%", f"%{termino}%", f"%{termino}%"))
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def crear_cliente(self, datos: Dict[str, Any]) -> str:
        """Crear un nuevo cliente"""
        db = self.__conexion_bd.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos")

        cursor = db.cursor()
        try:
            cliente_id = str(datos.get("id_cliente") or datos.get("cedula"))
            nombre = datos.get("nombre", "")
            apellido = datos.get("apellido", "")
            direccion = datos.get("direccion", "")
            celular = datos.get("celular", "")
            correo = datos.get("correo", "")

            if not cliente_id or not nombre:
                raise ValueError("ID y nombre del cliente son obligatorios")

            cursor.execute("""
                INSERT INTO Cliente (ID_cliente, Direccion_cliente, Celular_cliente, Correo_cliente)
                VALUES (%s, %s, %s, %s)
            """, (cliente_id, direccion, celular, correo))

            cursor.execute("""
                INSERT INTO Persona_natural (ID_cliente, Nombre_cliente, Apellido_cliente)
                VALUES (%s, %s, %s)
            """, (cliente_id, nombre, apellido))

            db.commit()
            return cliente_id
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()