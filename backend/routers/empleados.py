from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend import models
from backend.schemas import EmpleadoCreate, EmpleadoUpdate, EmpleadoOut
from backend.auth import require_roles

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/empleados", response_model=EmpleadoOut)
def create_empleado(
    payload: EmpleadoCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("dueno", "soporte")),
):
    nuevo = models.Empleado(**payload.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.get("/empleados", response_model=list[EmpleadoOut])
def list_empleados(
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("dueno", "soporte")),
):
    return db.query(models.Empleado).all()


@router.get("/empleados/{empleado_id}", response_model=EmpleadoOut)
def get_empleado(
    empleado_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("dueno", "soporte")),
):
    emp = db.query(models.Empleado).filter(models.Empleado.id == empleado_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return emp


@router.put("/empleados/{empleado_id}", response_model=EmpleadoOut)
def update_empleado(
    empleado_id: int,
    payload: EmpleadoUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("dueno", "soporte")),
):
    emp = db.query(models.Empleado).filter(models.Empleado.id == empleado_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(emp, k, v)
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@router.delete("/empleados/{empleado_id}")
def delete_empleado(
    empleado_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("dueno", "soporte")),
):
    emp = db.query(models.Empleado).filter(models.Empleado.id == empleado_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    emp.status = "inactivo"
    db.add(emp)
    db.commit()
    return {"ok": True, "id": empleado_id}
