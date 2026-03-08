from fastapi import Depends, Header, HTTPException
from backend.database import SessionLocal
from backend import models
from backend.utils import decode_access_token
from datetime import datetime


def parse_token(token: str) -> dict:
    try:
        payload = decode_access_token(token)
        return {
            "username": payload.get("sub"),
            "rol": (payload.get("rol") or '').lower(),
            "exp": payload.get("exp"),
        }
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


def get_current_user(authorization: str = Header(default=None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization requerido")

    try:
        scheme, token = authorization.split(" ", 1)
    except ValueError:
        raise HTTPException(status_code=401, detail="Authorization inválido")

    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Esquema de autorización inválido")

    return parse_token(token.strip())


def get_current_db_user(user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        db_user = db.query(models.Usuario).filter(models.Usuario.username == user["username"]).first()
        if not db_user:
            raise HTTPException(status_code=401, detail="Usuario autenticado no encontrado")
        if (db_user.status or 'activo') != 'activo':
            raise HTTPException(status_code=403, detail='La cuenta no está disponible para iniciar sesión')
        if db_user.locked_until and db_user.locked_until > datetime.utcnow():
            raise HTTPException(status_code=423, detail='La cuenta está temporalmente bloqueada')
        return db_user
    finally:
        db.close()


def require_roles(*allowed_roles):
    allowed = {role.lower() for role in allowed_roles}

    def dependency(user=Depends(get_current_db_user)):
        if (user.rol or '').lower() not in allowed:
            raise HTTPException(status_code=403, detail="No autorizado para este recurso")
        return user

    return dependency
