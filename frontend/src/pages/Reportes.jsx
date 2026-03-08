import React from 'react';
export default function Reportes() {
  return (
    <div style={{ background: 'white', padding: '30px', borderRadius: '20px', boxShadow: '0 10px 25px rgba(0,0,0,0.05)', height: '70vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ fontSize: '4rem', marginBottom: '15px' }}>📊</div>
      <h2 style={{ color: '#1e293b', marginTop: 0 }}>Dashboard Financiero</h2>
      <p style={{ color: '#64748b', textAlign: 'center', maxWidth: '400px' }}>Métricas de ventas, cortes de caja y análisis de ingresos.</p>
    </div>
  );
}