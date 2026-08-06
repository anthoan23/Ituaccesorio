import os
from uuid import uuid4

from flask import Blueprint, jsonify, render_template, request, current_app, g
from app.utils.decorators import jwt_required, tiene_permiso, token_fotos_required
from app.utils.jwt_utils import crear_firma_fotos
from app.utils.validators import validar_numero, validar_texto, validar_texto_numero
from app.models.ordenes_servicio import Orden_servicio
from app.models.test import Tests
from app.models.inventario import Inventario

taller_celular_blueprint = Blueprint("taller_celular", __name__)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


@taller_celular_blueprint.route("/api/taller_celular/crear-token/<id_orden>", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'registrar')
def crear_token_fotos(id_orden):
    """Genera la firma corta de un solo propósito: subir fotos de la orden.

    Es stateless (HMAC con el SECRET_KEY): no se guarda nada en el servidor y
    la URL del QR queda corta y fácil de escanear.
    """
    try:
        firma = crear_firma_fotos(id_orden)
        return jsonify({"success": True, "firma": firma}), 200
    except Exception as e:
        print(f"❌ Error al crear firma de fotos: {e}")
        return jsonify({"error": "No se pudo generar la firma de fotos."}), 500


@taller_celular_blueprint.route("/taller_celular/<id_orden>", methods=["GET"])
@token_fotos_required
def pagina_taller_celular(id_orden):
    """Página para tomar fotos desde el celular para una orden específica"""
    token_payload = getattr(g, 'token_payload', None)
    if token_payload and str(token_payload.get('id_orden')) != str(id_orden):
        return render_template('403.html'), 403

    return render_template(
        "taller_celular.html",
        active_page="taller_celular",
        show_navbar=True,
        show_notifications=True,
        id_orden=id_orden  # Pasamos el ID de la orden a la plantilla
    )

@taller_celular_blueprint.route("/api/taller_celular/registrar-fotos", methods=["POST"])
@token_fotos_required
def registrar_fotos():
    try:
        # Obtener datos del request (multipart/form-data)
        id_orden = request.form.get('id_orden')
        if not id_orden:
            return jsonify({"error": "No se proporcionó el ID de la orden"}), 400

        # La firma solo es válida para la orden para la que fue emitida
        token_payload = getattr(g, 'token_payload', None)
        if token_payload and str(token_payload.get('id_orden')) != str(id_orden):
            return jsonify({"error": "La firma no corresponde a esta orden."}), 403

        # Obtener los archivos
        files = request.files.getlist('fotos')
        
        if not files or len(files) == 0:
            return jsonify({"error": "No se subieron archivos"}), 400
        
        # Limitar a máximo 20 fotos
        if len(files) > 20:
            return jsonify({"error": "Máximo 20 fotos permitidas por orden"}), 400
        
        # ============================================
        # 1. CONFIGURAR Y CREAR LAS RUTAS FÍSICAS
        # ============================================
        # current_app.root_path apunta a 'Ituaccesorio/app'
        
        static_dir = os.path.join(current_app.root_path, 'static')
        taller_dir = os.path.join(static_dir, 'img', 'evidencias', 'taller')
        
        # Crear la carpeta específica para el ID de la orden
        carpeta_orden = os.path.join(taller_dir, str(id_orden))
        
        # os.makedirs con exist_ok=True creará todas las carpetas padre si no existen
        os.makedirs(carpeta_orden, exist_ok=True)
        
        rutas_guardadas = []
        archivos_guardados = 0
        
        for file in files:
            if file.filename == '':
                continue
            
            # Validar extensión
            if '.' not in file.filename:
                continue
            
            extension = file.filename.rsplit('.', 1)[1].lower()
            if extension not in ALLOWED_IMAGE_EXTENSIONS:
                print(f"⚠️ Extensión no permitida: {extension}")
                continue
            
            # Validar tamaño (máximo 10MB)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > 10 * 1024 * 1024:  # 10MB
                print(f"⚠️ Archivo demasiado grande: {file_size} bytes")
                continue
            
            # Generar nombre único
            nombre_archivo = f"{uuid4().hex}.{extension}"
            ruta_completa = os.path.join(carpeta_orden, nombre_archivo)
            
            # Guardar archivo físicamente
            file.save(ruta_completa)
            print(f"✅ Archivo guardado físicamente en: {ruta_completa}")
            
            # RUTA RELATIVA PARA LA BASE DE DATOS (URL web accesible)
            ruta_relativa = f'/static/img/evidencias/taller/{id_orden}/{nombre_archivo}'
            rutas_guardadas.append(ruta_relativa)
            archivos_guardados += 1
        
        if archivos_guardados == 0:
            return jsonify({"error": "No se pudo guardar ningún archivo. Verifica formatos (JPG, PNG, WEBP) y tamaño (máx 10MB)"}), 400
        
        # ============================================
        # 2. REGISTRAR EN LA BASE DE DATOS
        # ============================================
        ordenes = Orden_servicio(
            ID_orden_servicio=id_orden,
            Foto_orden_servicio=rutas_guardadas
        )
        
        resultado = ordenes.registrar_fotos()
        
        # ============================================
        # 3. PROCESAR RESPUESTA
        # ============================================
        if resultado.get("success"):
            return jsonify({
                "success": True,
                "mensaje": f"{archivos_guardados} fotos subidas y registradas exitosamente",
                "total_subidas": archivos_guardados,
                "rutas": rutas_guardadas,
                "data": resultado.get("data")
            }), 200
        else:
            # Si falló el registro en BD, eliminar los archivos físicos usando static_dir definido arriba
            for ruta in rutas_guardadas:
                try:
                    # Removemos el '/' inicial para concatenar correctamente
                    ruta_absoluta = os.path.join(static_dir, ruta.replace('/static/', '', 1))
                    if os.path.exists(ruta_absoluta):
                        os.remove(ruta_absoluta)
                        print(f"🗑️ Archivo eliminado por rollback: {ruta_absoluta}")
                except Exception as e:
                    print(f"Error al eliminar archivo {ruta}: {e}")
            
            # Eliminar carpeta si quedó vacía
            try:
                if os.path.exists(carpeta_orden) and not os.listdir(carpeta_orden):
                    os.rmdir(carpeta_orden)
                    print(f"🗑️ Carpeta vacía eliminada: {carpeta_orden}")
            except Exception as e:
                print(f"Error al eliminar carpeta: {e}")
            
            error_msg = resultado.get("error", "Error al registrar fotos en la base de datos")
            return jsonify({"error": error_msg}), 500
                
    except Exception as e:
        print(f"❌ Error en registrar_fotos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500