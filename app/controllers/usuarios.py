import os
import uuid

from flask import Blueprint, jsonify, render_template, request, g, current_app
import mysql.connector
from werkzeug.utils import secure_filename
from app.utils.decorators import jwt_required, tiene_permiso, solo_roles
from app.models.usuarios import Usuarios
from app.models.bitacora import registrar_en_bitacora
from app.utils.jwt_utils import set_auth_cookies

usuarios_blueprint = Blueprint("usuarios", __name__)


def _guardar_foto_perfil(archivo):
    if not archivo or not getattr(archivo, "filename", ""):
        return None

    nombre_seguro = secure_filename(archivo.filename)
    _, extension = os.path.splitext(nombre_seguro)
    extension = extension.lower()[:10]
    nombre_final = f"{uuid.uuid4().hex}{extension}"

    carpeta_destino = os.path.join(current_app.static_folder, "img", "perfil")
    os.makedirs(carpeta_destino, exist_ok=True)

    ruta_fisica = os.path.join(carpeta_destino, nombre_final)
    archivo.save(ruta_fisica)
    return f"/static/img/perfil/{nombre_final}"


def _actualizar_cookie_usuario(resp, usuario_actual, usuario_db):
    payload = {
        "id": usuario_db.get("id"),
        "usuario_nombre": usuario_db.get("nombre"),
        "cedula": usuario_db.get("cedula_personal"),
        "rol_id": usuario_db.get("rol_id"),
        "rol_nombre": usuario_db.get("rol_nombre"),
        "foto_perfil": usuario_db.get("foto_perfil"),
        "perfil_completo": bool((usuario_actual or {}).get("perfil_completo", True)),
    }
    return set_auth_cookies(resp, payload)


# ==================== PÁGINAS ====================

@usuarios_blueprint.route("/usuarios", methods=["GET"])
@jwt_required
@solo_roles(['admin'])
def pagina_usuarios():
    return render_template(
        "usuarios.html",
        show_navbar=True,
        show_notifications=True,
        active_page="usuarios",
        current_user=g.user if isinstance(g.user, dict) else {},
    )


# ==================== ADMINISTRACIÓN DE USUARIOS (SOLO ADMIN) ====================

@usuarios_blueprint.route("/api/usuarios", methods=["GET"])
@jwt_required
@solo_roles(['admin'])
def api_listar_usuarios():
    usuario_model = Usuarios()
    usuarios = usuario_model.listar_usuarios()
    return jsonify({"success": True, "usuarios": usuarios or []})


@usuarios_blueprint.route("/api/usuarios/empleados", methods=["GET"])
@jwt_required
@solo_roles(['admin'])
def api_listar_empleados():
    usuario_model = Usuarios()
    empleados = usuario_model.listar_empleados()
    return jsonify({"success": True, "empleados": empleados or []})


@usuarios_blueprint.route("/api/usuarios/clientes", methods=["GET"])
@jwt_required
@solo_roles(['admin'])
def api_listar_clientes():
    from app.models.clientes import Clientes
    cliente_model = Clientes()
    clientes_raw = cliente_model.listar_clientes()
    
    # Verificar si hubo error en la consulta
    if not clientes_raw or isinstance(clientes_raw, str):
        return jsonify({"success": True, "clientes": []})
    
    # Transformar los datos al formato esperado por el frontend
    clientes_transformados = []
    for cliente in clientes_raw:
        if not isinstance(cliente, dict):
            continue
            
        clientes_transformados.append({
            "cedula": cliente.get("id", ""),
            "nombre_completo": cliente.get("nombre", ""),
            "celular": cliente.get("celular", ""),
            "correo": cliente.get("correo", ""),
            "tipo": cliente.get("tipo", "natural"),
            "apellido": cliente.get("apellido", ""),
            "razon_social": cliente.get("razon_social", ""),
            "rif": cliente.get("rif", "")
        })
    
    return jsonify({"success": True, "clientes": clientes_transformados})


@usuarios_blueprint.route("/api/usuarios", methods=["POST"])
@jwt_required
@solo_roles(['admin'])
def api_crear_usuario():
    # Obtener datos tanto de JSON como de form-data
    data = request.get_json(silent=True) or request.form
    
    # ========== DEBUG: Imprimir datos recibidos ==========
    print("=" * 50)
    print("DATOS RECIBIDOS EN API CREAR USUARIO:")
    print(f"Request method: {request.method}")
    print(f"Content-Type: {request.content_type}")
    print(f"Datos (form/json): {dict(data)}")
    print(f"Archivos recibidos: {list(request.files.keys())}")
    print("=" * 50)
    
    # ========== OBTENER Y LIMPIAR CAMPOS ==========
    nombre = data.get("nombre", "").strip()
    
    # IMPORTANTE: El frontend envía 'cedula_personal', no 'cedula'
    cedula = data.get("cedula_personal")
    if not cedula:
        cedula = data.get("cedula")  # Fallback por si usan otro nombre
    
    # Convertir a string y limpiar
    if cedula:
        cedula = str(cedula).strip()
    else:
        cedula = ""
    
    password = data.get("password", "").strip()
    rol_id = data.get("rol_id", "").strip()
    
    # Manejar foto de perfil
    foto_perfil = None
    if request.files.get("foto_perfil"):
        foto_perfil = _guardar_foto_perfil(request.files.get("foto_perfil"))
    elif data.get("foto_perfil_actual"):
        foto_perfil = data.get("foto_perfil_actual")
    
    # ========== DEBUG: Mostrar datos procesados ==========
    print("DATOS PROCESADOS:")
    print(f"  nombre: '{nombre}' (bool: {bool(nombre)})")
    print(f"  cedula: '{cedula}' (bool: {bool(cedula)})")
    print(f"  password: '{'*' * len(password)}' (bool: {bool(password)})")
    print(f"  rol_id: '{rol_id}' (bool: {bool(rol_id)})")
    print(f"  foto_perfil: {foto_perfil}")
    print("=" * 50)
    
    # ========== VALIDACIONES ==========
    if not nombre or not cedula or not password or not rol_id:
        error_msg = f"Faltan datos obligatorios: "
        error_details = []
        if not nombre: error_details.append("nombre")
        if not cedula: error_details.append("cédula")
        if not password: error_details.append("contraseña")
        if not rol_id: error_details.append("rol")
        error_msg += ", ".join(error_details)
        
        return jsonify({
            "success": False, 
            "error": error_msg,
            "received": {
                "nombre": bool(nombre),
                "cedula": bool(cedula),
                "password": bool(password),
                "rol_id": bool(rol_id)
            }
        }), 400
    
    # Validar longitud del nombre
    if len(nombre) > 50:
        return jsonify({
            "success": False, 
            "error": "El nombre no puede exceder los 50 caracteres."
        }), 400
    
    # Validar contraseña
    if len(password) < 6:
        return jsonify({
            "success": False, 
            "error": "La contraseña debe tener al menos 6 caracteres."
        }), 400
    
    if len(password) > 50:
        return jsonify({
            "success": False, 
            "error": "La contraseña no puede exceder los 50 caracteres."
        }), 400
    
    # ========== CREAR MODELO DE USUARIO ==========
    usuario_model = Usuarios(
        nombre=nombre,
        cedula=cedula,
        password=password,
        rol_id=rol_id,
        foto_perfil=foto_perfil
    )
    
    # ========== EJECUTAR CREACIÓN ==========
    mensaje = usuario_model.agregar_usuario()
    
    print(f"RESULTADO AGREGAR USUARIO: {mensaje}")
    print("=" * 50)
    
    # ========== RESPUESTA ==========
    if "exitosamente" in mensaje:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Crear usuario",
            descripcion=f"Se creó el usuario: {nombre} - Cédula: {cedula} - Rol ID: {rol_id}",
            usuario_id=usuario_id,
            modulo_nombre="Usuarios"
        )
        
        return jsonify({
            "success": True, 
            "message": mensaje, 
            "id": usuario_model.id
        }), 201
    
    return jsonify({
        "success": False, 
        "error": mensaje
    }), 400


@usuarios_blueprint.route("/api/usuarios/<usuario_id>", methods=["PUT"])
@jwt_required
@solo_roles(['admin'])
def api_actualizar_usuario(usuario_id):
    data = request.get_json(silent=True) or request.form
    nombre = data.get("nombre", "").strip()
    cedula = data.get("cedula_personal") or data.get("cedula")
    password = data.get("password", "").strip()
    rol_id = data.get("rol_id", "").strip()
    foto_perfil = _guardar_foto_perfil(request.files.get("foto_perfil")) or data.get("foto_perfil_actual")

    if not nombre or not cedula or not rol_id:
        return jsonify({"success": False, "error": "Nombre, cédula y rol son obligatorios."}), 400

    usuario_model = Usuarios(
        id=usuario_id,
        nombre=nombre,
        cedula=cedula,
        password=password,
        rol_id=rol_id,
        foto_perfil=foto_perfil
    )
    mensaje = usuario_model.actualizar_usuario()

    if "exitosamente" in mensaje:
        usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Actualizar usuario",
            descripcion=f"Se actualizó el usuario ID: {usuario_id} - Nuevo nombre: {nombre} - Rol ID: {rol_id}",
            usuario_id=usuario_actual_id,
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400


@usuarios_blueprint.route("/api/usuarios/<usuario_id>", methods=["DELETE"])
@jwt_required
@solo_roles(['admin'])
def api_eliminar_usuario(usuario_id):
    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")

    if usuario_actual_id == usuario_id:
        return jsonify({"success": False, "error": "No puedes eliminar tu propio usuario."}), 403

    # Verificar el rol del usuario a eliminar
    usuario_model = Usuarios()
    usuario_objetivo = usuario_model.obtener_usuario_por_id(usuario_id)

    if not usuario_objetivo:
        return jsonify({"success": False, "error": "El usuario no existe."}), 404

    nombre_usuario = usuario_objetivo.get("nombre", "N/A")
    rol_objetivo = usuario_objetivo.get("rol_nombre", "").lower()

    # Verificar permisos para eliminar admin
    usuario_actual_rol = g.user.get("rol_nombre") if isinstance(g.user, dict) else getattr(g.user, "rol_nombre", "").lower()
    if rol_objetivo == "admin" and usuario_actual_rol != "admin":
        return jsonify({"success": False, "error": "Solo otro admin puede eliminar este usuario."}), 403

    usuario_model.id = usuario_id
    mensaje = usuario_model.eliminar_usuario()

    if "exitosamente" in mensaje:
        registrar_en_bitacora(
            accion="Eliminar usuario",
            descripcion=f"Se eliminó el usuario ID: {usuario_id} - Nombre: {nombre_usuario}",
            usuario_id=usuario_actual_id,
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400


# ==================== PERFIL PROPIO (TODOS LOS USUARIOS AUTENTICADOS) ====================

@usuarios_blueprint.route("/api/usuarios/mi-perfil", methods=["GET"])
@jwt_required
def api_obtener_mi_perfil():
    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", None)
    
    if not usuario_id or usuario_id == "SYSTEM":
        return jsonify({"success": False, "error": "No se pudo identificar al usuario actual."}), 401

    usuario_model = Usuarios()
    usuario = usuario_model.obtener_usuario_por_id(usuario_id)

    if not usuario:
        return jsonify({"success": False, "error": "El usuario actual no existe."}), 404

    return jsonify({"success": True, "usuario": usuario})


@usuarios_blueprint.route("/api/usuarios/mi-perfil", methods=["PUT"])
@jwt_required
def api_actualizar_mi_perfil():
    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", None)
    
    if not usuario_id or usuario_id == "SYSTEM":
        return jsonify({"success": False, "error": "No se pudo identificar al usuario actual."}), 401

    data = request.get_json(silent=True) or request.form
    nombre = data.get("nombre", "").strip()
    password = data.get("password", "").strip()
    foto_perfil = _guardar_foto_perfil(request.files.get("foto_perfil"))

    if not nombre:
        return jsonify({"success": False, "error": "El nombre es obligatorio."}), 400

    usuario_model = Usuarios()
    usuario_actual_db = usuario_model.obtener_usuario_por_id(usuario_id)

    if not usuario_actual_db:
        return jsonify({"success": False, "error": "El usuario actual no existe."}), 404

    if not foto_perfil:
        foto_perfil = usuario_actual_db.get("foto_perfil")

    mensaje = usuario_model.actualizar_perfil(
        usuario_id, nombre, password if password else None, foto_perfil
    )

    if "exitosamente" in mensaje:
        usuario_actualizado = usuario_model.obtener_usuario_por_id(usuario_id)

        registrar_en_bitacora(
            accion="Actualizar perfil",
            descripcion=f"Usuario actualizó su perfil",
            usuario_id=usuario_id,
            modulo_nombre="Usuarios"
        )

        resp = jsonify({"success": True, "message": mensaje, "usuario": usuario_actualizado})
        
        # Obtener el usuario actual para la cookie
        usuario_actual_data = {
            "perfil_completo": g.user.get("perfil_completo", True) if isinstance(g.user, dict) else getattr(g.user, "perfil_completo", True)
        }
        
        return _actualizar_cookie_usuario(resp, usuario_actual_data, usuario_actualizado)

    return jsonify({"success": False, "error": mensaje}), 400