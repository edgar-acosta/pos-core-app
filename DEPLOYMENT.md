# Deployment Guide

## Desarrollo local

### Backend

```bash
uvicorn backend.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

## Producción recomendada

### Backend

Usar un proceso administrado (por ejemplo, `systemd`, `supervisor` o contenedor) y ejecutar:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Variables opcionales:

- `POS_CORE_TOKEN_SECRET`: secreto para firmar sesiones.
- `POS_CORE_TOKEN_TTL_MINUTES`: duración de sesión.

## Base de datos

Actualmente se usa SQLite en:

- `backend/core.db`

Para producción, se recomienda migrar a PostgreSQL y añadir migraciones formales.

## Bootstrap inicial

Después del despliegue, crea el usuario inicial de soporte desde la raíz del proyecto:

```bash
python3 -m backend.bootstrap_support_user
```

## Frontend build

```bash
cd frontend
npm run build
```

Servir el contenido generado en:

- `frontend/dist/`
