import os
from uuid import uuid4

from flask import Blueprint, jsonify, render_template, request, current_app, g
from app.utils.helpers import guardar_fotos_evidencias
from app.utils.decorators import jwt_required, tiene_permiso, token_fotos_required
from app.utils.jwt_utils import crear_firma_fotos
from app.models.ordenes_servicio import Orden_servicio

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

        # Validación y guardado centralizados en app/utils/helpers.py
        # (whitelist de extensiones, 10 MB y máx. 20 fotos por orden)
        files = request.files.getlist('fotos')
        rutas_guardadas, error_fotos = guardar_fotos_evidencias(files, f"evidencias/taller/{id_orden}")
        if error_fotos:
            return jsonify({"error": error_fotos}), 400
        archivos_guardados = len(rutas_guardadas)

        # Rutas físicas para el rollback de la limpieza (necesarias si el
        # registro en BD falla y hay que borrar los archivos subidos)
        static_dir = current_app.static_folder
        carpeta_orden = os.path.join(static_dir, 'img', 'evidencias', 'taller', str(id_orden))
        
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