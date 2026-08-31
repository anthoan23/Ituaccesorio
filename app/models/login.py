from __future__ import annotations

import re
import traceback
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.database import conectar
from app.models.roles import Rol
from app.models.usuarios import Usuarios


class LoginManager:
    """Modelo para gestionar autenticacion y registro de usuarios"""
    
    def __init__(self):
        self.__conexion_bd = conectar()
        self._usuarios_model = Usuarios()
    
    # ==================== METODOS DE VALIDACION ====================
    
    def validar_usuario(self, nombre: str, password: str) -> dict | None:
        """
        Valida las credenciales de un usuario
        Reutiliza el metodo validar_login de Usuarios
        """
        try:
            return self._usuarios_model.validar_login(nombre, password)
        except Exception as e:
            print(f"Error en validar_usuario: {e}")
            traceback.print_exc()
            return None
    
    # ==================== METODOS DE REGISTRO ====================
    
    def obtener_rol_cliente(self) -> dict | None:
        """
        Obtiene el rol 'Cliente' del sistema
        Reutiliza el metodo obtener_rol_por_nombre de Usuarios
        """
        try:
            return self._usuarios_model.obtener_rol_por_nombre("Cliente")
        except Exception as e:
            print(f"Error al obtener rol cliente: {e}")
            traceback.print_exc()
            return None
    
    def verificar_usuario_existe_por_cedula(self, cedula: str) -> bool:
        """
        Verifica si un usuario ya existe por su cedula
        Reutiliza el metodo verificar_cedula_en_uso de Usuarios
        """
        try:
            return self._usuarios_model.verificar_cedula_en_uso(str(cedula))
        except Exception as e:
            print(f"Error al verificar cedula: {e}")
            traceback.print_exc()
            return False
    
    def verificar_usuario_existe_por_nombre(self, nombre: str) -> bool:
        """
        Verifica si un usuario ya existe por su nombre
        """
        try:
            temp_usuario = Usuarios(nombre=nombre)
            return temp_usuario.verificar_usuario_por_nombre()
        except Exception as e:
            print(f"Error al verificar nombre de usuario: {e}")
            traceback.print_exc()
            return False
    
    def crear_usuario(self, nombre: str, cedula: str, password: str, rol_id: int, foto_perfil: str = None) -> str | None:
        """
        Crea un nuevo usuario usando el modelo Usuarios
        
        Args:
            nombre: Nombre de usuario
            cedula: Cedula del usuario
            password: Contrasena en texto plano
            rol_id: ID del rol
            foto_perfil: Ruta de la foto de perfil (opcional)
        
        Returns:
            str: ID generado (ej: 'USR-001'), None si hubo error
        """
        try:
            print(f"Creando usuario: {nombre}, cedula: {cedula}, rol: {rol_id}")
            
            usuario = Usuarios(
                nombre=nombre,
                cedula=str(cedula),
                password=password,
                rol_id=str(rol_id),
                foto_perfil=foto_perfil
            )
            
            if usuario.verificar_usuario_por_nombre():
                print(f"El nombre de usuario '{nombre}' ya existe.")
                return None
            
            if usuario.verificar_cedula_en_uso(str(cedula)):
                print(f"La cedula '{cedula}' ya esta asignada a otro usuario.")
                return None
            
            resultado = usuario.agregar_usuario()
            print(f"Resultado de agregar_usuario: {resultado}")
            
            if "exitosamente" in resultado.lower():
                return usuario.id
            else:
                print(f"Error al crear usuario: {resultado}")
                return None
                
        except Exception as e:
            print(f"Error en crear_usuario: {e}")
            traceback.print_exc()
            return None
    
    def crear_cliente_natural(self, cedula: str, nombre: str, apellido: str, 
                              celular: str, correo: str = None, direccion: str = None) -> bool:
        """
        Crea un cliente como persona natural
        
        NOTA: Este metodo usa consultas directas porque la tabla Cliente/Persona_natural
        esta en la base de datos principal (ituaccesoriobd), no en la de seguridad.
        """
        db = None
        cursor = None
        try:
            db = self.__conexion_bd.conexion1()
            if not db:
                print("Error: No se pudo conectar a la base de datos principal")
                return False
            
            cursor = db.cursor()
            
            cursor.execute(
                "SELECT 1 FROM Cliente WHERE ID_cliente = %s LIMIT 1",
                (cedula,)
            )
            existe_cliente = cursor.fetchone() is not None
            
            if not existe_cliente:
                cursor.execute(
                    """
                    INSERT INTO Cliente (ID_cliente, Direccion_cliente, Celular_cliente, Correo_cliente)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (cedula, direccion, celular, correo)
                )
                print(f"Cliente insertado: {cedula}")
            else:
                cursor.execute(
                    """
                    UPDATE Cliente 
                    SET Direccion_cliente = %s, Celular_cliente = %s, Correo_cliente = %s
                    WHERE ID_cliente = %s
                    """,
                    (direccion, celular, correo, cedula)
                )
                print(f"Cliente actualizado: {cedula}")
            
            cursor.execute(
                "SELECT 1 FROM Persona_natural WHERE ID_cliente = %s LIMIT 1",
                (cedula,)
            )
            existe_persona_natural = cursor.fetchone() is not None
            
            if not existe_persona_natural:
                cursor.execute(
                    """
                    INSERT INTO Persona_natural (ID_cliente, Nombre_cliente, Apellido_cliente)
                    VALUES (%s, %s, %s)
                    """,
                    (cedula, nombre, apellido)
                )
                print(f"Persona natural creada: {nombre} {apellido}")
            else:
                cursor.execute(
                    """
                    UPDATE Persona_natural 
                    SET Nombre_cliente = %s, Apellido_cliente = %s
                    WHERE ID_cliente = %s
                    """,
                    (nombre, apellido, cedula)
                )
                print(f"Persona natural actualizada: {nombre} {apellido}")
            
            db.commit()
            print(f"Cliente natural creado/actualizado exitosamente: {nombre} {apellido}")
            return True
            
        except Exception as e:
            print(f"Error detallado al crear cliente natural: {e}")
            traceback.print_exc()
            if db:
                db.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()
    
    def verificar_perfil_completo_cliente(self, cedula: str) -> bool:
        """
        Verifica si un cliente tiene su perfil completo en Persona_natural
        """
        db = None
        cursor = None
        try:
            db = self.__conexion_bd.conexion1()
            if not db:
                print("Error: No se pudo conectar a la base de datos principal")
                return False
            
            cursor = db.cursor()
            cursor.execute(
                "SELECT 1 FROM Persona_natural WHERE ID_cliente = %s LIMIT 1",
                (cedula,)
            )
            existe = cursor.fetchone() is not None
            print(f"Verificando perfil cliente {cedula}: {'Completo' if existe else 'Incompleto'}")
            return existe
        except Exception as e:
            print(f"Error al verificar perfil cliente: {e}")
            traceback.print_exc()
            return False
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()
    
    def obtener_cliente_para_sesion(self, cedula: str) -> dict | None:
        """
        Obtiene los datos de un cliente para la sesion
        """
        db = None
        cursor = None
        try:
            db = self.__conexion_bd.conexion1()
            if not db:
                print("Error: No se pudo conectar a la base de datos principal")
                return None
            
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT 
                    c.ID_cliente AS cedula,
                    p.Nombre_cliente AS nombre,
                    p.Apellido_cliente AS apellido,
                    c.Celular_cliente AS celular,
                    c.Correo_cliente AS correo,
                    c.Direccion_cliente AS direccion
                FROM Cliente c
                INNER JOIN Persona_natural p ON c.ID_cliente = p.ID_cliente
                WHERE c.ID_cliente = %s
                LIMIT 1
                """,
                (cedula,)
            )
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener cliente: {e}")
            traceback.print_exc()
            return None
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()
    
    def obtener_empleado_para_sesion(self, cedula: str) -> dict | None:
        """
        Obtiene los datos de un empleado para la sesion
        """
        db = None
        cursor = None
        try:
            db = self.__conexion_bd.conexion1()
            if not db:
                print("Error: No se pudo conectar a la base de datos principal")
                return None
            
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT 
                    ID_empleado AS cedula,
                    Nombre_empleado AS nombre,
                    Apellido_empleado AS apellido,
                    Celular_empleado AS celular,
                    Correo_empleado AS correo,
                    Direccion_empleado AS direccion,
                    ID_cargo AS cargo
                FROM Empleado
                WHERE ID_empleado = %s
                LIMIT 1
                """,
                (cedula,)
            )
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener empleado: {e}")
            traceback.print_exc()
            return None
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()
    
    # ==================== METODOS ADICIONALES DE UTILIDAD ====================
    
    def obtener_rol_por_id(self, rol_id: int) -> dict | None:
        """
        Obtiene un rol por su ID
        """
        db = None
        cursor = None
        try:
            db = self.__conexion_bd.conexion2()
            if not db:
                return None
            
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, nombre, descripcion FROM rol WHERE id = %s LIMIT 1",
                (rol_id,)
            )
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener rol por ID: {e}")
            traceback.print_exc()
            return None
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()
    
    def obtener_usuario_por_id(self, usuario_id: str) -> dict | None:
        """
        Obtiene un usuario por su ID
        Reutiliza el metodo de Usuarios
        """
        try:
            return self._usuarios_model.obtener_usuario_por_id(usuario_id)
        except Exception as e:
            print(f"Error al obtener usuario por ID: {e}")
            traceback.print_exc()
            return None