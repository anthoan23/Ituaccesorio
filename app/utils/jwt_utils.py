import os
import time
import hmac
import hashlib
import base64
import jwt
from datetime import datetime, timedelta

SECRET = os.getenv('SECRET_KEY') or 'dev-secret'
ACCESS_TOKEN_EXPIRES_MINUTES = 30
REFRESH_TOKEN_EXPIRES_MINUTES = 30
TOKEN_FOTOS_EXPIRES_MINUTES = 5

def create_token(payload: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRES_MINUTES) -> str:
    data = payload.copy()
    data['exp'] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    token = jwt.encode(data, SECRET, algorithm='HS256')
    # PyJWT returns a str
    return token


def create_access_token(payload: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRES_MINUTES) -> str:
    return create_token(payload, expires_minutes=expires_minutes)


def create_refresh_token(payload: dict, expires_minutes: int = REFRESH_TOKEN_EXPIRES_MINUTES) -> str:
    return create_token(payload, expires_minutes=expires_minutes)


def crear_firma_fotos(id_orden: str, expires_minutes: int = TOKEN_FOTOS_EXPIRES_MINUTES) -> str:
    """Crea una firma corta sin estado para subir fotos en taller_celular.

    No guarda nada en el servidor: la firma es HMAC(SECRET, "id_orden|expira")
    truncada, así que se verifica recalculándola. Va en la URL del QR (?t=...).
    """
    expira = int(time.time()) + expires_minutes * 60
    msg = f"{id_orden}|{expira}".encode()
    firma = hmac.new(SECRET.encode(), msg, hashlib.sha256).digest()
    firma_corta = base64.urlsafe_b64encode(firma[:10]).decode()
    return f"{expira}.{firma_corta}"


def verificar_firma_fotos(id_orden: str, valor: str) -> bool:
    """Verifica la firma corta de fotos para la orden indicada (stateless)."""
    if not valor:
        return False
    try:
        expira_s, firma_s = valor.split(".")
        expira = int(expira_s)
        if time.time() > expira:
            return False
        msg = f"{id_orden}|{expira}".encode()
        esperada = hmac.new(SECRET.encode(), msg, hashlib.sha256).digest()[:10]
        dada = base64.urlsafe_b64decode(firma_s.encode())
        return hmac.compare_digest(esperada, dada)
    except Exception:
        return False


def set_auth_cookies(response, payload: dict, secure: bool = False, samesite: str = 'Lax', path: str = '/'):
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    max_age = ACCESS_TOKEN_EXPIRES_MINUTES * 60
    response.set_cookie('access_token', access_token, httponly=True, samesite=samesite, secure=secure, path=path, max_age=max_age)
    response.set_cookie('refresh_token', refresh_token, httponly=True, samesite=samesite, secure=secure, path=path, max_age=max_age)
    return response


def clear_auth_cookies(response, path: str = '/'):
    response.set_cookie('access_token', '', expires=0, path=path)
    response.set_cookie('refresh_token', '', expires=0, path=path)
    return response

def decode_token(token: str) -> dict | None:
    if not token:
        return None
    try:
        data = jwt.decode(token, SECRET, algorithms=['HS256'])
        # Remove exp before returning
        data.pop('exp', None)
        return data
    except Exception:
        return None
