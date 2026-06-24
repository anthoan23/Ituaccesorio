# app/controllers/backup.py
from flask import Blueprint, jsonify, render_template, request, g, current_app, send_file
import os
import datetime
import pymysql
from werkzeug.utils import secure_filename
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.backup import Backup

backup_blueprint = Blueprint("backup", __name__)

# Directorio donde se guardarán los backups
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'app', 'bd')


@backup_blueprint.route("/backup", methods=["GET"])
@jwt_required
@tiene_permiso('Backup', 'consultar')
def pagina_backup():
    """Página principal de respaldos"""
    return render_template(
        "backup.html",
        show_navbar=True,
        show_notifications=True,
        active_page="backup",
    )


@backup_blueprint.route("/api/backup/listar", methods=["GET"])
@jwt_required
@tiene_permiso('Backup', 'consultar')
def api_listar_backups():
    """Lista todos los respaldos registrados"""
    backup_model = Backup()
    backups = backup_model.listar_backups()
    return jsonify(backups)


@backup_blueprint.route("/api/backup/descargar/<int:id_backup>", methods=["GET"])
@jwt_required
@tiene_permiso('Backup', 'consultar')
def api_descargar_backup(id_backup):
    """Descarga el archivo de backup"""
    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
    
    # Obtener información del backup
    backup_model = Backup(id_usuario=usuario_id)
    backup_info = backup_model.obtener_info_backup(id_backup)
    
    if not backup_info:
        return jsonify({"success": False, "message": "No se encontró el backup"}), 404
    
    ruta_archivo = backup_info.get('direccion_bd')
    if not ruta_archivo or not os.path.exists(ruta_archivo):
        return jsonify({"success": False, "message": "El archivo de backup no existe"}), 404
    
    nombre_archivo = backup_info.get('nombre', f'backup_{id_backup}.sql')
    
    try:
        return send_file(
            ruta_archivo,
            as_attachment=True,
            download_name=nombre_archivo,
            mimetype='application/sql'
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al descargar: {str(e)}"}), 500


@backup_blueprint.route("/api/backup/crear", methods=["POST"])
@jwt_required
@tiene_permiso('Backup', 'registrar')
def api_crear_backup():
    """Crea un respaldo de la base de datos seleccionada usando pymysql"""
    data = request.get_json(silent=True) or {}
    tipo_bd = data.get("tipo_bd", "").strip()
    
    if tipo_bd not in ["seguridad", "ituaccesorio"]:
        return jsonify({"success": False, "message": "Tipo de base de datos inválido"}), 400

    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
    
    # Obtener configuración de la base de datos
    if tipo_bd == "seguridad":
        db_host = current_app.config.get('DB_HOST2', 'db2')
        db_name = current_app.config.get('DB_NAME2', 'seguridad')
        db_user = current_app.config.get('DB_USER', 'user_flask')
        db_password = current_app.config.get('DB_PASSWORD2', current_app.config.get('DB_PASSWORD', '12345678'))
    else:  # ituaccesorio
        db_host = current_app.config.get('DB_HOST1', 'db1')
        db_name = current_app.config.get('DB_NAME1', 'ituaccesoriobd')
        db_user = current_app.config.get('DB_USER', 'user_flask')
        db_password = current_app.config.get('DB_PASSWORD', '12345678')
    
    # Crear nombre del archivo
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"{tipo_bd}_backup_{timestamp}.sql"
    ruta_completa = os.path.join(BACKUP_DIR, nombre_archivo)
    
    # Asegurar que el directorio existe
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    connection = None
    try:
        # Conectar a la base de datos usando pymysql
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=3306,
            charset='utf8mb4',
            connect_timeout=30
        )
        
        # Generar el backup
        with open(ruta_completa, 'w', encoding='utf-8') as file:
            # Escribir cabecera
            file.write(f"-- ============================================\n")
            file.write(f"-- Backup de: {db_name}\n")
            file.write(f"-- Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"-- Tipo: {tipo_bd}\n")
            file.write(f"-- ============================================\n\n")
            
            file.write("SET FOREIGN_KEY_CHECKS=0;\n")
            file.write("SET AUTOCOMMIT=0;\n")
            file.write("SET SQL_QUOTE_SHOW_CREATE=1;\n\n")
            
            cursor = connection.cursor()
            
            # ========================================
            # 1. EXPORTAR TABLAS
            # ========================================
            file.write("-- ============================================\n")
            file.write("-- TABLAS\n")
            file.write("-- ============================================\n\n")
            
            # Obtener todas las tablas
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if not tables:
                return jsonify({
                    "success": False,
                    "message": "No se encontraron tablas en la base de datos"
                }), 400
            
            for table in tables:
                table_name = table[0]
                
                # Obtener la estructura de la tabla
                cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
                create_table = cursor.fetchone()[1]
                file.write(f"-- ----------------------------------------------------\n")
                file.write(f"-- Table structure for `{table_name}`\n")
                file.write(f"-- ----------------------------------------------------\n")
                file.write(f"DROP TABLE IF EXISTS `{table_name}`;\n")
                file.write(f"{create_table};\n\n")
                
                # Obtener los datos de la tabla
                cursor.execute(f"SELECT * FROM `{table_name}`")
                rows = cursor.fetchall()
                
                if rows:
                    # Obtener nombres de columnas
                    cursor.execute(f"DESCRIBE `{table_name}`")
                    columns = [col[0] for col in cursor.fetchall()]
                    
                    file.write(f"-- ----------------------------------------------------\n")
                    file.write(f"-- Dumping data for `{table_name}`\n")
                    file.write(f"-- ----------------------------------------------------\n")
                    
                    # Insertar datos en lotes
                    batch_size = 100
                    total_rows = len(rows)
                    
                    for i in range(0, total_rows, batch_size):
                        batch = rows[i:i+batch_size]
                        values_list = []
                        for row in batch:
                            values = []
                            for value in row:
                                if value is None:
                                    values.append('NULL')
                                elif isinstance(value, (int, float)):
                                    values.append(str(value))
                                elif isinstance(value, datetime.datetime):
                                    values.append(f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'")
                                elif isinstance(value, datetime.date):
                                    values.append(f"'{value.strftime('%Y-%m-%d')}'")
                                elif isinstance(value, datetime.time):
                                    values.append(f"'{value.strftime('%H:%M:%S')}'")
                                elif isinstance(value, (bytes, bytearray)):
                                    hex_str = value.hex()
                                    values.append(f"X'{hex_str}'")
                                else:
                                    escaped = str(value).replace("'", "''").replace("\\", "\\\\")
                                    values.append(f"'{escaped}'")
                            
                            values_list.append(f"({', '.join(values)})")
                        
                        file.write(f"INSERT INTO `{table_name}` (`{'`, `'.join(columns)}`) VALUES\n")
                        file.write(f",\n".join(values_list))
                        file.write(";\n\n")
            
            # ========================================
            # 2. EXPORTAR VISTAS
            # ========================================
            file.write("\n-- ============================================\n")
            file.write("-- VISTAS\n")
            file.write("-- ============================================\n\n")
            
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.VIEWS 
                WHERE TABLE_SCHEMA = %s
            """, (db_name,))
            views = cursor.fetchall()
            
            for view in views:
                view_name = view[0]
                try:
                    cursor.execute(f"SHOW CREATE VIEW `{view_name}`")
                    result = cursor.fetchone()
                    if result:
                        # El resultado puede tener 2 columnas: View, Create View
                        create_view = result[1] if len(result) > 1 else result[0]
                        file.write(f"-- ----------------------------------------------------\n")
                        file.write(f"-- View structure for `{view_name}`\n")
                        file.write(f"-- ----------------------------------------------------\n")
                        file.write(f"DROP VIEW IF EXISTS `{view_name}`;\n")
                        file.write(f"{create_view};\n\n")
                except Exception as e:
                    print(f"Error exporting view {view_name}: {e}")
            
            # ========================================
            # 3. EXPORTAR PROCEDIMIENTOS ALMACENADOS
            # ========================================
            file.write("\n-- ============================================\n")
            file.write("-- PROCEDIMIENTOS ALMACENADOS\n")
            file.write("-- ============================================\n\n")
            
            cursor.execute("""
                SELECT ROUTINE_NAME 
                FROM INFORMATION_SCHEMA.ROUTINES 
                WHERE ROUTINE_SCHEMA = %s 
                AND ROUTINE_TYPE = 'PROCEDURE'
            """, (db_name,))
            procedures = cursor.fetchall()
            
            for proc in procedures:
                proc_name = proc[0]
                try:
                    cursor.execute(f"SHOW CREATE PROCEDURE `{proc_name}`")
                    result = cursor.fetchone()
                    if result:
                        # El resultado tiene: Procedure, sql_mode, Create Procedure, character_set_client, collation_connection, Database Collation
                        create_proc = result[2] if len(result) > 2 else result[0]
                        file.write(f"-- ----------------------------------------------------\n")
                        file.write(f"-- Procedure structure for `{proc_name}`\n")
                        file.write(f"-- ----------------------------------------------------\n")
                        file.write(f"DROP PROCEDURE IF EXISTS `{proc_name}`;\n")
                        file.write(f"{create_proc};\n\n")
                except Exception as e:
                    print(f"Error exporting procedure {proc_name}: {e}")
            
            # ========================================
            # 4. EXPORTAR FUNCIONES
            # ========================================
            file.write("\n-- ============================================\n")
            file.write("-- FUNCIONES\n")
            file.write("-- ============================================\n\n")
            
            cursor.execute("""
                SELECT ROUTINE_NAME 
                FROM INFORMATION_SCHEMA.ROUTINES 
                WHERE ROUTINE_SCHEMA = %s 
                AND ROUTINE_TYPE = 'FUNCTION'
            """, (db_name,))
            functions = cursor.fetchall()
            
            for func in functions:
                func_name = func[0]
                try:
                    cursor.execute(f"SHOW CREATE FUNCTION `{func_name}`")
                    result = cursor.fetchone()
                    if result:
                        create_func = result[2] if len(result) > 2 else result[0]
                        file.write(f"-- ----------------------------------------------------\n")
                        file.write(f"-- Function structure for `{func_name}`\n")
                        file.write(f"-- ----------------------------------------------------\n")
                        file.write(f"DROP FUNCTION IF EXISTS `{func_name}`;\n")
                        file.write(f"{create_func};\n\n")
                except Exception as e:
                    print(f"Error exporting function {func_name}: {e}")
            
            # ========================================
            # 5. EXPORTAR TRIGGERS
            # ========================================
            file.write("\n-- ============================================\n")
            file.write("-- TRIGGERS\n")
            file.write("-- ============================================\n\n")
            
            cursor.execute("""
                SELECT TRIGGER_NAME 
                FROM INFORMATION_SCHEMA.TRIGGERS 
                WHERE TRIGGER_SCHEMA = %s
            """, (db_name,))
            triggers = cursor.fetchall()
            
            for trigger in triggers:
                trigger_name = trigger[0]
                try:
                    cursor.execute(f"SHOW CREATE TRIGGER `{trigger_name}`")
                    result = cursor.fetchone()
                    if result:
                        # El resultado tiene: Trigger, sql_mode, Create Trigger, character_set_client, collation_connection, Database Collation
                        create_trigger = result[2] if len(result) > 2 else result[0]
                        file.write(f"-- ----------------------------------------------------\n")
                        file.write(f"-- Trigger structure for `{trigger_name}`\n")
                        file.write(f"-- ----------------------------------------------------\n")
                        file.write(f"DROP TRIGGER IF EXISTS `{trigger_name}`;\n")
                        file.write(f"{create_trigger};\n\n")
                except Exception as e:
                    print(f"Error exporting trigger {trigger_name}: {e}")
            
            # ========================================
            # 6. EXPORTAR EVENTOS
            # ========================================
            file.write("\n-- ============================================\n")
            file.write("-- EVENTOS\n")
            file.write("-- ============================================\n\n")
            
            cursor.execute("""
                SELECT EVENT_NAME 
                FROM INFORMATION_SCHEMA.EVENTS 
                WHERE EVENT_SCHEMA = %s
            """, (db_name,))
            events = cursor.fetchall()
            
            for event in events:
                event_name = event[0]
                try:
                    cursor.execute(f"SHOW CREATE EVENT `{event_name}`")
                    result = cursor.fetchone()
                    if result:
                        create_event = result[1] if len(result) > 1 else result[0]
                        file.write(f"-- ----------------------------------------------------\n")
                        file.write(f"-- Event structure for `{event_name}`\n")
                        file.write(f"-- ----------------------------------------------------\n")
                        file.write(f"DROP EVENT IF EXISTS `{event_name}`;\n")
                        file.write(f"{create_event};\n\n")
                except Exception as e:
                    print(f"Error exporting event {event_name}: {e}")
            
            # Finalizar
            file.write("\n-- ============================================\n")
            file.write("-- FIN DEL BACKUP\n")
            file.write("-- ============================================\n")
            file.write("SET FOREIGN_KEY_CHECKS=1;\n")
            file.write("COMMIT;\n")
        
        cursor.close()
        connection.close()
        
        # Verificar que el archivo se creó correctamente
        if not os.path.exists(ruta_completa) or os.path.getsize(ruta_completa) == 0:
            return jsonify({
                "success": False,
                "message": "El archivo de backup está vacío o no se pudo crear"
            }), 500
        
        # Registrar el backup en la base de datos
        backup_model = Backup(id_usuario=usuario_id)
        resultado = backup_model.registrar_backup(ruta_completa, nombre_archivo)
        
        if "exitosamente" in resultado:
            return jsonify({
                "success": True,
                "message": f"Backup creado exitosamente: {nombre_archivo}",
                "archivo": nombre_archivo
            }), 201
        else:
            if os.path.exists(ruta_completa):
                os.remove(ruta_completa)
            return jsonify({"success": False, "message": resultado}), 400
            
    except pymysql.Error as e:
        if os.path.exists(ruta_completa):
            try:
                os.remove(ruta_completa)
            except:
                pass
        return jsonify({
            "success": False,
            "message": f"Error de base de datos: {str(e)}"
        }), 500
    except Exception as e:
        if os.path.exists(ruta_completa):
            try:
                os.remove(ruta_completa)
            except:
                pass
        return jsonify({
            "success": False,
            "message": f"Error al crear backup: {str(e)}"
        }), 500


@backup_blueprint.route("/api/backup/subir", methods=["POST"])
@jwt_required
@tiene_permiso('Backup', 'registrar')
def api_subir_backup():
    """Sube un archivo de backup existente"""
    if 'archivo' not in request.files:
        return jsonify({"success": False, "message": "No se encontró el archivo"}), 400
    
    archivo = request.files['archivo']
    if archivo.filename == '':
        return jsonify({"success": False, "message": "No se seleccionó ningún archivo"}), 400
    
    tipo_bd = request.form.get("tipo_bd", "").strip()
    if tipo_bd not in ["seguridad", "ituaccesorio"]:
        return jsonify({"success": False, "message": "Tipo de base de datos inválido"}), 400
    
    # Verificar extensión
    if not archivo.filename.endswith('.sql'):
        return jsonify({"success": False, "message": "El archivo debe tener extensión .sql"}), 400
    
    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
    
    # Crear nombre de archivo único
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Acortar el nombre para evitar problemas de longitud
    nombre_base = secure_filename(archivo.filename)
    if len(nombre_base) > 30:
        nombre_base = nombre_base[:30] + '.sql'
    
    tipo_corto = "seg" if tipo_bd == "seguridad" else "itu"
    nombre_archivo = f"{tipo_corto}_sub_{timestamp}_{nombre_base}"
    
    # Limitar la longitud total
    if len(nombre_archivo) > 100:
        base_sin_ext = nombre_base.replace('.sql', '')
        if len(base_sin_ext) > 20:
            base_sin_ext = base_sin_ext[:20]
        nombre_archivo = f"{tipo_corto}_sub_{timestamp}_{base_sin_ext}.sql"
    
    ruta_completa = os.path.join(BACKUP_DIR, nombre_archivo)
    
    # Asegurar que el directorio existe
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    try:
        # Guardar el archivo
        archivo.save(ruta_completa)
        
        # Registrar el backup en la base de datos
        backup_model = Backup(id_usuario=usuario_id)
        resultado = backup_model.registrar_backup(ruta_completa, nombre_archivo)
        
        if "exitosamente" in resultado:
            return jsonify({
                "success": True,
                "message": f"Backup subido exitosamente: {nombre_archivo}",
                "archivo": nombre_archivo
            }), 201
        else:
            # Si falla el registro, eliminar el archivo
            if os.path.exists(ruta_completa):
                os.remove(ruta_completa)
            return jsonify({"success": False, "message": resultado}), 400
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al subir backup: {str(e)}"}), 500


@backup_blueprint.route("/api/backup/eliminar/<int:id_backup>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Backup', 'eliminar')
def api_eliminar_backup(id_backup):
    """Elimina un respaldo"""
    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
    
    backup_model = Backup(id_usuario=usuario_id, id_backup=id_backup)
    resultado = backup_model.eliminar_backup(id_backup)
    
    if "exitosamente" in resultado:
        return jsonify({"success": True, "message": resultado}), 200
    else:
        return jsonify({"success": False, "message": resultado}), 400


@backup_blueprint.route("/api/backup/restaurar/<int:id_backup>", methods=["POST"])
@jwt_required
@tiene_permiso('Backup', 'modificar')
def api_restaurar_backup(id_backup):
    """Restaura un backup en la base de datos correspondiente"""
    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
    
    # Obtener información del backup
    backup_model = Backup(id_usuario=usuario_id)
    backup_info = backup_model.obtener_info_backup(id_backup)
    
    if not backup_info:
        return jsonify({"success": False, "message": "No se encontró el backup"}), 404
    
    # Determinar a qué base de datos pertenece el backup por el nombre
    nombre_archivo = backup_info.get('nombre', '')
    if 'seguridad' in nombre_archivo.lower() or 'seg' in nombre_archivo.lower():
        # Restaurar en base de datos de seguridad
        db_config = {
            'host': current_app.config.get('DB_HOST2', 'db2'),
            'database': current_app.config.get('DB_NAME2', 'seguridad'),
            'user': current_app.config.get('DB_USER', 'user_flask'),
            'password': current_app.config.get('DB_PASSWORD2', current_app.config.get('DB_PASSWORD', '12345678')),
            'port': 3306
        }
    else:
        # Restaurar en base de datos de ituaccesorio
        db_config = {
            'host': current_app.config.get('DB_HOST1', 'db1'),
            'database': current_app.config.get('DB_NAME1', 'ituaccesoriobd'),
            'user': current_app.config.get('DB_USER', 'user_flask'),
            'password': current_app.config.get('DB_PASSWORD', '12345678'),
            'port': 3306
        }
    
    # Ejecutar la restauración
    resultado = backup_model.restaurar_backup(id_backup, db_config)
    
    if resultado.get('success'):
        return jsonify({
            "success": True,
            "message": resultado.get('message'),
            "executed": resultado.get('executed', 0)
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": resultado.get('message', 'Error al restaurar el backup')
        }), 500