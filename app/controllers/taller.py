import os
from uuid import uuid4

from flask import Blueprint, jsonify, render_template, request, current_app, g
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.ordenes_servicio import Orden_servicio
from app.models.test import Tests
from app.models.inventario import Inventario

taller_blueprint = Blueprint("taller", __name__)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}





@taller_blueprint.route("/taller", methods=["GET"])
@jwt_required
@tiene_permiso('Taller', 'consultar')
def pagina_taller():
    return render_template(
        "taller.html",
        active_page="taller",
        show_navbar=True,
        show_notifications=True,
    )


@taller_blueprint.route("/api/taller/ordenes", methods=["GET"])
@jwt_required
@tiene_permiso('Taller', 'consultar')
def obtener_ordenes_taller():
    ordenes = Orden_servicio()
    resultado = ordenes.listar_ordenes_taller()
    return jsonify(resultado)


@taller_blueprint.route("/api/taller/reparaciones-asignadas", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'consultar')
def obtener_reparaciones_asignadas():
    # Obtener ID del empleado desde g.user
    usuario_id = g.user.get("cedula")

    ordenes = Orden_servicio(ID_empleado=usuario_id)
    resultado = ordenes.listar_ordenes_tecnico()
    return jsonify(resultado)


@taller_blueprint.route("/api/taller/consultar-ordene", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'consultar')
def consultar_orden():
    id_orden = request.json.get("id_orden")

    # Consultar la orden con todas sus fotos
    ordenes = Orden_servicio(ID_orden_servicio=id_orden)
    resultado_orden = ordenes.consultar_orden()
    
    # Consultar los tests (usando conexión independiente)
    tests = Tests(ID_orden=id_orden)
    resultado_tests = tests.listas_tests()

    # Validar resultado
    if resultado_orden is None:
        return jsonify({"error": "Error al consultar la orden"}), 500
    elif not resultado_orden:
        return jsonify({"error": "Orden no encontrada"}), 404

    # Devolver todo junto
    resultado = {
        "orden": resultado_orden, 
        "tests": resultado_tests if resultado_tests else [],
        "fotos": resultado_orden.get('fotos', [])
    }
    return jsonify(resultado)


@taller_blueprint.route("/api/taller/consultar-test", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'consultar')
def consultar_test():
    id_orden = request.json.get("id_orden")
    numero_test = request.json.get("numero_test")



    tests = Tests(ID_orden=id_orden, Numero_test=numero_test)
    resultado_test = tests.consultar_test()

    if resultado_test is None:
        return jsonify({"error": "Error al consultar el test"}), 500
    elif not resultado_test:
        return jsonify({"error": "Test no encontrado para la orden especificada"}), 404

    return jsonify(resultado_test)


@taller_blueprint.route("/api/taller/guardar-revision", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'editar')
def guardar_revision_tecnica():
    id_orden = request.json.get("id_orden")
    id_empleado = g.user.get("cedula")
    numero_test = request.json.get("numero_test")
    componentes = request.json.get("componentes_evaluados")

  

    # Obtener usuario actual para bitácora
    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    tests = Tests(
        ID_orden=id_orden,
        ID_empleado=id_empleado,
        Numero_test=numero_test,
        lista_tests=componentes,
        usuario_id=usuario_actual_id
    )

    # 4. Ejecutar el método que modificaste
    resultado_mensaje = tests.registrar_revision_test()

    # 5. Evaluar la respuesta del método para retornar el código HTTP correcto
    if "exitosamente" in resultado_mensaje:
        return jsonify({"mensaje": resultado_mensaje}), 200
    
    # Si devuelve algún mensaje de validación del ID, longitud o nulos
    elif "inválido" in resultado_mensaje or "obligatorio" in resultado_mensaje or "lista válida" in resultado_mensaje:
        return jsonify({"error": resultado_mensaje}), 400
        
    # Cualquier otro error interno de base de datos o excepciones (Exceptions)
    else:
        return jsonify({"error": resultado_mensaje}), 500


@taller_blueprint.route("/api/taller/asignar-orden", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'editar')
def asignar_orden_tecnico():
    id_orden = request.json.get("id_orden")
    id_empleado = g.user.get("cedula")

   
    ordenes = Orden_servicio(
        ID_orden_servicio=id_orden, 
        ID_empleado=id_empleado,
    )
    resultado = ordenes.asignar_orden_empleado()

    if resultado is True:
        return jsonify({"mensaje": "Técnico asignado exitosamente a la orden"}), 200
    else:
        return jsonify({"error": "Error al asignar el técnico a la orden"}), 500


@taller_blueprint.route("/api/taller/liberar-orden", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'editar')
def liberar_orden_tecnico():
    id_orden = request.json.get("id_orden")
    id_empleado = g.user.get("cedula")

    ordenes = Orden_servicio(ID_orden_servicio=id_orden, ID_empleado=id_empleado)
    resultado = ordenes.liberar_orden_empleado()

    if resultado is True:
        return jsonify({"mensaje": "Técnico liberado exitosamente de la orden"}), 200
    else:
        return jsonify({"error": "Error al liberar el técnico de la orden"}), 500


@taller_blueprint.route("/api/taller/consultar-inventario", methods=["GET"])
@jwt_required
@tiene_permiso('Taller', 'consultar')
def consultar_inventario():
    inventario = Inventario()
    resultado = inventario.listar_inventario_taller()
    return jsonify(resultado)


@taller_blueprint.route("/api/taller/guardar-reparacion", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'registrar')
def registrar_reparacion():
    try:
        # Obtener datos del request
        data = request.json
        
        # Validar campos obligatorios
        id_orden = data.get("id_orden")
        descripcion = data.get("descripcion_reparacion")
        id_empleado = g.user.get("cedula")
        
        
        # Procesar lista de repuestos (convertir a JSON si es necesario)
        repuestos = data.get("repuestos_utilizados")
        if repuestos and isinstance(repuestos, (list, dict)):
            import json
            repuestos = json.dumps(repuestos)
        
        
        # Crear instancia de Orden_servicio
        ordenes = Orden_servicio(
            ID_empleado=id_empleado,
            ID_orden_servicio=id_orden,
            Descripcion_reparacion=descripcion,
            lista_repuestos=repuestos,
        )
        
        # Registrar reparación
        resultado = ordenes.registrar_reparacion()
        
        # Procesar respuesta
        if resultado.get("success"):
            return jsonify({
                "mensaje": resultado.get("mensaje", "Reparación registrada exitosamente"),
                "data": resultado.get("data")
            }), 200
        else:
            error_msg = resultado.get("error", "Error desconocido")
            # Determinar código de estado según el error
            if any(palabra in error_msg.lower() for palabra in ["inválido", "obligatorio", "válida", "no encontrado"]):
                return jsonify({"error": error_msg}), 400
            elif "permiso" in error_msg.lower() or "autorización" in error_msg.lower():
                return jsonify({"error": error_msg}), 403
            else:
                return jsonify({"error": error_msg}), 500
                
    except Exception as e:
        print(f"Error en la ruta: {e}")
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    
@taller_blueprint.route("/api/taller/registrar-fotos", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'registrar')
def registrar_fotos():
    try:
        # Obtener datos del request (multipart/form-data)
        id_orden = request.form.get('id_orden')
        

        
        # Verificar que la orden existe
        ordenes = Orden_servicio(ID_orden_servicio=id_orden)
        orden_data = ordenes.consultar_orden()
        
        if not orden_data:
            return jsonify({"error": "Orden no encontrada"}), 404
        
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

@taller_blueprint.route("/api/taller/eliminar-fotos", methods=["DELETE"])
@jwt_required
@tiene_permiso('Taller', 'eliminar')
def eliminar_fotos():
    try:
        # Obtener datos del request
        data = request.json

        # Validar campo obligatorio
        id_foto = data.get("id_foto")
        if not id_foto:
            return jsonify({"error": "El ID de la foto es obligatorio"}), 400

        # Crear instancia de Orden_servicio
        ordenes = Orden_servicio(
            ID_foto_orden_servicio=id_foto
        )

        # Eliminar foto (ahora retorna un dict con la ruta)
        resultado = ordenes.eliminar_foto_orden_servicio()

        # Procesar respuesta
        if resultado.get("success"):
            # Eliminar el archivo físico
            ruta_foto = resultado.get('ruta_foto')
            id_orden = resultado.get('id_orden')
            
            if ruta_foto:
                try:
                    ruta_absoluta = os.path.join(current_app.root_path, ruta_foto.lstrip('/'))
                    if os.path.exists(ruta_absoluta):
                        os.remove(ruta_absoluta)
                        print(f"Archivo eliminado: {ruta_absoluta}")
                except Exception as e:
                    print(f"Error al eliminar archivo físico: {e}")
            
            # Verificar si la carpeta quedó vacía y eliminarla
            if id_orden:
                try:
                    base_path = os.path.join(current_app.root_path, 'static', 'img', 'evidencias', 'taller')
                    carpeta_orden = os.path.join(base_path, f'orden_{id_orden}')
                    if os.path.exists(carpeta_orden) and not os.listdir(carpeta_orden):
                        os.rmdir(carpeta_orden)
                        print(f"Carpeta eliminada: {carpeta_orden}")
                except Exception as e:
                    print(f"Error al eliminar carpeta: {e}")
            
            return jsonify({
                "success": True,
                "mensaje": resultado.get("mensaje")
            }), 200
        else:
            return jsonify({"error": resultado.get("error")}), 400

    except Exception as e:
        print(f"Error en la ruta: {e}")
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    
