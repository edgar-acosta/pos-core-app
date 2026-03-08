import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta


TOKEN_SECRET = os.environ.get('POS_CORE_TOKEN_SECRET', 'pos-core-dev-secret')
TOKEN_TTL_MINUTES = int(os.environ.get('POS_CORE_TOKEN_TTL_MINUTES', '480'))
PASSWORD_MIN_LENGTH = 10


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def validate_password_strength(password: str):
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(f'La contraseña debe tener al menos {PASSWORD_MIN_LENGTH} caracteres')
    if password.lower() == password or password.upper() == password:
        raise ValueError('La contraseña debe incluir mayúsculas y minúsculas')
    if not any(ch.isdigit() for ch in password):
        raise ValueError('La contraseña debe incluir al menos un número')
    if not any(not ch.isalnum() for ch in password):
        raise ValueError('La contraseña debe incluir al menos un carácter especial')


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')


def _b64_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode('utf-8'))


def create_access_token(username: str, rol: str) -> tuple[str, str]:
    expires_at = datetime.utcnow() + timedelta(minutes=TOKEN_TTL_MINUTES)
    payload = {
        'sub': username,
        'rol': rol,
        'exp': int(expires_at.timestamp()),
        'iat': int(datetime.utcnow().timestamp()),
    }
    payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')
    payload_part = _b64_encode(payload_json)
    signature = hmac.new(TOKEN_SECRET.encode('utf-8'), payload_part.encode('utf-8'), hashlib.sha256).hexdigest()
    return f'{payload_part}.{signature}', expires_at.isoformat()


def decode_access_token(token: str) -> dict:
    try:
        payload_part, signature = token.split('.', 1)
    except ValueError as exc:
        raise ValueError('Token mal formado') from exc

    expected = hmac.new(TOKEN_SECRET.encode('utf-8'), payload_part.encode('utf-8'), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise ValueError('Firma de token inválida')

    payload = json.loads(_b64_decode(payload_part))
    if int(payload.get('exp', 0)) < int(datetime.utcnow().timestamp()):
        raise ValueError('La sesión ha expirado')
    return payload


def serialize_datetime(value):
    return value.isoformat() if value else None
