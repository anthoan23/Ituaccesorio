from __future__ import annotations

import re
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.database import conectar
from app.models.roles import Rol


class LoginManager:
    """Modelo para gestionar autenticación y registro de usuarios"""
    
    def __init__(self):
        self.__conexion_bd = conectar()
    
    # ==================== MÉTODOS DE VALIDACIÓN ====================
    
    def validar_usuario(self, nombre: str, password: str) -> dict | None:
        """Valida las credenciales de un usuario"""
        db = self.__conexion_bd.conexion2()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT 
                    u.id, 
                    u.nombre, 
                    u.cedula, 
                    u.password, 
                    u.rol_id, 
                    u.foto_perfil, 
                    u.activo,
                    r.nombre AS rol_nombre
                FROM usuario u
                INNER JOIN rol r ON u.rol_id = r.id
                WHERE u.nombre = %s AND u.activo = 1
                """,
                (nombre,)
            )
            usuario = cursor.fetchone()
            
            if usuario and check_password_hash(usuario.get("password", ""), password):
                usuario.pop("password", None)
                return usuario
            
            return None
        except Exception as e:
            print(f"Error en validar_usuario: {e}")
            return None
        finally:
            cursor.close()
            db.close()
    
    # ==================== MÉTODOS DE REGISTRO ====================
    
    def obtener_rol_cliente(self) -> dict | None:
        """Obtiene el rol 'Cliente' del sistema"""
        db = self.__conexion_bd.conexion2()
        if not db:
            print("Error: No se pudo conectar a la base de datos de seguridad")
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, nombre, descripcion FROM rol WHERE LOWER(nombre) = 'cliente' LIMIT 1"
            )
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener rol cliente: {e}")
            return None
        finally:
            cursor.close()
            db.close()
    
    def verificar_usuario_existe_por_cedula(self, cedula: str) -> bool:
        """Verifica si un usuario ya existe por su cédula"""
        db = self.__conexion_bd.conexion2()
        if not db:
            return False
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM usuario WHERE cedula = %s LIMIT 1",
                (str(cedula),)
            )
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error al verificar usuario por cédula: {e}")
            return False
        finally:
            cursor.close()
            db.close()
    
    def verificar_usuario_existe_por_nombre(self, nombre: str) -> bool:
        """Verifica si un usuario ya existe por su nombre"""
        db = self.__conexion_bd.conexion2()
        if not db:
            return False
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM usuario WHERE nombre = %s LIMIT 1",
                (nombre,)
            )
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error al verificar usuario por nombre: {e}")
            return False
        finally:
            cursor.close()
            db.close()
    
    def crear_usuario(self, nombre: str, cedula: str, password: str, rol_id: int, foto_perfil: str = None) -> str | None:
        """
        Crea un nuevo usuario usando el procedimiento almacenado sp_registrar_usuario_con_prefijo
        
        Args:
            nombre: Nombre de usuario
            cedula: Cédula del usuario
            password: Contraseña en texto plano
            rol_id: ID del rol
            foto_perfil: Ruta de la foto de perfil (opcional)
        
        Returns:
            str: ID generado (ej: 'USR-001'), None si hubo error
        """
        db = self.__conexion_bd.conexion2()
        if not db:
            print("Error: No se pudo conectar a la base de datos")
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            password_hash = generate_password_hash(password)
            
            print(f"Llamando a procedimiento sp_registrar_usuario_con_prefijo con:")
            print(f"  nombre: {nombre}")
            print(f"  cedula: {cedula}")
            print(f"  rol_id: {rol_id}")
            
            # Llamar al procedimiento almacenado
            cursor.callproc('sp_registrar_usuario_con_prefijo', 
                          (nombre, cedula, password_hash, rol_id, foto_perfil))
            
            # Obtener el resultado (el ID generado)
            usuario_id = None
            for result in cursor.stored_results():
                row = result.fetchone()
                if row and 'id_generado' in row:
                    usuario_id = row['id_generado']
                    break
            
            db.commit()
            
            if usuario_id:
                print(f"Usuario creado con ID: {usuario_id}")
                return usuario_id
            else:
                print("Usuario creado pero no se pudo obtener el ID")
                return None
            
        except Exception as e:
            print(f"Error al crear usuario: {e}")
            db.rollback()
            return None
        finally:
            cursor.close()
            db.close()
    
    def crear_cliente_natural(self, cedula: str, nombre: str, apellido: str, 
                              celular: str, correo: str = None, direccion: str = None) -> bool:
        """Crea un cliente como persona natural"""
        db = self.__conexion_bd.conexion1()
        if not db:
            print("Error: No se pudo conectar a la base de datos principal")
            return False
        
        cursor = db.cursor()
        try:
            # Verificar si ya existe en Cliente
            cursor.execute(
                "SELECT 1 FROM Cliente WHERE ID_cliente = %s LIMIT 1",
                (str(cedula),)
            )
            existe_cliente = cursor.fetchone() is not None
            
            if not existe_cliente:
                # Insertar en Cliente
                cursor.execute(
                    """
                    INSERT INTO Cliente (ID_cliente, Direccion_cliente, Celular_cliente, Correo_cliente)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (str(cedula), direccion, celular, correo)
                )
                print(f"Cliente insertado: {cedula}")
            
            # Insertar en Persona_natural
            cursor.execute(
                """
                INSERT INTO Persona_natural (ID_cliente, Nombre_cliente, Apellido_cliente)
                VALUES (%s, %s, %s)
                """,
                (str(cedula), nombre, apellido)
            )
            
            db.commit()
            print(f"Cliente natural creado: {nombre} {apellido}")
            return True
            
        except Exception as e:
            print(f"Error detallado al crear cliente natural: {e}")
            db.rollback()
            return False
        finally:
            cursor.close()
            db.close()
    
    def verificar_perfil_completo_cliente(self, cedula: str) -> bool:
        """Verifica si un cliente tiene su perfil completo en Persona_natural"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return False
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM Persona_natural WHERE ID_persona_natural = %s LIMIT 1",
                (str(cedula),)
            )
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error al verificar perfil cliente: {e}")
            return False
        finally:
            cursor.close()
            db.close()
    
    def obtener_cliente_para_sesion(self, cedula: str) -> dict | None:
        """Obtiene los datos de un cliente para la sesión"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
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
                (str(cedula),)
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()