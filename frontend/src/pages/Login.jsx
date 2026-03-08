import React, { useState } from 'react';
export default function Login({ onLogin }) {
  const [u, setU] = useState(''); const [p, setP] = useState('');
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('http://127.0.0.1:8000/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: u, password: p }) });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('token', data.token);
        localStorage.setItem('must_change_password', data.must_change_password ? '1' : '0');
        localStorage.setItem('session_username', data.username || '');
        onLogin(data);
      } 
      else {
        const err = await res.json().catch(() => ({}));
        alert(err.detail || 'Credenciales incorrectas');
      }
    } catch (e) { alert('Error conectando al backend'); }
  };
  return (
    <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0f172a' }}>
      <form onSubmit={handleLogin} style={{ background: 'white', padding: '40px', borderRadius: '20px', width: '320px', textAlign: 'center', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)' }}>
        <h2 style={{marginTop:0, color: '#1e293b'}}>Iniciar Sesión</h2>
        <input placeholder="Usuario" value={u} onChange={e=>setU(e.target.value)} style={{ width: '100%', padding: '12px', marginBottom: '15px', boxSizing: 'border-box', borderRadius: '8px', border: '1px solid #cbd5e1' }}/>
        <input type="password" placeholder="Contraseña" value={p} onChange={e=>setP(e.target.value)} style={{ width: '100%', padding: '12px', marginBottom: '20px', boxSizing: 'border-box', borderRadius: '8px', border: '1px solid #cbd5e1' }}/>
        <button style={{ width: '100%', padding: '14px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer' }}>Entrar al Sistema</button>
      </form>
    </div>
  );
}