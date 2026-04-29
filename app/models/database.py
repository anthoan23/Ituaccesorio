import mysql.connector
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

class conectar:
    def __init__(self):
        # Leemos las variables del entorno usando os.getenv
        self.__host1 = os.getenv("DB_HOST1")
        self.__host2 = os.getenv("DB_HOST2")
        self.__port = int(os.getenv("DB_PORT"))
        self.__user = os.getenv("DB_USER")
        self.__password = os.getenv("DB_PASSWORD")
        self.__database1 = os.getenv("DB_NAME1")
        self.__database2 = os.getenv("DB_NAME2")

    def _crear_conexion(self, host, port, database):
        try:
            return mysql.connector.connect(
                host=host,
                port=port,
                user=self.__user,
                password=self.__password,
                database=database
            )
        except mysql.connector.Error as err:
            print(f"Error al conectar: {err}")
            return None

    def conexion1(self): 
        return self._crear_conexion(self.__host1, self.__port, self.__database1)
        
    def conexion2(self): 
        return self._crear_conexion(self.__host2, self.__port, self.__database2)
