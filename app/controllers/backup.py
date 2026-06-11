from flask import Blueprint, jsonify, render_template, request, g, send_file, after_this_request
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.bitacora import registrar_en_bitacora
from app.models.backup import Backup
import os

backup_blueprint = Blueprint('backup', __name__)

# Ruta para la página web (GET)
@backup_blueprint.route("/backup", methods=["GET"])
@jwt_required
@tiene_permiso('Backup', 'consultar')
def pagina_backup():
    return render_template(
        "backup.html",
        show_navbar=True,
        show_notifications=True,
        active_page="backup",
    )

# API: Listar bases de datos (GET)
@backup_blueprint.route("/api/backup/databases", methods=["GET"])
@jwt_required
@tiene_permiso('Backup', 'consultar')
def api_listar_databases():
    backup_model = Backup()
    databases = backup_model.listar_databases()
    return jsonify(databases)

# API: Crear backup (POST) - Descarga directa
@backup_blueprint.route("/api/backup", methods=["POST"])
@jwt_required
@tiene_permiso('Backup', 'crear_backup')
def api_crear_backup():
    data = request.get_json()
    database_name = data.get("database_name", "").strip()
    
    if not database_name:
        return jsonify({"success": False, "message": "El nombre de la base de datos es obligatorio."}), 400
    
    if database_name not in ['ituaccesoriobd', 'seguridad']:
        return jsonify({"success": False, "message": "Base de datos no válida."}), 400
    
    backup_model = Backup(database_name=database_name)
    result = backup_model.crear_backup()
    
    if not result['success']:
        return jsonify({"success": False, "message": result['message']}), 400
    
    # Registrar en bitácora
    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
    registrar_en_bitacora(
        accion="Crear backup",
        descripcion=f"Se creó backup de la base de datos {database_name} - Archivo: {result['filename']}",
        usuario_id=usuario_id,
        modulo_nombre="Backup"
    )
    
    # Enviar archivo y limpiar después
    response = send_file(
        result['filepath'],
        as_attachment=True,
        download_name=result['filename'],
        mimetype='application/sql'
    )
    
    @after_this_request
    def cleanup_files(response):
        try:
            if os.path.exists(result['filepath']):
                os.remove(result['filepath'])
        except:
            pass
        return response
    
    return response

# API: Restaurar backup (POST)
@backup_blueprint.route("/api/backup/restore", methods=["POST"])
@jwt_required
@tiene_permiso('Backup', 'restaurar_backup')
def api_restaurar_backup():
    database_name = request.form.get("database_name", "").strip()
    backup_file = request.files.get("backup_file")
    
    if not database_name:
        return jsonify({"success": False, "message": "El nombre de la base de datos es obligatorio."}), 400
    
    if not backup_file:
        return jsonify({"success": False, "message": "El archivo de backup es requerido."}), 400
    
    if database_name not in ['ituaccesoriobd', 'seguridad']:
        return jsonify({"success": False, "message": "Base de datos no válida."}), 400
    
    if not backup_file.filename.endswith('.sql'):
        return jsonify({"success": False, "message": "El archivo debe tener extensión .sql"}), 400
    
    # Leer contenido
    file_content = backup_file.read()
    
    # Verificar tamaño (100MB max)
    max_size = 100 * 1024 * 1024
    if len(file_content) > max_size:
        return jsonify({"success": False, "message": "El archivo es demasiado grande. Máximo 100MB"}), 400
    
    backup_model = Backup(database_name=database_name)
    result = backup_model.restaurar_backup(file_content)
    
    if result['success']:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        registrar_en_bitacora(
            accion="Restaurar backup",
            descripcion=f"Se restauró backup en la base de datos {database_name} - Archivo: {backup_file.filename}",
            usuario_id=usuario_id,
            modulo_nombre="Backup"
        )
        return jsonify(result), 200
    else:
        return jsonify(result), 400