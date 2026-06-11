from __future__ import annotations
import subprocess
import os
import tempfile
import re
from datetime import datetime
from flask import current_app

class Backup:
    """Clase para gestionar backups de bases de datos (similar a Cargo)"""
    
    def __init__(self, database_name: str = ""):
        self.database_name = database_name
        # Leer configuración directamente del .env
        self.db_configs = {
            'ituaccesoriobd': {
                'host': os.getenv('DB_HOST1', 'db1'),
                'port': os.getenv('DB_PORT', '3306'),
                'database': os.getenv('DB_NAME1', 'ituaccesoriobd'),
                'user': os.getenv('DB_USER', 'user_flask'),
                'password': os.getenv('DB_PASSWORD', '12345678')
            },
            'seguridad': {
                'host': os.getenv('DB_HOST2', 'db2'),
                'port': os.getenv('DB_PORT', '3306'),
                'database': os.getenv('DB_NAME2', 'seguridad'),
                'user': os.getenv('DB_USER', 'user_flask'),
                'password': os.getenv('DB_PASSWORD2', 'password_seguro')
            }
        }
    
    def listar_databases(self):
        """Lista las bases de datos disponibles (similar a listar_cargos)"""
        databases = [
            {
                'id': 'ituaccesoriobd',
                'nombre': 'Base de datos principal',
                'descripcion': 'Tablas de productos, cargos, especialidades, etc.',
                'host': self.db_configs['ituaccesoriobd']['host']
            },
            {
                'id': 'seguridad',
                'nombre': 'Base de datos de seguridad',
                'descripcion': 'Usuarios, roles, permisos y bitácora',
                'host': self.db_configs['seguridad']['host']
            }
        ]
        return databases
    
    def crear_backup(self) -> dict:
        """
        Crea un backup completo de la base de datos
        Incluye: tablas, datos, triggers, funciones, procedimientos
        """
        if self.database_name not in self.db_configs:
            return {
                'success': False,
                'message': f'Base de datos "{self.database_name}" no encontrada'
            }
        
        config = self.db_configs[self.database_name]
        
        # Crear nombre de archivo con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"backup_{self.database_name}_{timestamp}.sql"
        
        # Usar directorio temporal
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
        
        # Comando mysqldump completo
        cmd = [
            'mysqldump',
            f'--host={config["host"]}',
            f'--port={config["port"]}',
            f'--user={config["user"]}',
            f'--password={config["password"]}',
            '--routines',           # Procedimientos y funciones
            '--triggers',           # Triggers
            '--single-transaction', # Consistencia
            '--complete-insert',    # INSERTs completos
            '--skip-add-locks',
            '--default-character-set=utf8mb4',
            '--no-tablespaces',
            self.database_name
        ]
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=300
                )
            
            if result.returncode != 0:
                if os.path.exists(filepath):
                    os.remove(filepath)
                return {
                    'success': False,
                    'message': f'Error al crear backup: {result.stderr}'
                }
            
            if os.path.getsize(filepath) == 0:
                os.remove(filepath)
                return {
                    'success': False,
                    'message': 'El backup generado está vacío'
                }
            
            return {
                'success': True,
                'message': 'Backup creado exitosamente',
                'filename': filename,
                'filepath': filepath,
                'size_bytes': os.path.getsize(filepath),
                'database': self.database_name,
                'timestamp': timestamp
            }
            
        except subprocess.TimeoutExpired:
            if os.path.exists(filepath):
                os.remove(filepath)
            return {
                'success': False,
                'message': 'Timeout: El backup tomó demasiado tiempo'
            }
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return {
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            }
    
    def restaurar_backup(self, file_content: bytes) -> dict:
        """Restaura un backup en la base de datos"""
        if self.database_name not in self.db_configs:
            return {
                'success': False,
                'message': f'Base de datos "{self.database_name}" no encontrada'
            }
        
        config = self.db_configs[self.database_name]
        
        # Guardar archivo temporal
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f'restore_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sql')
        
        try:
            # Guardar el archivo
            with open(temp_file, 'wb') as f:
                f.write(file_content)
            
            if os.path.getsize(temp_file) == 0:
                return {
                    'success': False,
                    'message': 'El archivo de backup está vacío'
                }
            
            # Comando mysql para restaurar
            cmd = [
                'mysql',
                f'--host={config["host"]}',
                f'--port={config["port"]}',
                f'--user={config["user"]}',
                f'--password={config["password"]}',
                '--default-character-set=utf8mb4',
                self.database_name
            ]
            
            with open(temp_file, 'r', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd,
                    stdin=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=600
                )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'message': f'Error al restaurar backup: {result.stderr}'
                }
            
            return {
                'success': True,
                'message': f'Backup restaurado exitosamente en {self.database_name}'
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'Timeout: La restauración tomó demasiado tiempo'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            }
        finally:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass