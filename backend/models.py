from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from backend.database import Base
from datetime import datetime


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    rol = Column(String)
    empleado_id = Column(Integer, nullable=True)
    status = Column(String, default="activo")
    must_change_password = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, nullable=True)
    created_by = Column(String, nullable=True)


class Empleado(Base):
    __tablename__ = "empleados"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    rol = Column(String, index=True)  # empleado, dueno, soporte
    horario = Column(String, nullable=True)
    actividades = Column(String, nullable=True)
    salario = Column(Float, nullable=True)
    nomina_info = Column(String, nullable=True)
    contacto = Column(String, nullable=True)
    status = Column(String, default="activo")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    actor_username = Column(String, nullable=False)
    action = Column(String, nullable=False)
    target_type = Column(String, nullable=False)
    target_id = Column(Integer, nullable=True)
    target_label = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    source_ip = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
