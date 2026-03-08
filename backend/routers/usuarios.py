from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from backend.database import SessionLocal
from backend import models
from backend.schemas import (
    AuditLogItem,
    UsuarioChangePasswordRequest,
    UsuarioCreate,
    UsuarioDeleteRequest,
    UsuarioListItem,
    UsuarioOut,
    UsuarioResetPasswordRequest,
    UsuarioStatusUpdate,
)
from backend.utils import create_access_token, hash_password, serialize_datetime, validate_password_strength, verify_password
from backend.auth import require_roles, get_current_db_user

router = APIRouter()
MAX_FAILED_ATTEMPTS = 5
LOCK_MINUTES = 15


def write_audit(db, actor_username: str, action: str, target_type: str, target_id=None, target_label=None, details=None, source_ip=None):
    db.add(models.AuditLog(
        actor_username=actor_username,
        action=action,
        target_type=target_type,
        target_id=target_id,
        target_label=target_label,
        details=details,
        source_ip=source_ip,
    ))


def ensure_support_password(current_user, password: str):
    if not verify_password(password, current_user.password):
        raise HTTPException(status_code=403, detail='Contraseña de confirmación inválida')


def build_user_item(user, empleados_map):
    return UsuarioListItem(
        id=user.id,
        username=user.username,
        rol=user.rol,
        empleado_id=user.empleado_id,
        empleado_nombre=empleados_map.get(user.empleado_id),
        status=user.status,
        must_change_password=bool(user.must_change_password),
        last_login_at=serialize_datetime(user.last_login_at),
        failed_login_attempts=user.failed_login_attempts or 0,
        locked_until=serialize_datetime(user.locked_until),
        created_by=user.created_by,
    )


@router.post('/usuarios', response_model=UsuarioOut)
def create_usuario(
    payload: UsuarioCreate,
    current_user=Depends(get_current_db_user),
    _: dict = Depends(require_roles("soporte")),
    request: Request = None,
):
    db = SessionLocal()
    try:
        existing = db.query(models.Usuario).filter(models.Usuario.username == payload.username).first()
        if existing:
            raise HTTPException(status_code=409, detail='El nombre de usuario ya existe')

        role = payload.rol
        if not role and payload.empleado_id:
            emp = db.query(models.Empleado).filter(models.Empleado.id == payload.empleado_id).first()
            if emp:
                role = emp.rol

        if not role:
            raise HTTPException(status_code=400, detail='No se pudo determinar el rol del usuario')

        try:
            validate_password_strength(payload.password)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        hashed = hash_password(payload.password)
        nuevo = models.Usuario(
            username=payload.username,
            password=hashed,
            rol=role or 'empleado',
            empleado_id=payload.empleado_id,
            status='activo',
            must_change_password=True,
            created_by=current_user.username,
            password_changed_at=datetime.utcnow(),
        )
        db.add(nuevo)
        db.flush()
        write_audit(
            db,
            actor_username=current_user.username,
            action='usuario_creado',
            target_type='usuario',
            target_id=nuevo.id,
            target_label=payload.username,
            details=f'Rol: {role}',
            source_ip=request.client.host if request and request.client else None,
        )
        db.commit()
        db.refresh(nuevo)
        return nuevo
    finally:
        db.close()


@router.get('/usuarios', response_model=list[UsuarioListItem])
def list_usuarios(_: dict = Depends(require_roles("soporte"))):
    db = SessionLocal()
    try:
        usuarios = db.query(models.Usuario).order_by(models.Usuario.rol.desc(), models.Usuario.username.asc()).all()
        empleados = {e.id: e.nombre for e in db.query(models.Empleado).all()}
        return [build_user_item(u, empleados) for u in usuarios]
    finally:
        db.close()


@router.get('/usuarios/auditoria', response_model=list[AuditLogItem])
def list_audit_logs(_: dict = Depends(require_roles('soporte'))):
    db = SessionLocal()
    try:
        logs = db.query(models.AuditLog).order_by(models.AuditLog.created_at.desc()).limit(100).all()
        return [
            AuditLogItem(
                id=log.id,
                actor_username=log.actor_username,
                action=log.action,
                target_type=log.target_type,
                target_id=log.target_id,
                target_label=log.target_label,
                details=log.details,
                source_ip=log.source_ip,
                created_at=serialize_datetime(log.created_at),
            )
            for log in logs
        ]
    finally:
        db.close()


@router.patch('/usuarios/{usuario_id}/status')
def update_usuario_status(
    usuario_id: int,
    payload: UsuarioStatusUpdate,
    current_user=Depends(get_current_db_user),
    _: dict = Depends(require_roles('soporte')),
    request: Request = None,
):
    db = SessionLocal()
    try:
        current_db_user = db.query(models.Usuario).filter(models.Usuario.id == current_user.id).first()
        ensure_support_password(current_db_user, payload.current_password)
        user = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
        if not user:
            raise HTTPException(status_code=404, detail='Usuario no encontrado')
        if user.id == current_db_user.id and payload.status != 'activo':
            raise HTTPException(status_code=400, detail='No puedes desactivar tu propia cuenta')
        if payload.status not in {'activo', 'bloqueado', 'suspendido'}:
            raise HTTPException(status_code=400, detail='Estado inválido')
        user.status = payload.status
        if payload.status == 'activo':
            user.locked_until = None
            user.failed_login_attempts = 0
        write_audit(
            db,
            actor_username=current_db_user.username,
            action='usuario_estado_actualizado',
            target_type='usuario',
            target_id=user.id,
            target_label=user.username,
            details=f'Nuevo estado: {payload.status}',
            source_ip=request.client.host if request and request.client else None,
        )
        db.commit()
        return {'ok': True, 'id': user.id, 'status': user.status}
    finally:
        db.close()


@router.post('/usuarios/{usuario_id}/reset-password')
def reset_usuario_password(
    usuario_id: int,
    payload: UsuarioResetPasswordRequest,
    current_user=Depends(get_current_db_user),
    _: dict = Depends(require_roles('soporte')),
    request: Request = None,
):
    db = SessionLocal()
    try:
        current_db_user = db.query(models.Usuario).filter(models.Usuario.id == current_user.id).first()
        ensure_support_password(current_db_user, payload.current_password)
        try:
            validate_password_strength(payload.new_password)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        user = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
        if not user:
            raise HTTPException(status_code=404, detail='Usuario no encontrado')
        user.password = hash_password(payload.new_password)
        user.must_change_password = True
        user.failed_login_attempts = 0
        user.locked_until = None
        user.password_changed_at = datetime.utcnow()
        write_audit(
            db,
            actor_username=current_db_user.username,
            action='usuario_password_reseteado',
            target_type='usuario',
            target_id=user.id,
            target_label=user.username,
            details='Restablecimiento forzado por soporte',
            source_ip=request.client.host if request and request.client else None,
        )
        db.commit()
        return {'ok': True, 'id': user.id, 'must_change_password': True}
    finally:
        db.close()


@router.delete('/usuarios/{usuario_id}')
def delete_usuario(
    usuario_id: int,
    payload: UsuarioDeleteRequest,
    current_user=Depends(get_current_db_user),
    _: dict = Depends(require_roles("soporte")),
    request: Request = None,
):
    db = SessionLocal()
    try:
        current_db_user = db.query(models.Usuario).filter(models.Usuario.id == current_user.id).first()
        ensure_support_password(current_db_user, payload.current_password)

        user = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
        if not user:
            raise HTTPException(status_code=404, detail='Usuario no encontrado')

        if user.id == current_db_user.id:
            raise HTTPException(status_code=400, detail='No puedes eliminar tu propia cuenta')

        if (user.rol or '').lower() == 'soporte':
            soporte_count = db.query(models.Usuario).filter(models.Usuario.rol == 'soporte').count()
            if soporte_count <= 1:
                raise HTTPException(status_code=400, detail='Debe existir al menos un usuario de soporte')

        write_audit(
            db,
            actor_username=current_db_user.username,
            action='usuario_eliminado',
            target_type='usuario',
            target_id=user.id,
            target_label=user.username,
            details=f'Rol eliminado: {user.rol}',
            source_ip=request.client.host if request and request.client else None,
        )
        db.delete(user)
        db.commit()
        return {'ok': True, 'id': usuario_id}
    finally:
        db.close()


@router.post('/usuarios/change-password')
def change_own_password(
    payload: UsuarioChangePasswordRequest,
    current_user=Depends(get_current_db_user),
    request: Request = None,
):
    db = SessionLocal()
    try:
        db_user = db.query(models.Usuario).filter(models.Usuario.id == current_user.id).first()
        if not verify_password(payload.current_password, db_user.password):
            raise HTTPException(status_code=403, detail='La contraseña actual es incorrecta')
        try:
            validate_password_strength(payload.new_password)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if verify_password(payload.new_password, db_user.password):
            raise HTTPException(status_code=400, detail='La nueva contraseña debe ser distinta a la actual')
        db_user.password = hash_password(payload.new_password)
        db_user.must_change_password = False
        db_user.password_changed_at = datetime.utcnow()
        db_user.failed_login_attempts = 0
        db_user.locked_until = None
        write_audit(
            db,
            actor_username=db_user.username,
            action='usuario_password_cambiado',
            target_type='usuario',
            target_id=db_user.id,
            target_label=db_user.username,
            details='Cambio de contraseña realizado por el usuario',
            source_ip=request.client.host if request and request.client else None,
        )
        db.commit()
        return {'ok': True, 'must_change_password': False}
    finally:
        db.close()


@router.post('/auth/login')
def login(data: dict, request: Request):
    db = SessionLocal()
    try:
        user = db.query(models.Usuario).filter_by(username=data.get('username')).first()
        if not user:
            raise HTTPException(status_code=401, detail='Credenciales incorrectas')

        if (user.status or 'activo') != 'activo':
            raise HTTPException(status_code=403, detail='La cuenta no está activa')

        if user.locked_until and user.locked_until > datetime.utcnow():
            raise HTTPException(status_code=423, detail='La cuenta está bloqueada temporalmente por intentos fallidos')

        if not verify_password(data.get('password', ''), user.password):
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(minutes=LOCK_MINUTES)
                write_audit(
                    db,
                    actor_username=user.username,
                    action='usuario_bloqueado_por_intentos',
                    target_type='usuario',
                    target_id=user.id,
                    target_label=user.username,
                    details=f'Bloqueo temporal por {user.failed_login_attempts} intentos fallidos',
                    source_ip=request.client.host if request and request.client else None,
                )
            db.commit()
            raise HTTPException(status_code=401, detail='Credenciales incorrectas')

        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.utcnow()
        role = getattr(user, 'rol', 'empleado')
        token, expires_at = create_access_token(user.username, role)
        write_audit(
            db,
            actor_username=user.username,
            action='login_exitoso',
            target_type='usuario',
            target_id=user.id,
            target_label=user.username,
            details='Inicio de sesión correcto',
            source_ip=request.client.host if request and request.client else None,
        )
        db.commit()
        return {
            'token': token,
            'rol': role,
            'username': user.username,
            'must_change_password': bool(user.must_change_password),
            'expires_at': expires_at,
        }
    finally:
        db.close()
