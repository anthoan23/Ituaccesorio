import os
import jwt
from datetime import datetime, timedelta

SECRET = os.getenv('SECRET_KEY') or 'dev-secret'

def create_token(payload: dict, expires_minutes: int = 60) -> str:
    data = payload.copy()
    data['exp'] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    token = jwt.encode(data, SECRET, algorithm='HS256')
    # PyJWT returns a str
    return token

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
