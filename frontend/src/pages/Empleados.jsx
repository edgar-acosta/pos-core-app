import React, { useEffect, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

function getToken() {
  return localStorage.getItem('token')
}

function authHeaders(extra = {}) {
  const token = getToken()
  return {
    ...extra,
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  }
}

export default function Empleados({ ui }) {
  const [empleados, setEmpleados] = useState([])
  const [usuarios, setUsuarios] = useState([])
  const [auditLogs, setAuditLogs] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadingUsuarios, setLoadingUsuarios] = useState(false)
  const [loadingAudit, setLoadingAudit] = useState(false)
  const currentRole = (ui?.rol || '').toLowerCase()
  const [credentialForm, setCredentialForm] = useState({ empleado_id: '', username: '', password: '' })
  const [form, setForm] = useState({
    id: null,
    nombre: '',
    rol: 'empleado',
    horario: '',
    actividades: '',
    salario: '',
    nomina_info: '',
    contacto: ''
  })

  useEffect(() => {
    loadEmpleados()
    if (currentRole === 'soporte') {
      loadUsuarios()
      loadAuditLogs()
    }
  }, [currentRole])

  async function loadEmpleados() {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/empleados`, {
        headers: authHeaders()
      })
      const data = await res.json()
      setEmpleados(data || [])
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function loadUsuarios() {
    setLoadingUsuarios(true)
    try {
      const res = await fetch(`${API_BASE}/usuarios`, { headers: authHeaders() })
      const data = await res.json()
      setUsuarios(Array.isArray(data) ? data : [])
    } catch (err) {
      console.error(err)
    } finally {
      setLoadingUsuarios(false)
    }
  }

  async function loadAuditLogs() {
    setLoadingAudit(true)
    try {
      const res = await fetch(`${API_BASE}/usuarios/auditoria`, { headers: authHeaders() })
      const data = await res.json()
      setAuditLogs(Array.isArray(data) ? data : [])
    } catch (err) {
      console.error(err)
    } finally {
      setLoadingAudit(false)
    }
  }

  function agrupadosPorRol() {
    const map = { dueno: [], soporte: [], empleado: [] }
    empleados.forEach(e => {
      const r = (e.rol || 'empleado').toLowerCase()
      if (!map[r]) map[r] = []
      map[r].push(e)
    })
    return map
  }

  function resetForm() {
    setForm({ id: null, nombre: '', rol: 'empleado', horario: '', actividades: '', salario: '', nomina_info: '', contacto: '' })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const payload = { ...form }
    if (payload.salario === '') payload.salario = null
    try {
      if (form.id) {
        await fetch(`${API_BASE}/empleados/${form.id}`, {
          method: 'PUT',
          headers: authHeaders({ 'Content-Type': 'application/json' }),
          body: JSON.stringify(payload)
        })
      } else {
        await fetch(`${API_BASE}/empleados`, {
          method: 'POST',
          headers: authHeaders({ 'Content-Type': 'application/json' }),
          body: JSON.stringify(payload)
        })
      }
      resetForm()
      loadEmpleados()
    } catch (err) {
      console.error(err)
    }
  }

  function startEdit(emp) {
    setForm({
      id: emp.id,
      nombre: emp.nombre || '',
      rol: emp.rol || 'empleado',
      horario: emp.horario || '',
      actividades: emp.actividades || '',
      salario: emp.salario || '',
      nomina_info: emp.nomina_info || '',
      contacto: emp.contacto || ''
    })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  async function handleDelete(id) {
    if (!confirm('¿Deseas marcar este empleado como inactivo?')) return
    try {
      await fetch(`${API_BASE}/empleados/${id}`, {
        method: 'DELETE',
        headers: authHeaders()
      })
      loadEmpleados()
    } catch (err) {
      console.error(err)
    }
  }

  function prepararCredenciales(emp) {
    setCredentialForm({
      empleado_id: String(emp.id),
      username: (emp.nombre || '').toLowerCase().replace(/\s+/g, '.'),
      password: ''
    })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  async function crearCredenciales(e) {
    e.preventDefault()
    if (!credentialForm.empleado_id || !credentialForm.username || !credentialForm.password) {
      alert('Completa empleado, usuario y contraseña')
      return
    }

    const empleado = empleados.find(item => String(item.id) === String(credentialForm.empleado_id))
    if (!empleado) {
      alert('Empleado no válido')
      return
    }

    try {
      const res = await fetch(`${API_BASE}/usuarios`, {
        method: 'POST',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({
          username: credentialForm.username,
          password: credentialForm.password,
          empleado_id: empleado.id,
          rol: empleado.rol
        })
      })
      const data = await res.json().catch(() => ({}))
      if (res.ok) {
        alert('Credenciales creadas')
        setCredentialForm({ empleado_id: '', username: '', password: '' })
        loadUsuarios()
        loadAuditLogs()
      } else {
        alert(data.detail || 'Error creando credenciales')
      }
    } catch (e) { console.error(e); alert('Error de conexión'); }
  }

  async function eliminarUsuario(usuario) {
    const currentPassword = prompt(`Confirma tu contraseña de soporte para eliminar a ${usuario.username}`)
    if (!currentPassword) return
    try {
      const res = await fetch(`${API_BASE}/usuarios/${usuario.id}`, {
        method: 'DELETE',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ current_password: currentPassword })
      })
      const data = await res.json().catch(() => ({}))
      if (res.ok) {
        alert('Usuario eliminado')
        loadUsuarios()
        loadAuditLogs()
      } else {
        alert(data.detail || 'No fue posible eliminar el usuario')
      }
    } catch (error) {
      console.error(error)
      alert('Error de conexión')
    }
  }

  async function cambiarEstadoUsuario(usuario) {
    const status = prompt('Nuevo estado: activo, bloqueado o suspendido', usuario.status || 'activo')
    if (!status) return
    const currentPassword = prompt(`Confirma tu contraseña de soporte para actualizar a ${usuario.username}`)
    if (!currentPassword) return
    try {
      const res = await fetch(`${API_BASE}/usuarios/${usuario.id}/status`, {
        method: 'PATCH',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ status: status.toLowerCase(), current_password: currentPassword })
      })
      const data = await res.json().catch(() => ({}))
      if (res.ok) {
        alert('Estado actualizado')
        loadUsuarios()
        loadAuditLogs()
      } else {
        alert(data.detail || 'No fue posible actualizar el estado')
      }
    } catch (error) {
      console.error(error)
      alert('Error de conexión')
    }
  }

  async function resetearPasswordUsuario(usuario) {
    const newPassword = prompt(`Nueva contraseña temporal para ${usuario.username}`)
    if (!newPassword) return
    const currentPassword = prompt('Confirma tu contraseña de soporte para continuar')
    if (!currentPassword) return
    try {
      const res = await fetch(`${API_BASE}/usuarios/${usuario.id}/reset-password`, {
        method: 'POST',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ new_password: newPassword, current_password: currentPassword })
      })
      const data = await res.json().catch(() => ({}))
      if (res.ok) {
        alert('Contraseña restablecida. El usuario deberá cambiarla al entrar.')
        loadUsuarios()
        loadAuditLogs()
      } else {
        alert(data.detail || 'No fue posible restablecer la contraseña')
      }
    } catch (error) {
      console.error(error)
      alert('Error de conexión')
    }
  }

  const grupos = agrupadosPorRol()
  const resumen = {
    total: empleados.length,
    activos: empleados.filter(e => e.status !== 'inactivo').length,
    credenciales: usuarios.length,
    soportes: empleados.filter(e => e.rol === 'soporte').length
  }
  const soporteMode = currentRole === 'soporte'

  return (
    <div style={{ display: 'grid', gap: 20, padding: 20 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 16 }}>
        {[
          ['Personal total', resumen.total, '#0f172a'],
          ['Activos', resumen.activos, '#0f766e'],
          ['Credenciales', resumen.credenciales, '#7c3aed'],
          ['Soporte', resumen.soportes, '#c2410c']
        ].map(([label, value, color]) => (
          <div key={label} style={{ background: 'white', padding: 18, borderRadius: 16, boxShadow: '0 12px 30px rgba(15,23,42,0.06)' }}>
            <div style={{ fontSize: 13, color: '#64748b', marginBottom: 8 }}>{label}</div>
            <div style={{ fontSize: 30, fontWeight: 700, color }}>{value}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: soporteMode ? '1.15fr 0.85fr' : '1fr', gap: 20 }}>
        <div style={{ display: 'grid', gap: 20 }}>
          <div style={{ background: 'white', borderRadius: 18, padding: 22, boxShadow: '0 12px 30px rgba(15,23,42,0.06)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <div>
                <h2 style={{ margin: 0, color: '#0f172a' }}>Gestión de empleados</h2>
                <p style={{ margin: '6px 0 0 0', color: '#64748b' }}>Altas, bajas, modificaciones y control operativo del personal.</p>
              </div>
            </div>

            <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <input required placeholder="Nombre completo" value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} style={fieldStyle} />
              <select value={form.rol} onChange={e => setForm({ ...form, rol: e.target.value })} style={fieldStyle}>
                <option value="empleado">Empleado</option>
                <option value="dueno">Dueño</option>
                <option value="soporte">Soporte</option>
              </select>
              <input placeholder="Horario" value={form.horario} onChange={e => setForm({ ...form, horario: e.target.value })} style={fieldStyle} />
              <input placeholder="Contacto" value={form.contacto} onChange={e => setForm({ ...form, contacto: e.target.value })} style={fieldStyle} />
              <input placeholder="Actividades" value={form.actividades} onChange={e => setForm({ ...form, actividades: e.target.value })} style={fieldStyle} />
              <input placeholder="Nómina / referencia" value={form.nomina_info} onChange={e => setForm({ ...form, nomina_info: e.target.value })} style={fieldStyle} />
              <input placeholder="Salario" type="number" step="0.01" value={form.salario} onChange={e => setForm({ ...form, salario: e.target.value })} style={fieldStyle} />
              <div style={{ display: 'flex', gap: 10 }}>
                <button type="submit" style={primaryButton}>{form.id ? 'Actualizar empleado' : 'Registrar empleado'}</button>
                <button type="button" onClick={resetForm} style={secondaryButton}>Limpiar</button>
              </div>
            </form>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 16 }}>
            {loading ? <div>Cargando...</div> : ['dueno', 'soporte', 'empleado'].map(roleKey => (
              <div key={roleKey} style={{ background: 'white', padding: 18, borderRadius: 18, boxShadow: '0 12px 30px rgba(15,23,42,0.06)' }}>
                <h3 style={{ marginTop: 0, marginBottom: 14, textTransform: 'capitalize', color: '#0f172a' }}>{roleKey}</h3>
                {(grupos[roleKey] || []).length === 0 && <div style={{ color: '#94a3b8' }}>Sin registros</div>}
                {(grupos[roleKey] || []).map(emp => (
                  <div key={emp.id} style={{ border: '1px solid #e2e8f0', borderRadius: 14, padding: 14, marginBottom: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10 }}>
                      <strong style={{ color: '#0f172a' }}>{emp.nombre}</strong>
                      <span style={{ fontSize: 12, color: emp.status === 'inactivo' ? '#dc2626' : '#0f766e' }}>{emp.status || 'activo'}</span>
                    </div>
                    <div style={metaStyle}>Horario: {emp.horario || 'No definido'}</div>
                    <div style={metaStyle}>Contacto: {emp.contacto || 'No definido'}</div>
                    <div style={metaStyle}>Salario: {emp.salario ? `$${emp.salario}` : 'No definido'}</div>
                    <div style={{ ...metaStyle, marginTop: 6 }}>{emp.actividades || 'Sin actividades capturadas'}</div>
                    <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 10 }}>
                      <button onClick={() => startEdit(emp)} style={miniButton}>Editar</button>
                      {soporteMode && <button onClick={() => prepararCredenciales(emp)} style={miniButton}>Preparar acceso</button>}
                      <button onClick={() => handleDelete(emp.id)} style={dangerGhostButton}>Inactivar</button>
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        {soporteMode && (
          <div style={{ display: 'grid', gap: 20 }}>
            <div style={{ background: 'white', borderRadius: 18, padding: 22, boxShadow: '0 12px 30px rgba(15,23,42,0.06)' }}>
              <h3 style={{ marginTop: 0, color: '#0f172a' }}>Administración de credenciales</h3>
              <p style={{ color: '#64748b', fontSize: 14 }}>Seguridad activa: solo soporte puede ver usuarios, las contraseñas nunca se muestran, se exige reconfirmación para acciones críticas y los usuarios nuevos deberán cambiar su contraseña en el primer acceso.</p>

              <form onSubmit={crearCredenciales} style={{ display: 'grid', gap: 12, marginTop: 14 }}>
                <select value={credentialForm.empleado_id} onChange={e => setCredentialForm({ ...credentialForm, empleado_id: e.target.value })} style={fieldStyle}>
                  <option value="">Selecciona empleado</option>
                  {empleados.filter(emp => emp.status !== 'inactivo').map(emp => (
                    <option key={emp.id} value={emp.id}>{emp.nombre} · {emp.rol}</option>
                  ))}
                </select>
                <input placeholder="Nombre de usuario" value={credentialForm.username} onChange={e => setCredentialForm({ ...credentialForm, username: e.target.value })} style={fieldStyle} />
                <input type="password" placeholder="Contraseña inicial robusta" value={credentialForm.password} onChange={e => setCredentialForm({ ...credentialForm, password: e.target.value })} style={fieldStyle} />
                <button type="submit" style={primaryButton}>Crear credencial</button>
              </form>
            </div>

            <div style={{ background: 'white', borderRadius: 18, padding: 22, boxShadow: '0 12px 30px rgba(15,23,42,0.06)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
                <h3 style={{ margin: 0, color: '#0f172a' }}>Credenciales registradas</h3>
                <button onClick={loadUsuarios} style={secondaryButton}>Actualizar</button>
              </div>

              {loadingUsuarios ? <div>Cargando credenciales...</div> : (
                <div style={{ display: 'grid', gap: 12 }}>
                  {usuarios.length === 0 && <div style={{ color: '#94a3b8' }}>No hay credenciales registradas.</div>}
                  {usuarios.map(usuario => (
                    <div key={usuario.id} style={{ border: '1px solid #e2e8f0', borderRadius: 14, padding: 14 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'center' }}>
                        <div>
                          <div style={{ fontWeight: 700, color: '#0f172a' }}>{usuario.username}</div>
                          <div style={metaStyle}>Rol: {usuario.rol || 'sin rol'} · Empleado: {usuario.empleado_nombre || 'sin vínculo'}</div>
                          <div style={metaStyle}>Estado: {usuario.status || 'activo'} · Cambio forzoso: {usuario.must_change_password ? 'sí' : 'no'}</div>
                          <div style={metaStyle}>Último acceso: {usuario.last_login_at || 'sin acceso'} · Fallos: {usuario.failed_login_attempts || 0}</div>
                        </div>
                        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                          <button onClick={() => cambiarEstadoUsuario(usuario)} style={miniButton}>Estado</button>
                          <button onClick={() => resetearPasswordUsuario(usuario)} style={miniButton}>Reset password</button>
                          <button onClick={() => eliminarUsuario(usuario)} style={dangerGhostButton}>Eliminar</button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div style={{ background: 'white', borderRadius: 18, padding: 22, boxShadow: '0 12px 30px rgba(15,23,42,0.06)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
                <h3 style={{ margin: 0, color: '#0f172a' }}>Bitácora de auditoría</h3>
                <button onClick={loadAuditLogs} style={secondaryButton}>Actualizar</button>
              </div>
              {loadingAudit ? <div>Cargando bitácora...</div> : (
                <div style={{ display: 'grid', gap: 10, maxHeight: 320, overflowY: 'auto' }}>
                  {auditLogs.length === 0 && <div style={{ color: '#94a3b8' }}>Sin eventos registrados.</div>}
                  {auditLogs.map(log => (
                    <div key={log.id} style={{ border: '1px solid #e2e8f0', borderRadius: 12, padding: 12 }}>
                      <div style={{ fontWeight: 700, color: '#0f172a' }}>{log.action}</div>
                      <div style={metaStyle}>Actor: {log.actor_username} · Objetivo: {log.target_label || log.target_type}</div>
                      <div style={metaStyle}>Fecha: {log.created_at || 'sin fecha'} · IP: {log.source_ip || 'n/a'}</div>
                      {log.details && <div style={{ ...metaStyle, marginTop: 4 }}>{log.details}</div>}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

const fieldStyle = {
  width: '100%',
  padding: '12px 14px',
  borderRadius: 12,
  border: '1px solid #cbd5e1',
  fontSize: 14,
  outline: 'none',
  boxSizing: 'border-box'
}

const primaryButton = {
  background: '#0f172a',
  color: 'white',
  border: 'none',
  borderRadius: 12,
  padding: '12px 14px',
  fontWeight: 600,
  cursor: 'pointer'
}

const secondaryButton = {
  background: '#f8fafc',
  color: '#334155',
  border: '1px solid #cbd5e1',
  borderRadius: 12,
  padding: '12px 14px',
  fontWeight: 600,
  cursor: 'pointer'
}

const miniButton = {
  background: '#e2e8f0',
  color: '#0f172a',
  border: 'none',
  borderRadius: 10,
  padding: '8px 10px',
  fontSize: 12,
  fontWeight: 600,
  cursor: 'pointer'
}

const dangerGhostButton = {
  background: '#fff1f2',
  color: '#be123c',
  border: '1px solid #fecdd3',
  borderRadius: 10,
  padding: '8px 10px',
  fontSize: 12,
  fontWeight: 600,
  cursor: 'pointer'
}

const metaStyle = {
  fontSize: 13,
  color: '#64748b'
}