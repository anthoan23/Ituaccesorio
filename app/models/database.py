import mysql.connector
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

class conectar:
    def __init__(self):
        # La configuración se resuelve de forma perezosa para que las
        # subclases no tengan que llamar explícitamente a super().__init__().
        pass

    def _crear_conexion(self, host, port, database, password=None):
        try:
            return mysql.connector.connect(
                host=host,
                port=port,
                user=os.getenv("DB_USER"),
                password=password if password is not None else os.getenv("DB_PASSWORD"),
                database=database
            )
        except mysql.connector.Error as err:
            print(f"Error al conectar: {err}")
            return None

    def conexion1(self): 
        return self._crear_conexion(
            os.getenv("DB_HOST1"),
            int(os.getenv("DB_PORT")),
            os.getenv("DB_NAME1"),
        )
        
    def conexion2(self): 
        return self._crear_conexion(
            os.getenv("DB_HOST2"),
            int(os.getenv("DB_PORT")),
            os.getenv("DB_NAME2"),
            password=os.getenv("DB_PASSWORD2", os.getenv("DB_PASSWORD")),
        )
