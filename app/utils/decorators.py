from functools import wraps
from flask import request, jsonify, g
from app.utils.jwt_utils import decode_token

def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = None
        # Prefer cookie (HttpOnly) but accept Authorization header as fallback
        token = request.cookies.get('access_token')
        if not token:
            auth = request.headers.get('Authorization', '')
            if auth.startswith('Bearer '):
                token = auth.split(' ', 1)[1].strip()

        payload = decode_token(token)
        if not payload:
            return jsonify({"success": False, "error": "Autenticación requerida."}), 401

        # Attach user payload to g for handlers/templates
        g.user = payload
        return func(*args, **kwargs)

    return wrapper
