from flask import Blueprint, jsonify, render_template, request, g, send_file
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.gestion_bd import MySQLDockerManager
import os
import tempfile
import datetime
from pathlib import Path

gestion_bd_blueprint = Blueprint("gestion_bd", __name__)

# Configuración de las bases de datos desde .env
DB_CONFIGS = {
    "ituaccesorio-bd": {
        "container_name": "mysql_db1",  # Cambia según tu contenedor
        "db_user": os.getenv("DB_USER", "user_flask"),
        "db_password": os.getenv("DB_PASSWORD", "12345678"),
        "db_name": os.getenv("DB_NAME1", "ituaccesoriobd"),
        "backup_dir": "backups/ituaccesorio"
    },
    "bd-seguridad": {
        "container_name": "mysql_db2",  # Cambia según tu contenedor
        "db_user": os.getenv("DB_USER", "user_flask"),
        "db_password": os.getenv("DB_PASSWORD2", "password_seguro"),
        "db_name": os.getenv("DB_NAME2", "seguridad"),
        "backup_dir": "backups/seguridad"
    }
}


@gestion_bd_blueprint.route("/seguridad_bd", methods=["GET"])
@jwt_required
def pagina_gestion_bd():
    return render_template(
        "seguridad_bd.html",
        show_navbar=True,
        show_notifications=True,
        active_page="seguridad_bd",
    )


@gestion_bd_blueprint.route("/api/backup/create", methods=["POST"])
@jwt_required

def crear_backup():
    """
    Endpoint para crear una copia de seguridad (descargar)
    Espera: { "database": "ituaccesorio-bd" o "bd-seguridad" }
    """
    try:
        data = request.get_json()
        database_name = data.get("database")
        
        if not database_name:
            return jsonify({"error": "Debe especificar la base de datos"}), 400
        
        if database_name not in DB_CONFIGS:
            return jsonify({"error": f"Base de datos '{database_name}' no válida"}), 400
        
        config = DB_CONFIGS[database_name]
        
        # Crear directorio de backups si no existe
        backup_dir = Path(config["backup_dir"])
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar el gestor de MySQL
        manager = MySQLDockerManager(
            container_name=config["container_name"],
            db_user=config["db_user"],
            db_name=config["db_name"],
            db_password=config["db_password"],
            backup_dir=config["backup_dir"]
        )
        
        # Crear el backup
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{database_name}_{timestamp}.sql"
        backup_path = manager.backup(filename=filename)
        
        if backup_path and Path(backup_path).exists():
            # Enviar el archivo como descarga
            return send_file(
                backup_path,
                as_attachment=True,
                download_name=filename,
                mimetype="application/sql"
            )
        else:
            return jsonify({"error": "Error al generar el backup"}), 500
            
    except Exception as e:
        print(f"Error en crear_backup: {str(e)}")
        return jsonify({"error": str(e)}), 500


@gestion_bd_blueprint.route("/api/backup/restore", methods=["POST"])
@jwt_required

def restaurar_backup():
    """
    Endpoint para restaurar una copia de seguridad (subir archivo)
    Espera form-data con:
        - database_name: "ituaccesorio-bd" o "bd-seguridad"
        - backup_file: archivo .sql, .gz o .zip
    """
    try:
        # Obtener datos del formulario
        database_name = request.form.get("database_name")
        
        if not database_name:
            return jsonify({"error": "Debe especificar la base de datos"}), 400
        
        if database_name not in DB_CONFIGS:
            return jsonify({"error": f"Base de datos '{database_name}' no válida"}), 400
        
        # Obtener el archivo
        if "backup_file" not in request.files:
            return jsonify({"error": "No se recibió ningún archivo"}), 400
        
        backup_file = request.files["backup_file"]
        
        if backup_file.filename == "":
            return jsonify({"error": "Nombre de archivo vacío"}), 400
        
        # Validar extensión
        allowed_extensions = {".sql", ".gz", ".zip"}
        file_ext = Path(backup_file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({"error": f"Extensión no permitida. Use: {', '.join(allowed_extensions)}"}), 400
        
        # Guardar archivo temporalmente
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp_file:
            backup_file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        config = DB_CONFIGS[database_name]
        
        # Si es un archivo comprimido, descomprimirlo
        sql_file_path = tmp_path
        if file_ext == ".gz":
            sql_file_path = descomprimir_gzip(tmp_path)
        elif file_ext == ".zip":
            sql_file_path = descomprimir_zip(tmp_path)
        
        # Inicializar el gestor de MySQL
        manager = MySQLDockerManager(
            container_name=config["container_name"],
            db_user=config["db_user"],
            db_name=config["db_name"],
            db_password=config["db_password"],
            backup_dir=config["backup_dir"]
        )
        
        # Restaurar la base de datos
        success = manager.restore(sql_file_path, drop_existing=True)
        
        # Limpiar archivos temporales
        limpiar_archivo_temporal(tmp_path)
        if sql_file_path != tmp_path:
            limpiar_archivo_temporal(sql_file_path)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Base de datos '{database_name}' restaurada exitosamente"
            }), 200
        else:
            return jsonify({"error": "Error al restaurar la base de datos"}), 500
            
    except Exception as e:
        print(f"Error en restaurar_backup: {str(e)}")
        return jsonify({"error": str(e)}), 500


@gestion_bd_blueprint.route("/api/backup/list", methods=["GET"])
@jwt_required

def listar_backups():
    """
    Endpoint para listar los backups disponibles
    Query param: database (opcional) - filtra por base de datos
    """
    try:
        database_name = request.args.get("database")
        
        if database_name and database_name not in DB_CONFIGS:
            return jsonify({"error": f"Base de datos '{database_name}' no válida"}), 400
        
        backups = {}
        
        # Si se especifica una BD, solo listar esa
        dbs_to_list = [database_name] if database_name else DB_CONFIGS.keys()
        
        for db_name in dbs_to_list:
            config = DB_CONFIGS[db_name]
            backup_dir = Path(config["backup_dir"])
            
            if backup_dir.exists():
                backups[db_name] = []
                for backup_file in sorted(backup_dir.glob("*.sql"), reverse=True):
                    stat = backup_file.stat()
                    backups[db_name].append({
                        "filename": backup_file.name,
                        "size_kb": round(stat.st_size / 1024, 2),
                        "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            else:
                backups[db_name] = []
        
        return jsonify({
            "success": True,
            "backups": backups
        }), 200
        
    except Exception as e:
        print(f"Error en listar_backups: {str(e)}")
        return jsonify({"error": str(e)}), 500


@gestion_bd_blueprint.route("/api/backup/delete", methods=["DELETE"])
@jwt_required

def eliminar_backup():
    """
    Endpoint para eliminar un backup específico
    Espera: { "database": "ituaccesorio-bd", "filename": "backup_xxx.sql" }
    """
    try:
        data = request.get_json()
        database_name = data.get("database")
        filename = data.get("filename")
        
        if not database_name or not filename:
            return jsonify({"error": "Debe especificar database y filename"}), 400
        
        if database_name not in DB_CONFIGS:
            return jsonify({"error": f"Base de datos '{database_name}' no válida"}), 400
        
        config = DB_CONFIGS[database_name]
        
        manager = MySQLDockerManager(
            container_name=config["container_name"],
            db_user=config["db_user"],
            db_name=config["db_name"],
            db_password=config["db_password"],
            backup_dir=config["backup_dir"]
        )
        
        success = manager.delete_backup(filename)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Backup '{filename}' eliminado exitosamente"
            }), 200
        else:
            return jsonify({"error": f"Backup '{filename}' no encontrado"}), 404
            
    except Exception as e:
        print(f"Error en eliminar_backup: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

def descomprimir_gzip(gz_path):
    """Descomprime un archivo .gz"""
    import gzip
    import shutil
    
    output_path = gz_path.replace(".gz", "")
    
    with gzip.open(gz_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    return output_path


def descomprimir_zip(zip_path):
    """Descomprime un archivo .zip y busca el archivo .sql"""
    import zipfile
    
    extract_dir = Path(zip_path).parent / "extracted"
    extract_dir.mkdir(exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    # Buscar el primer archivo .sql en el zip
    sql_files = list(extract_dir.glob("*.sql"))
    
    if not sql_files:
        raise Exception("El archivo ZIP no contiene ningún archivo .sql")
    
    return str(sql_files[0])


def limpiar_archivo_temporal(file_path):
    """Elimina un archivo temporal"""
    try:
        if file_path and Path(file_path).exists():
            Path(file_path).unlink()
    except Exception as e:
        print(f"Error al limpiar archivo temporal {file_path}: {e}")