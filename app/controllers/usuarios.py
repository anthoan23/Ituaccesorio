import os
import uuid

from flask import Blueprint, jsonify, render_template, request, g, current_app
import mysql.connector
from werkzeug.utils import secure_filename
from app.utils.decorators import jwt_required, tiene_permiso, solo_roles
from app.models.usuarios import Usuarios
from app.models.bitacora import registrar_en_bitacora
from app.utils.jwt_utils import set_auth_cookies
from app.models.modulos import Modulo
from app.models.permisos import Permiso
from app.models.roles import Rol

usuarios_blueprint = Blueprint("usuarios", __name__)


def _bool(valor):
    if isinstance(valor, bool):
        return valor
    if valor is None:
        return 0
    if isinstance(valor, (int, float)):
        return 1 if int(valor) != 0 else 0
    texto = str(valor).strip().lower()
    return 1 if texto in {"1", "true", "on", "si", "yes"} else 0


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


# ==================== MÓDULOS ====================

@usuarios_blueprint.route("/api/modulos", methods=["GET"])
@jwt_required
@solo_roles(['admin'])
def api_listar_modulos():
    modulo_model = Modulo()
    modulos = modulo_model.listar_modulos()
    return jsonify({"success": True, "modulos": modulos or []})


@usuarios_blueprint.route("/api/modulos", methods=["POST"])
@jwt_required
@solo_roles(['admin'])
def api_crear_modulo():
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre", "").strip()
    descripcion = data.get("descripcion", "").strip()

    if not nombre:
        return jsonify({"success": False, "error": "El nombre del módulo es obligatorio."}), 400

    modulo_model = Modulo(nombre=nombre, descripcion=descripcion)
    mensaje = modulo_model.agregar_modulo()

    if "exitosamente" in mensaje:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Crear módulo",
            descripcion=f"Se creó el módulo: {nombre}",
            usuario_id=usuario_id,
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje, "id": modulo_model.id}), 201

    return jsonify({"success": False, "error": mensaje}), 400


@usuarios_blueprint.route("/api/modulos/<modulo_id>", methods=["PUT"])
@jwt_required
@solo_roles(['admin'])
def api_actualizar_modulo(modulo_id):
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre", "").strip()
    descripcion = data.get("descripcion", "").strip()

    if not nombre:
        return jsonify({"success": False, "error": "El nombre del módulo es obligatorio."}), 400

    modulo_model = Modulo(id=modulo_id, nombre=nombre, descripcion=descripcion)
    mensaje = modulo_model.actualizar_modulo()

    if "exitosamente" in mensaje:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Actualizar módulo",
            descripcion=f"Se actualizó el módulo ID: {modulo_id} - Nuevo nombre: {nombre}",
            usuario_id=usuario_id,
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400


@usuarios_blueprint.route("/api/modulos/<modulo_id>", methods=["DELETE"])
@jwt_required
@solo_roles(['admin'])
def api_eliminar_modulo(modulo_id):
    modulo_model = Modulo(id=modulo_id)
    mensaje = modulo_model.eliminar_modulo()

    if "exitosamente" in mensaje:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Eliminar módulo",
            descripcion=f"Se eliminó el módulo ID: {modulo_id}",
            usuario_id=usuario_id,
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400


# ==================== PERMISOS ====================

@usuarios_blueprint.route("/api/permisos/rol/<rol_id>", methods=["GET"])
@jwt_required
@solo_roles(['admin'])
def api_obtener_permisos_por_rol(rol_id):
    """Obtiene todos los permisos de un rol específico aplicando la regla de negocio"""
    # Verificar que el rol existe
    rol_model = Rol(id=rol_id)
    if not rol_model.verificar_rol_por_id():
        return jsonify({"success": False, "error": f"El rol con ID {rol_id} no existe."}), 404

    permiso_model = Permiso(rol_id=rol_id)
    permisos = permiso_model.listar_permisos_completos_por_rol()

    return jsonify({
        "success": True,
        "rol_id": rol_id,
        "permisos": permisos or []
    })


@usuarios_blueprint.route("/api/permisos/rol/<rol_id>", methods=["PUT"])
@jwt_required
@solo_roles(['admin'])
def api_actualizar_permisos_rol(rol_id):
    """Actualiza todos los permisos de un rol específico"""
    data = request.get_json(silent=True) or {}
    permisos = data.get("permisos", [])

    if not permisos:
        return jsonify({"success": False, "error": "Se requiere la lista de permisos."}), 400

    # Verificar que el rol existe
    rol_model = Rol(id=rol_id)
    rol_existente = rol_model.obtener_rol_por_id()

    if not rol_existente:
        return jsonify({"success": False, "error": f"El rol con ID {rol_id} no existe."}), 404

    # Verificar permisos para modificar admin (solo otro admin puede)
    nombre_rol = rol_existente.get("nombre", "").lower()
    usuario_actual = getattr(g, 'user', None)
    usuario_rol = ""
    if usuario_actual:
        if isinstance(usuario_actual, dict):
            usuario_rol = usuario_actual.get("rol_nombre", "").lower()
        else:
            usuario_rol = getattr(usuario_actual, "rol_nombre", "").lower()

    if nombre_rol == "admin" and usuario_rol != "admin":
        return jsonify({"success": False, "error": "No tienes permisos para modificar los permisos del rol Admin."}), 403

    # Preparar datos para guardado masivo
    permisos_data = []
    for permiso in permisos:
        modulo_id = permiso.get("modulo_id")
        if modulo_id:
            permisos_data.append({
                "modulo_id": modulo_id,
                "registrar": _bool(permiso.get("registrar", False)),
                "modificar": _bool(permiso.get("modificar", False)),
                "eliminar": _bool(permiso.get("eliminar", False))
            })

    if not permisos_data:
        return jsonify({"success": False, "error": "No hay permisos válidos para guardar."}), 400

    permiso_model = Permiso()
    exitosos, errores = permiso_model.guardar_permisos_masivos(rol_id, permisos_data)

    if errores:
        return jsonify({
            "success": False,
            "error": "Algunos permisos no se pudieron guardar.",
            "detalles": errores
        }), 500

    # Obtener ID del usuario desde g.user
    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")

    registrar_en_bitacora(
        accion="Actualizar permisos de rol",
        descripcion=f"Se actualizaron {exitosos} permisos para el rol ID: {rol_id} - {rol_existente.get('nombre', 'N/A')}",
        usuario_id=usuario_id,
        modulo_nombre="Usuarios"
    )

    return jsonify({
        "success": True,
        "message": "Permisos actualizados correctamente.",
        "actualizados": exitosos
    })


@usuarios_blueprint.route("/api/permisos/rol/<rol_id>/modulo/<modulo_id>", methods=["GET"])
@jwt_required
@solo_roles(['admin'])
def api_obtener_permiso_especifico(rol_id, modulo_id):
    """Obtiene un permiso específico de un rol para un módulo aplicando la regla de negocio"""
    # Verificar que el rol existe
    rol_model = Rol(id=rol_id)
    if not rol_model.verificar_rol_por_id():
        return jsonify({"success": False, "error": f"El rol con ID {rol_id} no existe."}), 404

    # Verificar que el módulo existe
    modulo_model = Modulo(id=modulo_id)
    modulo = modulo_model.obtener_modulo_por_id()
    if not modulo:
        return jsonify({"success": False, "error": f"El módulo con ID {modulo_id} no existe."}), 404

    permiso_model = Permiso(rol_id=rol_id, modulo_id=modulo_id)
    permisos = permiso_model.listar_permisos_completos_por_rol()
    
    # Buscar el permiso específico
    permiso = None
    for p in (permisos or []):
        if p["modulo_id"] == int(modulo_id):
            permiso = p
            break

    return jsonify({
        "success": True,
        "permiso": {
            "rol_id": rol_id,
            "modulo_id": modulo_id,
            "modulo_nombre": modulo["nombre"],
            "consultar": permiso.get("consultar", False) if permiso else False,
            "registrar": permiso.get("registrar", False) if permiso else False,
            "modificar": permiso.get("modificar", False) if permiso else False,
            "eliminar": permiso.get("eliminar", False) if permiso else False,
        }
    })


@usuarios_blueprint.route("/api/usuarios/mis-permisos", methods=["GET"])
@jwt_required
def api_obtener_mis_permisos():
    """Obtiene todos los permisos del usuario actual aplicando la regla de negocio"""
    # Obtener ID del usuario desde g.user
    usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", None)
    
    if not usuario_id or usuario_id == "SYSTEM":
        return jsonify({"success": False, "error": "No se pudo identificar al usuario."}), 401

    permiso_model = Permiso()
    permisos = permiso_model.obtener_permisos_usuario(usuario_id)

    return jsonify({"success": True, "permisos": permisos or []})


# ==================== ROLES ====================

@usuarios_blueprint.route("/api/roles", methods=["GET"])
@jwt_required
@solo_roles(['admin'])
def api_listar_roles():
    rol_model = Rol()
    roles = rol_model.listar_roles()
    return jsonify({"success": True, "roles": roles or []})


@usuarios_blueprint.route("/api/roles", methods=["POST"])
@jwt_required
@solo_roles(['admin'])
def api_crear_rol():
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre", "").strip()
    descripcion = data.get("descripcion", "").strip()

    if not nombre:
        return jsonify({"success": False, "error": "El nombre del rol es obligatorio."}), 400

    rol_model = Rol(nombre=nombre, descripcion=descripcion)
    mensaje = rol_model.agregar_rol()

    if "exitosamente" in mensaje:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Crear rol",
            descripcion=f"Se creó el rol: {nombre}",
            usuario_id=usuario_id,
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje, "id": rol_model.id}), 201

    return jsonify({"success": False, "error": mensaje}), 400


@usuarios_blueprint.route("/api/roles/<rol_id>", methods=["PUT"])
@jwt_required
@solo_roles(['admin'])
def api_actualizar_rol(rol_id):
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre", "").strip()
    descripcion = data.get("descripcion", "").strip()

    if not nombre:
        return jsonify({"success": False, "error": "El nombre del rol es obligatorio."}), 400

    # Verificar que no se esté modificando el rol Admin
    rol_existente = Rol(id=rol_id)
    rol_data = rol_existente.obtener_rol_por_id()
    
    if rol_data and rol_data.get("nombre", "").lower() == "admin":
        usuario_actual = g.user.get("rol_nombre") if isinstance(g.user, dict) else getattr(g.user, "rol_nombre", "")
        if usuario_actual != "admin":
            return jsonify({"success": False, "error": "No se puede modificar el rol Admin."}), 403

    rol_model = Rol(id=rol_id, nombre=nombre, descripcion=descripcion)
    mensaje = rol_model.actualizar_rol()

    if "exitosamente" in mensaje:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Actualizar rol",
            descripcion=f"Se actualizó el rol ID: {rol_id} - Nuevo nombre: {nombre}",
            usuario_id=usuario_id,
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400


@usuarios_blueprint.route("/api/roles/<rol_id>", methods=["DELETE"])
@jwt_required
@solo_roles(['admin'])
def api_eliminar_rol(rol_id):
    # Verificar que no se esté eliminando el rol Admin
    rol_existente = Rol(id=rol_id)
    rol_data = rol_existente.obtener_rol_por_id()
    
    if rol_data and rol_data.get("nombre", "").lower() == "admin":
        return jsonify({"success": False, "error": "No se puede eliminar el rol Admin."}), 403

    rol_model = Rol(id=rol_id)
    mensaje = rol_model.eliminar_rol()

    if "exitosamente" in mensaje:
        usuario_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Eliminar rol",
            descripcion=f"Se eliminó el rol ID: {rol_id}",
            usuario_id=usuario_id,
            modulo_nombre="Usuarios"
        )
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400