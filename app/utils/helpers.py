# app/utils/helpers.py
import os
import uuid
from flask import g, current_app
from werkzeug.utils import secure_filename

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def obtener_usuario_autenticado_id():
    """Obtiene el ID del usuario autenticado"""
    usuario = getattr(g, "user", None)
    if not usuario:
        return None

    if isinstance(usuario, dict):
        return usuario.get("usuario_id") or usuario.get("user_id") or usuario.get("id")

    return getattr(usuario, "usuario_id", None) or getattr(usuario, "user_id", None) or getattr(usuario, "id", None)


def obtener_usuario_autenticado_info():
    """Obtiene la información completa del usuario autenticado"""
    usuario = getattr(g, "user", None)
    if not usuario:
        return {"id": "SYSTEM", "nombre": "SISTEMA", "foto": None}
    
    if isinstance(usuario, dict):
        user_id = usuario.get("usuario_id") or usuario.get("id") or "SYSTEM"
        user_name = usuario.get("usuario_nombre") or usuario.get("nombre") or usuario.get("username") or "USUARIO"
        user_foto = usuario.get("foto_perfil") or None
        return {"id": user_id, "nombre": user_name, "foto": user_foto}
    
    user_id = getattr(usuario, "usuario_id", None) or getattr(usuario, "id", None) or "SYSTEM"
    user_name = getattr(usuario, "usuario_nombre", None) or getattr(usuario, "nombre", None) or getattr(usuario, "username", None) or "USUARIO"
    user_foto = getattr(usuario, "foto_perfil", None) or None
    return {"id": user_id, "nombre": user_name, "foto": user_foto}


def es_imagen_permitida(nombre_archivo: str) -> bool:
    """Verifica si la extensión del archivo es una imagen permitida"""
    return "." in nombre_archivo and nombre_archivo.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def guardar_foto_inventario(archivo):
    """Guarda una foto de inventario y retorna su ruta"""
    if not archivo or not getattr(archivo, "filename", ""):
        return None

    if not es_imagen_permitida(archivo.filename):
        raise ValueError("La foto debe ser una imagen válida.")

    nombre_seguro = secure_filename(archivo.filename)
    _, extension = os.path.splitext(nombre_seguro)
    extension = extension.lower()[:10] or ".jpg"
    nombre_final = f"{uuid.uuid4().hex}{extension}"

    carpeta_destino = os.path.join(current_app.static_folder, "img", "evidencias", "inventario")
    os.makedirs(carpeta_destino, exist_ok=True)

    ruta_fisica = os.path.join(carpeta_destino, nombre_final)
    archivo.save(ruta_fisica)
    return f"/static/img/evidencias/inventario/{nombre_final}"