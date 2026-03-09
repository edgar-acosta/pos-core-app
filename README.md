# POS Core App

Sistema base para punto de venta con backend en FastAPI y frontend en React/Vite.

## Funcionalidades actuales

- Autenticación con sesiones firmadas y expiración.
- Gestión de empleados con persistencia en SQLite.
- Gestión de credenciales solo para usuarios con rol `soporte`.
- Seguridad de usuarios:
  - política de contraseña fuerte,
  - cambio obligatorio de contraseña,
  - reset de contraseña por soporte,
  - bloqueo por intentos fallidos,
  - suspensión/bloqueo de usuarios,
  - auditoría de acciones.
- Matriz de permisos por rol:
  - `empleado`: ventas e inventarios,
  - `dueno`: ventas, inventarios, empleados y reportes,
  - `soporte`: todo + mantenimiento.

## Estructura

- `backend/`: API, base de datos, autenticación, routers y utilidades.
- `frontend/`: interfaz React/Vite.
- `plugins/`: espacio para módulos enchufables.

## Requisitos

- Python 3.9+
- Node.js 18+
- npm

## Instalación

### Backend

```bash
cd backend
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Crear el primer usuario de soporte

La base de datos no se versiona. Después de clonar el repositorio, crea el primer usuario de soporte con:

```bash
python3 -m backend.bootstrap_support_user
```

El script es idempotente: si ya existe un usuario con rol `soporte`, no crea otro automáticamente.

## Ejecutar en desarrollo

### Backend

Desde la raíz del proyecto:

```bash
uvicorn backend.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

## Acceso

Después de crear el usuario de soporte, inicia sesión desde la UI en:

- `http://127.0.0.1:5173`

## Seguridad implementada

- Contraseñas hasheadas.
- Tokens firmados con expiración.
- Reconfirmación de contraseña para acciones críticas.
- Bitácora de auditoría de usuarios.
- Restricción backend por rol, no solo en frontend.

## Publicación

Ramas actuales:

- `develop`: rama de trabajo principal.
- `main`: rama estable/publicable.

## Sugerencias siguientes

- Separar administración de usuarios dentro de `Mantenimiento`.
- Añadir recuperación de contraseña con correo o flujo administrativo.
- Agregar tests automáticos para autenticación y permisos.
