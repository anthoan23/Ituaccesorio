import subprocess
import os
import datetime
import tempfile
import gzip
import shutil
import zipfile
from pathlib import Path

class MySQLDockerManager:
    """
    Clase para gestionar copias de seguridad y restauración de MySQL en Docker
    """
    
    def __init__(self, container_name, db_user, db_name, db_password=None, backup_dir="backups"):
        """
        Inicializa la configuración
        
        Args:
            container_name: Nombre del contenedor Docker
            db_user: Usuario de MySQL
            db_name: Nombre de la base de datos
            db_password: Contraseña de MySQL (opcional)
            backup_dir: Directorio donde guardar los backups
        """
        self.container_name = container_name
        self.db_user = db_user
        self.db_name = db_name
        self.db_password = db_password
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_mysql_cmd_base(self):
        """
        Construye la base del comando MySQL para ejecutar dentro del contenedor
        
        Returns:
            str: Comando base de MySQL
        """
        if self.db_password:
            return f"docker exec -i {self.container_name} mysql -u{self.db_user} -p{self.db_password}"
        else:
            return f"docker exec -i {self.container_name} mysql -u{self.db_user}"
    
    def _get_mysqldump_cmd_base(self):
        """
        Construye la base del comando mysqldump para ejecutar dentro del contenedor
        
        Returns:
            str: Comando base de mysqldump
        """
        if self.db_password:
            return f"docker exec {self.container_name} mysqldump -u{self.db_user} -p{self.db_password}"
        else:
            return f"docker exec {self.container_name} mysqldump -u{self.db_user}"
    
    def backup(self, filename=None, compress=False):
        """
        Crea una copia de seguridad de la base de datos MySQL
        
        Args:
            filename: Nombre del archivo de backup (opcional)
            compress: Si es True, comprime el backup con gzip
            
        Returns:
            str: Ruta del archivo de backup creado
        """
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_{self.db_name}_{timestamp}.sql"
        
        backup_path = self.backup_dir / filename
        cmd = f"{self._get_mysqldump_cmd_base()} {self.db_name}"
        
        try:
            # Crear directorio si no existe
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            with open(backup_path, 'w', encoding='utf-8') as backup_file:
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    stdout=backup_file, 
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            if result.returncode == 0:
                size_kb = backup_path.stat().st_size / 1024
                print(f"✅ Backup creado exitosamente: {backup_path} ({size_kb:.2f} KB)")
                
                if compress:
                    return self._compress_file(backup_path)
                
                return str(backup_path)
            else:
                error_msg = result.stderr
                print(f"❌ Error al crear backup: {error_msg}")
                
                # Limpiar archivo si se creó pero hay error
                if backup_path.exists():
                    backup_path.unlink()
                
                return None
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    def backup_all_databases(self, filename=None, compress=False):
        """
        Crea backup de TODAS las bases de datos MySQL
        
        Args:
            filename: Nombre del archivo de backup (opcional)
            compress: Si es True, comprime el backup con gzip
            
        Returns:
            str: Ruta del archivo de backup creado
        """
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_all_databases_{timestamp}.sql"
        
        backup_path = self.backup_dir / filename
        cmd = f"{self._get_mysqldump_cmd_base()} --all-databases"
        
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            with open(backup_path, 'w', encoding='utf-8') as backup_file:
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    stdout=backup_file, 
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            if result.returncode == 0:
                size_kb = backup_path.stat().st_size / 1024
                print(f"✅ Backup de todas las BD creado: {backup_path} ({size_kb:.2f} KB)")
                
                if compress:
                    return self._compress_file(backup_path)
                
                return str(backup_path)
            else:
                print(f"❌ Error al crear backup: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    def backup_with_options(self, filename=None, options="", compress=False):
        """
        Crea backup con opciones personalizadas
        
        Args:
            filename: Nombre del archivo (opcional)
            options: Opciones adicionales para mysqldump
            compress: Si es True, comprime el backup
            
        Returns:
            str: Ruta del backup creado
        """
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_{self.db_name}_{timestamp}.sql"
        
        backup_path = self.backup_dir / filename
        cmd = f"{self._get_mysqldump_cmd_base()} {options} {self.db_name}"
        
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            with open(backup_path, 'w', encoding='utf-8') as backup_file:
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    stdout=backup_file, 
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            if result.returncode == 0:
                print(f"✅ Backup creado con opciones: {backup_path}")
                
                if compress:
                    return self._compress_file(backup_path)
                
                return str(backup_path)
            else:
                print(f"❌ Error al crear backup: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    def restore(self, sql_file_path, drop_existing=False):
        """
        Restaura la base de datos desde un archivo SQL
        
        Args:
            sql_file_path: Ruta al archivo SQL a restaurar
            drop_existing: Si es True, elimina la BD existente antes de restaurar
            
        Returns:
            bool: True si la restauración fue exitosa
        """
        sql_file = Path(sql_file_path)
        
        if not sql_file.exists():
            print(f"❌ El archivo {sql_file_path} no existe")
            return False
        
        # Verificar si es un archivo comprimido
        if sql_file.suffix == '.gz':
            sql_file_path = self._decompress_gzip(sql_file_path)
            sql_file = Path(sql_file_path)
        elif sql_file.suffix == '.zip':
            sql_file_path = self._decompress_zip(sql_file_path)
            sql_file = Path(sql_file_path)
        
        if sql_file.suffix != '.sql':
            print(f"⚠️ El archivo no tiene extensión .sql, pero se intentará restaurar igual")
        
        try:
            # Si se solicita eliminar la BD existente
            if drop_existing:
                if not self._drop_and_recreate_database():
                    return False
            
            # Restaurar la base de datos
            mysql_cmd = self._get_mysql_cmd_base()
            cmd = f"{mysql_cmd} {self.db_name}"
            
            with open(sql_file_path, 'r', encoding='utf-8') as sql_file_content:
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    stdin=sql_file_content,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            if result.returncode == 0:
                print(f"✅ Base de datos restaurada exitosamente desde {sql_file_path}")
                return True
            else:
                print(f"❌ Error al restaurar: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def restore_from_string(self, sql_content, drop_existing=False):
        """
        Restaura la base de datos desde un string SQL
        
        Args:
            sql_content: Contenido SQL como string
            drop_existing: Si es True, elimina la BD existente antes de restaurar
            
        Returns:
            bool: True si la restauración fue exitosa
        """
        tmp_file = None
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as tmp:
                tmp.write(sql_content)
                tmp_file = tmp.name
            
            result = self.restore(tmp_file, drop_existing)
            
            return result
            
        except Exception as e:
            print(f"❌ Error en restore_from_string: {str(e)}")
            return False
        finally:
            # Limpiar archivo temporal
            if tmp_file and Path(tmp_file).exists():
                try:
                    Path(tmp_file).unlink()
                except:
                    pass
    
    def restore_from_compressed(self, compressed_path, drop_existing=False):
        """
        Restaura desde un archivo comprimido (.gz o .zip)
        
        Args:
            compressed_path: Ruta al archivo comprimido
            drop_existing: Si es True, elimina la BD existente
            
        Returns:
            bool: True si la restauración fue exitosa
        """
        return self.restore(compressed_path, drop_existing)
    
    def list_backups(self):
        """
        Lista todos los backups disponibles
        
        Returns:
            list: Lista de diccionarios con información de los backups
        """
        backups = []
        extensions = ['*.sql', '*.sql.gz', '*.zip']
        
        for ext in extensions:
            backups.extend(list(self.backup_dir.glob(ext)))
        
        backups_info = []
        for backup in sorted(backups, reverse=True):
            size_kb = backup.stat().st_size / 1024
            modified_time = datetime.datetime.fromtimestamp(backup.stat().st_mtime)
            
            backups_info.append({
                "filename": backup.name,
                "path": str(backup),
                "size_kb": round(size_kb, 2),
                "size_mb": round(size_kb / 1024, 2),
                "modified": modified_time.strftime("%Y-%m-%d %H:%M:%S"),
                "extension": backup.suffix
            })
        
        if backups_info:
            print("\n📁 Backups disponibles:")
            print("-" * 60)
            for backup in backups_info:
                print(f"  📄 {backup['filename']}")
                print(f"     Tamaño: {backup['size_kb']} KB | Modificado: {backup['modified']}")
            print("-" * 60)
        else:
            print("❌ No hay backups disponibles")
        
        return backups_info
    
    def delete_backup(self, filename):
        """
        Elimina un archivo de backup específico
        
        Args:
            filename: Nombre del archivo a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        backup_path = self.backup_dir / filename
        
        if backup_path.exists():
            backup_path.unlink()
            print(f"✅ Backup eliminado: {filename}")
            return True
        else:
            print(f"❌ Backup no encontrado: {filename}")
            return False
    
    def delete_old_backups(self, days=30):
        """
        Elimina backups más antiguos que days días
        
        Args:
            days: Número de días de antigüedad
            
        Returns:
            int: Número de backups eliminados
        """
        cutoff_time = datetime.datetime.now() - datetime.timedelta(days=days)
        deleted_count = 0
        
        extensions = ['*.sql', '*.sql.gz', '*.zip']
        
        for ext in extensions:
            for backup in self.backup_dir.glob(ext):
                modified_time = datetime.datetime.fromtimestamp(backup.stat().st_mtime)
                if modified_time < cutoff_time:
                    backup.unlink()
                    deleted_count += 1
                    print(f"🗑️ Eliminado backup antiguo: {backup.name}")
        
        print(f"✅ Eliminados {deleted_count} backups con más de {days} días")
        return deleted_count
    
    def _compress_file(self, file_path):
        """
        Comprime un archivo usando gzip
        
        Args:
            file_path: Ruta del archivo a comprimir
            
        Returns:
            str: Ruta del archivo comprimido
        """
        compressed_file = f"{file_path}.gz"
        
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Obtener tamaños antes de eliminar original
        original_size = Path(file_path).stat().st_size / 1024
        compressed_size = Path(compressed_file).stat().st_size / 1024
        
        # Eliminar el original
        Path(file_path).unlink()
        
        print(f"✅ Backup comprimido: {compressed_file}")
        print(f"   Original: {original_size:.2f} KB → Comprimido: {compressed_size:.2f} KB")
        print(f"   Ahorro: {(1 - compressed_size/original_size) * 100:.1f}%")
        
        return compressed_file
    
    def _decompress_gzip(self, gz_path):
        """
        Descomprime un archivo .gz
        
        Args:
            gz_path: Ruta del archivo .gz
            
        Returns:
            str: Ruta del archivo descomprimido
        """
        output_path = gz_path.replace('.gz', '')
        
        with gzip.open(gz_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        print(f"✅ Archivo descomprimido: {output_path}")
        return output_path
    
    def _decompress_zip(self, zip_path):
        """
        Descomprime un archivo .zip y busca el archivo .sql
        
        Args:
            zip_path: Ruta del archivo .zip
            
        Returns:
            str: Ruta del archivo .sql encontrado
            
        Raises:
            Exception: Si no se encuentra ningún archivo .sql en el zip
        """
        extract_dir = Path(zip_path).parent / f"extracted_{Path(zip_path).stem}"
        extract_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Buscar el primer archivo .sql en el zip
        sql_files = list(extract_dir.glob("*.sql"))
        
        if not sql_files:
            raise Exception("El archivo ZIP no contiene ningún archivo .sql")
        
        print(f"✅ Archivo ZIP descomprimido: {sql_files[0]}")
        return str(sql_files[0])
    
    def _drop_and_recreate_database(self):
        """
        Elimina y recrea la base de datos MySQL
        
        Returns:
            bool: True si la operación fue exitosa
        """
        try:
            mysql_cmd = self._get_mysql_cmd_base()
            
            # Eliminar BD
            drop_cmd = f"{mysql_cmd} -e 'DROP DATABASE IF EXISTS {self.db_name};'"
            result = subprocess.run(drop_cmd, shell=True, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                print(f"❌ Error al eliminar BD: {result.stderr}")
                return False
            
            # Crear BD
            create_cmd = f"{mysql_cmd} -e 'CREATE DATABASE {self.db_name};'"
            result = subprocess.run(create_cmd, shell=True, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                print(f"❌ Error al crear BD: {result.stderr}")
                return False
            
            print(f"✅ Base de datos '{self.db_name}' recreada exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_connection(self):
        """
        Prueba la conexión a MySQL en el contenedor
        
        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            mysql_cmd = self._get_mysql_cmd_base()
            cmd = f"{mysql_cmd} -e 'SELECT 1'"
            
            result = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                print(f"✅ Conexión exitosa a MySQL en contenedor '{self.container_name}'")
                return True
            else:
                print(f"❌ Error de conexión: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def get_database_size(self):
        """
        Obtiene el tamaño de la base de datos
        
        Returns:
            dict: Información del tamaño de la BD
        """
        try:
            mysql_cmd = self._get_mysql_cmd_base()
            query = f"SELECT SUM(data_length + index_length) / 1024 / 1024 AS size_mb FROM information_schema.tables WHERE table_schema = '{self.db_name}';"
            cmd = f"{mysql_cmd} -e '{query}' --batch --skip-column-names"
            
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                size_mb = float(result.stdout.strip()) if result.stdout.strip() else 0
                print(f"📊 Tamaño de la BD '{self.db_name}': {size_mb:.2f} MB")
                return {"size_mb": round(size_mb, 2), "size_kb": round(size_mb * 1024, 2)}
            else:
                print(f"❌ Error al obtener tamaño: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    def get_table_list(self):
        """
        Obtiene la lista de tablas de la base de datos
        
        Returns:
            list: Lista de nombres de tablas
        """
        try:
            mysql_cmd = self._get_mysql_cmd_base()
            cmd = f"{mysql_cmd} {self.db_name} -e 'SHOW TABLES;' --batch --skip-column-names"
            
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                tables = [table.strip() for table in result.stdout.strip().split('\n') if table.strip()]
                print(f"📋 Tablas en '{self.db_name}': {len(tables)} tablas")
                return tables
            else:
                print(f"❌ Error al obtener tablas: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return []


# ============================================
# EJEMPLO DE USO
# ============================================

