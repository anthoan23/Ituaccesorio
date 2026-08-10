import os
import uuid

from flask import Blueprint, jsonify, render_template, request, g, current_app
from werkzeug.utils import secure_filename
from app.utils.decorators import jwt_required, solo_roles
from app.models.usuarios import Usuarios
from app.utils.jwt_utils import set_auth_cookies
from app.models.modulos import Modulo
from app.models.permisos import Permiso
from app.models.roles import Rol
from app.models.clientes import Clientes
from app.utils.validators import (
    validar_texto,
    validar_numero,
    validar_solo_letras,
    validar_solo_letras_numeros,
    validar_contraseña,
    validar_cedula_venezolana,
    validar_sin_espacios,
    validar_sin_caracteres_especiales,
    validar_campo_comun
)

usuarios_blueprint = Blueprint("usuarios", __name__)


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
    cliente_model = Clientes()
    clientes_raw = cliente_model.listar_clientes()
    
    if not clientes_raw or isinstance(clientes_raw, str):
        return jsonify({"success": True, "clientes": []})
    
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
    data = request.get_json(silent=True) or request.form
    
    # Validar nombre
    nombre = data.get("nombre", "").strip()
    error = validar_solo_letras(nombre, 1, 50, "Nombre", permitir_espacios=True)
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    # Validar cédula
    cedula = data.get("cedula_personal") or data.get("cedula", "")
    error = validar_cedula_venezolana(cedula, "Cédula")
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    # Validar contraseña
    password = data.get("password", "").strip()
    error = validar_contraseña(password, 6, 50, "Contraseña")
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    # Validar rol
    rol_id = data.get("rol_id", "").strip()
    if not rol_id:
        return jsonify({"success": False, "error": "El campo Rol es obligatorio."}), 400
    
    error = validar_numero(rol_id, 1, 10, "Rol")
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    # Verificar que el rol exista
    from app.models.roles import Rol
    rol_model = Rol(id=rol_id)
    if not rol_model.verificar_rol_por_id():
        return jsonify({"success": False, "error": f"El rol con ID {rol_id} no existe."}), 400
    
    # Guardar foto de perfil
    foto_perfil = None
    archivo = request.files.get("foto_perfil")
    if archivo and getattr(archivo, "filename", ""):
        nombre_seguro = secure_filename(archivo.filename)
        _, extension = os.path.splitext(nombre_seguro)
        extension = extension.lower()[:10]
        nombre_final = f"{uuid.uuid4().hex}{extension}"
        
        carpeta_destino = os.path.join(current_app.static_folder, "img", "perfil")
        os.makedirs(carpeta_destino, exist_ok=True)
        
        ruta_fisica = os.path.join(carpeta_destino, nombre_final)
        archivo.save(ruta_fisica)
        foto_perfil = f"/static/img/perfil/{nombre_final}"
    elif data.get("foto_perfil_actual"):
        foto_perfil = data.get("foto_perfil_actual")
    
    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
    
    usuario_model = Usuarios(
        nombre=nombre,
        cedula=cedula,
        password=password,
        rol_id=rol_id,
        foto_perfil=foto_perfil,
        usuario_id=usuario_actual_id
    )
    
    mensaje = usuario_model.agregar_usuario()
    
    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje, "id": usuario_model.id}), 201
    
    return jsonify({"success": False, "error": mensaje}), 400


@usuarios_blueprint.route("/api/usuarios/<usuario_id>", methods=["PUT"])
@jwt_required
@solo_roles(['admin'])
def api_actualizar_usuario(usuario_id):
    data = request.get_json(silent=True) or request.form
    
    # Validar ID de usuario
    error = validar_numero(usuario_id, 1, 10, "Usuario")
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    # Validar nombre
    nombre = data.get("nombre", "").strip()
    error = validar_solo_letras(nombre, 1, 50, "Nombre", permitir_espacios=True)
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    # Validar cédula
    cedula = data.get("cedula_personal") or data.get("cedula", "")
    error = validar_cedula_venezolana(cedula, "Cédula")
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    # Validar contraseña (opcional)
    password = data.get("password", "").strip()
    if password:
        error = validar_contraseña(password, 6, 50, "Contraseña")
        if error:
            return jsonify({"success": False, "error": error}), 400
    
    # Validar rol
    rol_id = data.get("rol_id", "").strip()
    if not rol_id:
        return jsonify({"success": False, "error": "El campo Rol es obligatorio."}), 400
    
    error = validar_numero(rol_id, 1, 10, "Rol")
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    # Verificar que el rol exista
    from app.models.roles import Rol
    rol_model = Rol(id=rol_id)
    if not rol_model.verificar_rol_por_id():
        return jsonify({"success": False, "error": f"El rol con ID {rol_id} no existe."}), 400
    
    # Guardar foto de perfil
    foto_perfil = None
    archivo = request.files.get("foto_perfil")
    if archivo and getattr(archivo, "filename", ""):
        nombre_seguro = secure_filename(archivo.filename)
        _, extension = os.path.splitext(nombre_seguro)
        extension = extension.lower()[:10]
        nombre_final = f"{uuid.uuid4().hex}{extension}"
        
        carpeta_destino = os.path.join(current_app.static_folder, "img", "perfil")
        os.makedirs(carpeta_destino, exist_ok=True)
        
        ruta_fisica = os.path.join(carpeta_destino, nombre_final)
        archivo.save(ruta_fisica)
        foto_perfil = f"/static/img/perfil/{nombre_final}"
    else:
        foto_perfil = data.get("foto_perfil_actual")

    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    usuario_model = Usuarios(
        id=usuario_id,
        nombre=nombre,
        cedula=cedula,
        password=password,
        rol_id=rol_id,
        foto_perfil=foto_perfil,
        usuario_id=usuario_actual_id
    )
    
    mensaje = usuario_model.actualizar_usuario()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400


@usuarios_blueprint.route("/api/usuarios/<usuario_id>", methods=["DELETE"])
@jwt_required
@solo_roles(['admin'])
def api_eliminar_usuario(usuario_id):
    error = validar_numero(usuario_id, 1, 10, "Usuario")
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    if usuario_actual_id == usuario_id:
        return jsonify({"success": False, "error": "No puedes eliminar tu propio usuario."}), 403

    usuario_model_verif = Usuarios()
    usuario_objetivo = usuario_model_verif.obtener_usuario_por_id(usuario_id)

    if not usuario_objetivo:
        return jsonify({"success": False, "error": "El usuario no existe."}), 404

    rol_objetivo = usuario_objetivo.get("rol_nombre", "").lower()
    usuario_actual_rol = g.user.get("rol_nombre") if isinstance(g.user, dict) else getattr(g.user, "rol_nombre", "").lower()
    
    if rol_objetivo == "admin" and usuario_actual_rol != "admin":
        return jsonify({"success": False, "error": "Solo otro admin puede eliminar este usuario."}), 403

    usuario_model = Usuarios(id=usuario_id, usuario_id=usuario_actual_id)
    mensaje = usuario_model.eliminar_usuario()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400


# ==================== PERFIL PROPIO ====================

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
    
    # Validar nombre
    error = validar_solo_letras(nombre, 1, 50, "Nombre", permitir_espacios=True)
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    # Validar contraseña si se proporciona
    if password:
        error = validar_contraseña(password, 6, 50, "Contraseña")
        if error:
            return jsonify({"success": False, "error": error}), 400
    
    if not nombre:
        return jsonify({"success": False, "error": "El nombre es obligatorio."}), 400
    
    # Guardar foto de perfil
    foto_perfil = None
    archivo = request.files.get("foto_perfil")
    if archivo and getattr(archivo, "filename", ""):
        nombre_seguro = secure_filename(archivo.filename)
        _, extension = os.path.splitext(nombre_seguro)
        extension = extension.lower()[:10]
        nombre_final = f"{uuid.uuid4().hex}{extension}"
        
        carpeta_destino = os.path.join(current_app.static_folder, "img", "perfil")
        os.makedirs(carpeta_destino, exist_ok=True)
        
        ruta_fisica = os.path.join(carpeta_destino, nombre_final)
        archivo.save(ruta_fisica)
        foto_perfil = f"/static/img/perfil/{nombre_final}"

    usuario_model = Usuarios(usuario_id=usuario_id)
    usuario_actual_db = usuario_model.obtener_usuario_por_id(usuario_id)

    if not usuario_actual_db:
        return jsonify({"success": False, "error": "El usuario actual no existe."}), 404

    if not foto_perfil:
        foto_perfil = usuario_actual_db.get("foto_perfil")

    usuario_actualizacion = Usuarios(usuario_id=usuario_id)
    mensaje = usuario_actualizacion.actualizar_perfil(
        usuario_id, nombre, password if password else None, foto_perfil
    )

    if "exitosamente" in mensaje:
        usuario_actualizado = usuario_model.obtener_usuario_por_id(usuario_id)

        resp = jsonify({"success": True, "message": mensaje, "usuario": usuario_actualizado})
        
        # Actualizar cookie
        payload = {
            "id": usuario_actualizado.get("id"),
            "usuario_nombre": usuario_actualizado.get("nombre"),
            "cedula": usuario_actualizado.get("cedula_personal"),
            "rol_id": usuario_actualizado.get("rol_id"),
            "rol_nombre": usuario_actualizado.get("rol_nombre"),
            "foto_perfil": usuario_actualizado.get("foto_perfil"),
            "perfil_completo": g.user.get("perfil_completo", True) if isinstance(g.user, dict) else getattr(g.user, "perfil_completo", True),
        }
        return set_auth_cookies(resp, payload)

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
    error = validar_solo_letras_numeros(nombre, 1, 50, "Nombre", permitir_espacios=False)
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    descripcion = data.get("descripcion", "").strip()
    if descripcion:
        error = validar_sin_caracteres_especiales(descripcion, 1, 255, "Descripción", permitir_espacios=True)
        if error:
            return jsonify({"success": False, "error": error}), 400

    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    modulo_model = Modulo(
        nombre=nombre,
        descripcion=descripcion,
        usuario_id=usuario_actual_id
    )
    
    mensaje = modulo_model.agregar_modulo()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje, "id": modulo_model.id}), 201

    return jsonify({"success": False, "error": mensaje}), 400


@usuarios_blueprint.route("/api/modulos/<modulo_id>", methods=["PUT"])
@jwt_required
@solo_roles(['admin'])
def api_actualizar_modulo(modulo_id):
    data = request.get_json(silent=True) or {}
    
    error = validar_numero(modulo_id, 1, 10, "Módulo")
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    nombre = data.get("nombre", "").strip()
    error = validar_solo_letras_numeros(nombre, 1, 50, "Nombre", permitir_espacios=False)
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    descripcion = data.get("descripcion", "").strip()
    if descripcion:
        error = validar_sin_caracteres_especiales(descripcion, 1, 255, "Descripción", permitir_espacios=True)
        if error:
            return jsonify({"success": False, "error": error}), 400

    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    modulo_model = Modulo(
        id=modulo_id,
        nombre=nombre,
        descripcion=descripcion,
        usuario_id=usuario_actual_id
    )
    
    mensaje = modulo_model.actualizar_modulo()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400


@usuarios_blueprint.route("/api/modulos/<modulo_id>", methods=["DELETE"])
@jwt_required
@solo_roles(['admin'])
def api_eliminar_modulo(modulo_id):
    error = validar_numero(modulo_id, 1, 10, "Módulo")
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    modulo_model = Modulo(id=modulo_id, usuario_id=usuario_actual_id)
    mensaje = modulo_model.eliminar_modulo()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400


# ==================== PERMISOS ====================

@usuarios_blueprint.route("/api/permisos/rol/<rol_id>", methods=["GET"])
@jwt_required
@solo_roles(['admin'])
def api_obtener_permisos_por_rol(rol_id):
    error = validar_numero(rol_id, 1, 10, "Rol")
    if error:
        return jsonify({"success": False, "error": error}), 400
    
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
    error = validar_numero(rol_id, 1, 10, "Rol")
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    data = request.get_json(silent=True) or {}
    permisos = data.get("permisos", [])

    if not permisos:
        return jsonify({"success": False, "error": "Se requiere la lista de permisos."}), 400

    rol_model = Rol(id=rol_id)
    rol_existente = rol_model.obtener_rol_por_id()

    if not rol_existente:
        return jsonify({"success": False, "error": f"El rol con ID {rol_id} no existe."}), 404

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
            # Convertir a booleano
            registrar = permiso.get("registrar", False)
            if isinstance(registrar, str):
                registrar = registrar.lower() in {"1", "true", "on", "si", "yes"}
            modificar = permiso.get("modificar", False)
            if isinstance(modificar, str):
                modificar = modificar.lower() in {"1", "true", "on", "si", "yes"}
            eliminar = permiso.get("eliminar", False)
            if isinstance(eliminar, str):
                eliminar = eliminar.lower() in {"1", "true", "on", "si", "yes"}
            
            permisos_data.append({
                "modulo_id": modulo_id,
                "registrar": 1 if registrar else 0,
                "modificar": 1 if modificar else 0,
                "eliminar": 1 if eliminar else 0
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

    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")
    
    from app.models.bitacora import Bitacora
    bitacora = Bitacora(
        accion="Actualizar permisos de rol",
        descripcion=f"Se actualizaron {exitosos} permisos para el rol ID: {rol_id} - {rol_existente.get('nombre', 'N/A')}",
        usuario_id=usuario_actual_id,
        modulo_nombre="Usuarios"
    )
    bitacora.registrar()

    return jsonify({
        "success": True,
        "message": "Permisos actualizados correctamente.",
        "actualizados": exitosos
    })


@usuarios_blueprint.route("/api/permisos/rol/<rol_id>/modulo/<modulo_id>", methods=["GET"])
@jwt_required
@solo_roles(['admin'])
def api_obtener_permiso_especifico(rol_id, modulo_id):
    error = validar_numero(rol_id, 1, 10, "Rol")
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    error = validar_numero(modulo_id, 1, 10, "Módulo")
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    rol_model = Rol(id=rol_id)
    if not rol_model.verificar_rol_por_id():
        return jsonify({"success": False, "error": f"El rol con ID {rol_id} no existe."}), 404

    modulo_model = Modulo(id=modulo_id)
    modulo = modulo_model.obtener_modulo_por_id()
    if not modulo:
        return jsonify({"success": False, "error": f"El módulo con ID {modulo_id} no existe."}), 404

    permiso_model = Permiso(rol_id=rol_id, modulo_id=modulo_id)
    permisos = permiso_model.listar_permisos_completos_por_rol()
    
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
    error = validar_solo_letras(nombre, 1, 50, "Nombre", permitir_espacios=True)
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    descripcion = data.get("descripcion", "").strip()
    if descripcion:
        error = validar_sin_caracteres_especiales(descripcion, 1, 255, "Descripción", permitir_espacios=True)
        if error:
            return jsonify({"success": False, "error": error}), 400

    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    rol_model = Rol(
        nombre=nombre,
        descripcion=descripcion,
        usuario_id=usuario_actual_id
    )
    
    mensaje = rol_model.agregar_rol()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje, "id": rol_model.id}), 201

    return jsonify({"success": False, "error": mensaje}), 400


@usuarios_blueprint.route("/api/roles/<rol_id>", methods=["PUT"])
@jwt_required
@solo_roles(['admin'])
def api_actualizar_rol(rol_id):
    data = request.get_json(silent=True) or {}
    
    error = validar_numero(rol_id, 1, 10, "Rol")
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    nombre = data.get("nombre", "").strip()
    error = validar_solo_letras(nombre, 1, 50, "Nombre", permitir_espacios=True)
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    descripcion = data.get("descripcion", "").strip()
    if descripcion:
        error = validar_sin_caracteres_especiales(descripcion, 1, 255, "Descripción", permitir_espacios=True)
        if error:
            return jsonify({"success": False, "error": error}), 400

    rol_existente = Rol(id=rol_id)
    rol_data = rol_existente.obtener_rol_por_id()
    
    if rol_data and rol_data.get("nombre", "").lower() == "admin":
        usuario_actual = g.user.get("rol_nombre") if isinstance(g.user, dict) else getattr(g.user, "rol_nombre", "")
        if usuario_actual != "admin":
            return jsonify({"success": False, "error": "No se puede modificar el rol Admin."}), 403

    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    rol_model = Rol(
        id=rol_id,
        nombre=nombre,
        descripcion=descripcion,
        usuario_id=usuario_actual_id
    )
    
    mensaje = rol_model.actualizar_rol()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400


@usuarios_blueprint.route("/api/roles/<rol_id>", methods=["DELETE"])
@jwt_required
@solo_roles(['admin'])
def api_eliminar_rol(rol_id):
    error = validar_numero(rol_id, 1, 10, "Rol")
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    rol_existente = Rol(id=rol_id)
    rol_data = rol_existente.obtener_rol_por_id()
    
    if rol_data and rol_data.get("nombre", "").lower() == "admin":
        return jsonify({"success": False, "error": "No se puede eliminar el rol Admin."}), 403

    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id")

    rol_model = Rol(id=rol_id, usuario_id=usuario_actual_id)
    mensaje = rol_model.eliminar_rol()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 200

    return jsonify({"success": False, "error": mensaje}), 400