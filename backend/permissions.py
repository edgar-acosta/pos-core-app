MODULE_PERMISSIONS = {
    "empleado": ["Registrar Venta", "Inventarios"],
    "dueno": ["Registrar Venta", "Inventarios", "Empleados", "Reportes"],
    "soporte": ["Registrar Venta", "Inventarios", "Empleados", "Reportes", "Mantenimiento"],
}


def get_allowed_modules(role: str) -> list[str]:
    return MODULE_PERMISSIONS.get((role or "").lower(), [])
