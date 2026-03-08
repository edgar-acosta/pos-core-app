export const DEFAULT_ROLE_MODULES = {
  empleado: ['Registrar Venta', 'Inventarios'],
  dueno: ['Registrar Venta', 'Inventarios', 'Empleados', 'Reportes'],
  soporte: ['Registrar Venta', 'Inventarios', 'Empleados', 'Reportes', 'Mantenimiento'],
}

export function getAllowedModules(ui) {
  if (Array.isArray(ui?.allowed_modules) && ui.allowed_modules.length > 0) {
    return ui.allowed_modules
  }

  return DEFAULT_ROLE_MODULES[(ui?.rol || '').toLowerCase()] || []
}

export function canAccessModule(ui, moduleName) {
  return getAllowedModules(ui).includes(moduleName)
}
