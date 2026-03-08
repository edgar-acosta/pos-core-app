from pydantic import BaseModel
from typing import Optional


class EmpleadoCreate(BaseModel):
    nombre: str
    rol: str
    horario: Optional[str] = None
    actividades: Optional[str] = None
    salario: Optional[float] = None
    nomina_info: Optional[str] = None
    contacto: Optional[str] = None


class EmpleadoUpdate(BaseModel):
    nombre: Optional[str] = None
    rol: Optional[str] = None
    horario: Optional[str] = None
    actividades: Optional[str] = None
    salario: Optional[float] = None
    nomina_info: Optional[str] = None
    contacto: Optional[str] = None
    status: Optional[str] = None


class EmpleadoOut(BaseModel):
    id: int
    nombre: str
    rol: str
    horario: Optional[str]
    actividades: Optional[str]
    salario: Optional[float]
    nomina_info: Optional[str]
    contacto: Optional[str]
    status: Optional[str]

    model_config = {"from_attributes": True}


class UsuarioCreate(BaseModel):
    username: str
    password: str
    empleado_id: Optional[int] = None
    rol: Optional[str] = None


class UsuarioOut(BaseModel):
    id: int
    username: str
    rol: Optional[str]
    empleado_id: Optional[int]
    status: Optional[str] = None
    must_change_password: Optional[bool] = None

    model_config = {"from_attributes": True}


class UsuarioListItem(BaseModel):
    id: int
    username: str
    rol: Optional[str]
    empleado_id: Optional[int]
    empleado_nombre: Optional[str] = None
    status: Optional[str] = None
    must_change_password: bool = False
    last_login_at: Optional[str] = None
    failed_login_attempts: int = 0
    locked_until: Optional[str] = None
    created_by: Optional[str] = None


class UsuarioDeleteRequest(BaseModel):
    current_password: str


class UsuarioStatusUpdate(BaseModel):
    status: str
    current_password: str


class UsuarioResetPasswordRequest(BaseModel):
    new_password: str
    current_password: str


class UsuarioChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class AuditLogItem(BaseModel):
    id: int
    actor_username: str
    action: str
    target_type: str
    target_id: Optional[int] = None
    target_label: Optional[str] = None
    details: Optional[str] = None
    source_ip: Optional[str] = None
    created_at: Optional[str] = None
