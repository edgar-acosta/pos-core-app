import React from 'react';
import { getAllowedModules } from '../utils/permissions';

export default function Sidebar({ ui, tabActual, setTabActual, logout, sidebarColor }) {
  const visible = getAllowedModules(ui);

  return (
    <aside style={{ width: '260px', background: sidebarColor, color: 'white', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '25px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
        <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>🏪 MyPOS</h2>
        <p style={{ fontSize: '0.8rem', color: '#94a3b8', margin: '5px 0 0 0' }}>{ui?.nombre} ({ui?.rol})</p>
      </div>
      <nav style={{ padding: '20px 0', flex: 1 }}>
        {visible.map(item => (
          <button key={item} onClick={() => setTabActual(item)} style={{ width: '100%', padding: '15px 25px', textAlign: 'left', background: tabActual === item ? 'rgba(255,255,255,0.1)' : 'transparent', color: 'white', border: 'none', cursor: 'pointer', fontWeight: tabActual === item ? 'bold' : 'normal', transition: '0.2s' }}>
            {item}
          </button>
        ))}
        {ui?.plugins?.map(p => (
          <button key={p.label} onClick={() => setTabActual(p.label)} style={{ width: '90%', margin: '20px auto', display: 'block', padding: '15px', background: p.ui.color_tema, color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
            {p.label}
          </button>
        ))}
      </nav>
    </aside>
  );
}