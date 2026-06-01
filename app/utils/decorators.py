from functools import wraps
from flask import request, jsonify, g, make_response
from app.utils.jwt_utils import decode_token, set_auth_cookies


def _get_bearer_token():
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return auth.split(' ', 1)[1].strip()
    return None

def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.cookies.get('access_token') or _get_bearer_token()
        payload = decode_token(token)

        if not payload:
            refresh_token = request.cookies.get('refresh_token')
            payload = decode_token(refresh_token)

        if not payload:
            return jsonify({"success": False, "error": "Autenticación requerida."}), 401

        # Attach user payload to g for handlers/templates
        g.user = payload
        response = make_response(func(*args, **kwargs))

        if request.cookies.get('access_token') or request.cookies.get('refresh_token'):
            set_auth_cookies(response, payload)

        return response

    return wrapper
