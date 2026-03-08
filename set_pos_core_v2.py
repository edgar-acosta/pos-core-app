import os

def crear_archivo(ruta, contenido):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido.strip())
    print(f"✅ Creado: {ruta}")

def generar_proyecto_core():
    print("🚀 Reconstruyendo el POS Core completo...\n")
    
    # ==========================================
    # 1. ESTRUCTURA DE CARPETAS BASE
    # ==========================================
    carpetas = ["backend", "frontend/src/components", "frontend/src/pages", "plugins"]
    for c in carpetas:
        os.makedirs(c, exist_ok=True)

    # ==========================================
    # 2. BACKEND (FastAPI Core)
    # ==========================================
    crear_archivo("backend/requirements.txt", """
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
python-multipart==0.0.6
pydantic==2.4.2
""")

    crear_archivo("backend/database.py", """
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///core.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    rol = Column(String)

Base.metadata.create_all(bind=engine)
""")

    crear_archivo("backend/main.py", """
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os, json, sys, importlib

app = FastAPI(title="MyPOS Core API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PLUGIN_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins")
if not os.path.exists(PLUGIN_DIR):
    os.makedirs(PLUGIN_DIR)

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
for plugin in os.listdir(PLUGIN_DIR):
    plugin_path = os.path.join(PLUGIN_DIR, plugin)
    if os.path.isdir(plugin_path):
        uploads_dir = os.path.join(plugin_path, "uploads")
        if os.path.exists(uploads_dir):
            app.mount(f"/p/{plugin}/uploads", StaticFiles(directory=uploads_dir), name=f"{plugin}_uploads")
        
        router_module = f"plugins.{plugin}.backend.router"
        try:
            modulo = importlib.import_module(router_module)
            app.include_router(modulo.router, prefix=f"/p/{plugin}")
            print(f"🔌 Plugin cargado exitosamente: {plugin}")
        except Exception as e:
            print(f"⚠️ No se pudo cargar el plugin {plugin}: {e}")

@app.post("/auth/login")
async def login(data: dict):
    if data.get("username") == "admin" and data.get("password") == "admin":
        return {"token": "fake-jwt-token-root", "rol": "soporte"}
    raise HTTPException(status_code=401, detail="Credenciales incorrectas")

@app.get("/config/ui")
async def get_ui_config():
    plugins_activos = []
    for plugin in os.listdir(PLUGIN_DIR):
        manifest_path = os.path.join(PLUGIN_DIR, plugin, "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                plugins_activos.append(json.load(f))

    return {
        "nombre": "Soporte Técnico",
        "rol": "SOPORTE",
        "plugins": plugins_activos
    }
""")

    # ==========================================
    # 3. FRONTEND CONFIG
    # ==========================================
    crear_archivo("frontend/package.json", """
{
  "name": "pos-core",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": { "dev": "vite", "build": "vite build", "preview": "vite preview" },
  "dependencies": { "react": "^18.2.0", "react-dom": "^18.2.0" },
  "devDependencies": { "@vitejs/plugin-react": "^4.2.1", "vite": "^5.0.8" }
}
""")

    crear_archivo("frontend/vite.config.js", """
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({ plugins: [react()] })
""")

    crear_archivo("frontend/index.html", """
<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>MyPOS Core</title>
    <style>body { margin: 0; padding: 0; box-sizing: border-box; background: #f1f5f9; }</style>
  </head>
  <body><div id="root"></div><script type="module" src="/src/main.jsx"></script></body>
</html>
""")

    crear_archivo("frontend/src/main.jsx", """
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
ReactDOM.createRoot(document.getElementById('root')).render(<React.StrictMode><App /></React.StrictMode>)
""")

    # ==========================================
    # 4. COMPONENTES Y MÓDULOS CORE (Nuevos diseños funcionales)
    # ==========================================
    crear_archivo("frontend/src/components/Sidebar.jsx", """
import React from 'react';
export default function Sidebar({ ui, tabActual, setTabActual, logout, sidebarColor }) {
  return (
    <aside style={{ width: '260px', background: sidebarColor, color: 'white', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '25px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
        <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>🏪 MyPOS</h2>
        <p style={{ fontSize: '0.8rem', color: '#94a3b8', margin: '5px 0 0 0' }}>root ({ui?.rol})</p>
      </div>
      <nav style={{ padding: '20px 0', flex: 1 }}>
        {['Registrar Venta', 'Inventarios', 'Empleados', 'Reportes', 'Mantenimiento'].map(item => (
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
""")

    crear_archivo("frontend/src/pages/Login.jsx", """
import React, { useState } from 'react';
export default function Login({ setToken }) {
  const [u, setU] = useState(''); const [p, setP] = useState('');
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('http://127.0.0.1:8000/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: u, password: p }) });
      if (res.ok) { const data = await res.json(); localStorage.setItem('token', data.token); setToken(data.token); } 
      else { alert('Credenciales incorrectas (Usa admin / admin)'); }
    } catch (e) { alert('Error conectando al backend'); }
  };
  return (
    <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0f172a' }}>
      <form onSubmit={handleLogin} style={{ background: 'white', padding: '40px', borderRadius: '20px', width: '320px', textAlign: 'center', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)' }}>
        <h2 style={{marginTop:0, color: '#1e293b'}}>Iniciar Sesión</h2>
        <input placeholder="Usuario (admin)" value={u} onChange={e=>setU(e.target.value)} style={{ width: '100%', padding: '12px', marginBottom: '15px', boxSizing: 'border-box', borderRadius: '8px', border: '1px solid #cbd5e1' }}/>
        <input type="password" placeholder="Contraseña (admin)" value={p} onChange={e=>setP(e.target.value)} style={{ width: '100%', padding: '12px', marginBottom: '20px', boxSizing: 'border-box', borderRadius: '8px', border: '1px solid #cbd5e1' }}/>
        <button style={{ width: '100%', padding: '14px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer' }}>Entrar al Sistema</button>
      </form>
    </div>
  );
}
""")

    # --- PANTALLAS CORE ---
    crear_archivo("frontend/src/pages/RegistrarVenta.jsx", r"""
import React from 'react';
export default function RegistrarVenta() {
  return (
    <div style={{ background: 'white', padding: '30px', borderRadius: '20px', boxShadow: '0 10px 25px rgba(0,0,0,0.05)', height: '70vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ fontSize: '4rem', marginBottom: '15px' }}>🛒</div>
      <h2 style={{ color: '#1e293b', marginTop: 0 }}>Terminal de Ventas</h2>
      <p style={{ color: '#64748b', textAlign: 'center', maxWidth: '400px' }}>Aquí podrás escanear productos y generar los tickets de compra para los clientes.</p>
    </div>
  );
}
""")

    crear_archivo("frontend/src/pages/Inventarios.jsx", r"""
import React from 'react';
export default function Inventarios() {
  return (
    <div style={{ background: 'white', padding: '30px', borderRadius: '20px', boxShadow: '0 10px 25px rgba(0,0,0,0.05)', height: '70vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ fontSize: '4rem', marginBottom: '15px' }}>📋</div>
      <h2 style={{ color: '#1e293b', marginTop: 0 }}>Inventario General Core</h2>
      <p style={{ color: '#64748b', textAlign: 'center', maxWidth: '400px' }}>Catálogo maestro de productos para venta en mostrador.</p>
    </div>
  );
}
""")

    crear_archivo("frontend/src/pages/Empleados.jsx", r"""
import React from 'react';
export default function Empleados() {
  return (
    <div style={{ background: 'white', padding: '30px', borderRadius: '20px', boxShadow: '0 10px 25px rgba(0,0,0,0.05)', height: '70vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ fontSize: '4rem', marginBottom: '15px' }}>👥</div>
      <h2 style={{ color: '#1e293b', marginTop: 0 }}>Gestión de Personal</h2>
      <p style={{ color: '#64748b', textAlign: 'center', maxWidth: '400px' }}>Administra roles, accesos y nóminas de tus empleados.</p>
    </div>
  );
}
""")

    crear_archivo("frontend/src/pages/Reportes.jsx", r"""
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
""")

    crear_archivo("frontend/src/pages/Mantenimiento.jsx", r"""
import React from 'react';
export default function Mantenimiento() {
  return (
    <div style={{ background: 'white', padding: '30px', borderRadius: '20px', boxShadow: '0 10px 25px rgba(0,0,0,0.05)', height: '70vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ fontSize: '4rem', marginBottom: '15px' }}>⚙️</div>
      <h2 style={{ color: '#1e293b', marginTop: 0 }}>Configuraciones del Sistema</h2>
      <p style={{ color: '#64748b', textAlign: 'center', maxWidth: '400px' }}>Ajustes globales, bases de datos y control de plugins.</p>
    </div>
  );
}
""")

    # ==========================================
    # 5. APP.JSX (V15 - MOTOR COMPLETO)
    # ==========================================
    app_jsx_content = r"""
import { useState, useEffect, useCallback, useRef } from 'react'
import Login from './pages/Login'
import Sidebar from './components/Sidebar'
import RegistrarVenta from './pages/RegistrarVenta'
import Inventarios from './pages/Inventarios'
import Empleados from './pages/Empleados'
import Reportes from './pages/Reportes'
import Mantenimiento from './pages/Mantenimiento'

const IngredientBuilder = ({ insumosDisponibles, value, onChange }) => {
  const [lineas, setLineas] = useState(() => {
    try { return value ? JSON.parse(value) : [{ insumoId: '', cantidad: '', unidad: '' }]; } 
    catch (e) { return [{ insumoId: '', cantidad: '', unidad: '' }]; }
  });
  useEffect(() => { if (!value) setLineas([{ insumoId: '', cantidad: '', unidad: '' }]); }, [value]);
  const actualizarLinea = (index, campo, valor) => {
    const nuevas = [...lineas];
    if (campo === 'cantidad' && valor !== '' && Number(valor) <= 0) valor = ''; 
    nuevas[index][campo] = valor; setLineas(nuevas); onChange(JSON.stringify(nuevas)); 
  };
  const agregarLinea = () => setLineas([...lineas, { insumoId: '', cantidad: '', unidad: '' }]);
  const eliminarLinea = (index) => {
    if (lineas.length === 1) return;
    const nuevas = lineas.filter((_, i) => i !== index); setLineas(nuevas); onChange(JSON.stringify(nuevas));
  };
  return (
    <div style={{ background: '#fff', padding: '15px', borderRadius: '10px', border: '1px solid #e2e8f0', marginTop: '10px' }}>
      <p style={{ fontSize: '0.7rem', fontWeight: 'bold', color: '#64748b', marginBottom: '10px', textTransform: 'uppercase' }}>Composición de la Receta</p>
      {lineas.map((linea, i) => (
        <div key={i} style={{ display: 'flex', gap: '8px', marginBottom: '8px', alignItems: 'center' }}>
          <select style={{ flex: 2, padding: '8px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '0.8rem' }} value={linea.insumoId} onChange={(e) => actualizarLinea(i, 'insumoId', e.target.value)}>
            <option value="">Seleccionar Insumo...</option>
            {insumosDisponibles.map(ins => <option key={ins.ID} value={ins.ID}>{ins.Insumo} ({ins.Unidad})</option>)}
          </select>
          <input type="number" step="any" min="0.01" placeholder="Cant." style={{ width: '70px', padding: '8px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '0.8rem' }} value={linea.cantidad} onChange={(e) => actualizarLinea(i, 'cantidad', e.target.value)} />
          <select style={{ width: '85px', padding: '8px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '0.8rem' }} value={linea.unidad} onChange={(e) => actualizarLinea(i, 'unidad', e.target.value)}>
            <option value="">Unidad...</option><option value="kg">kg</option><option value="gr">gr</option><option value="lt">lt</option><option value="ml">ml</option><option value="pza">pza</option><option value="cda">cda</option><option value="cdita">cdita</option>
          </select>
          <button onClick={() => eliminarLinea(i)} style={{ background: '#fee2e2', color: '#ef4444', border: 'none', borderRadius: '5px', padding: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>✕</button>
        </div>
      ))}
      <button onClick={agregarLinea} style={{ width: '100%', marginTop: '5px', padding: '10px', background: '#f8fafc', border: '1px dashed #cbd5e1', color: '#475569', borderRadius: '6px', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 'bold' }}>+ Añadir Ingrediente</button>
    </div>
  );
};

const VisualSelect = ({ endpoint, value, onChange, token }) => {
  const [opciones, setOpciones] = useState([]); const [isOpen, setIsOpen] = useState(false);
  useEffect(() => {
    fetch(`http://127.0.0.1:8000${endpoint}`, { headers: { 'Authorization': `Bearer ${token}` } })
    .then(res => res.json()).then(data => setOpciones(data)).catch(e => console.error(e));
  }, [endpoint, token]);
  const seleccionado = opciones.find(o => String(o.ID) === String(value));
  const renderFotoUrl = (ruta) => {
    if (!ruta || ruta === 'IMAGE:') return 'https://via.placeholder.com/100?text=Pan';
    return `http://127.0.0.1:8000/p/panaderia_pro/${ruta.replace('IMAGE:', '')}`;
  };
  return (
    <div style={{ position: 'relative', marginTop: '5px' }}>
      <div onClick={() => setIsOpen(!isOpen)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid #cbd5e1', background: 'white', display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}>
        {seleccionado ? (
          <><img src={renderFotoUrl(seleccionado.Foto)} style={{ width: '30px', height: '30px', borderRadius: '50%', objectFit: 'cover' }} alt="pan" /><span style={{ fontWeight: 'bold', fontSize: '0.85rem', color: '#334155' }}>{seleccionado.Nombre}</span></>
        ) : <span style={{ fontSize: '0.85rem', color: '#64748b' }}>Seleccionar del Catálogo...</span>}
        <span style={{ marginLeft: 'auto', fontSize: '0.8rem', color: '#94a3b8' }}>{isOpen ? '▲' : '▼'}</span>
      </div>
      {isOpen && (
        <div style={{ position: 'absolute', top: '100%', left: 0, right: 0, background: 'white', border: '1px solid #cbd5e1', borderRadius: '8px', zIndex: 50, maxHeight: '200px', overflowY: 'auto', marginTop: '5px', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}>
          {opciones.length === 0 ? <div style={{ padding: '15px', textAlign: 'center', fontSize: '0.8rem', color: '#94a3b8' }}>No hay elementos.</div> : opciones.map(op => (
            <div key={op.ID} onClick={() => { onChange(op.ID); setIsOpen(false); }} style={{ padding: '10px', display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', borderBottom: '1px solid #f1f5f9' }}>
              <img src={renderFotoUrl(op.Foto)} style={{ width: '35px', height: '35px', borderRadius: '8px', objectFit: 'cover' }} alt="pan" />
              <span style={{ fontSize: '0.85rem', fontWeight: '500', color: '#334155' }}>{op.Nombre}</span>
            </div>
          ))}
        </div>
      )}
      {seleccionado && (
        <div style={{ marginTop: '15px', textAlign: 'center', background: '#f8fafc', padding: '10px', borderRadius: '10px', border: '1px dashed #cbd5e1' }}>
          <img src={renderFotoUrl(seleccionado.Foto)} style={{ width: '100%', height: '140px', objectFit: 'cover', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }} alt="preview" />
        </div>
      )}
    </div>
  );
};

const PantallaAutomatica = ({ config, color, onBack, token }) => {
  const [formData, setFormData] = useState({}); const [tablaData, setTablaData] = useState([]);
  const [insumosParaCarga, setInsumosParaCarga] = useState([]); 
  const [loading, setLoading] = useState(false); const [modalDetalle, setModalDetalle] = useState(null); 
  const [resetKey, setResetKey] = useState(0); const csvInputRef = useRef(null);
  const [alerta, setAlerta] = useState(null); const [confirmacionBorrado, setConfirmacionBorrado] = useState(null);

  const mostrarAlerta = (mensaje, tipo = 'error') => { setAlerta({ mensaje, tipo }); setTimeout(() => setAlerta(null), 3500); };

  const renderCelda = (valor) => {
    if (typeof valor === 'string' && valor.startsWith('IMAGE:') && valor !== 'IMAGE:') {
      const filename = valor.replace('IMAGE:', '');
      return <img src={`http://127.0.0.1:8000/p/panaderia_pro/${filename}`} style={{ width: '60px', height: '60px', borderRadius: '10px', objectFit: 'cover', border: '1px solid #eee' }} alt="Preview" onError={(e) => e.target.src = 'https://via.placeholder.com/60'} />;
    }
    if (valor === 'IMAGE:') return <span style={{fontSize: '0.8rem', color: '#94a3b8', background: '#f1f5f9', padding: '5px 10px', borderRadius: '20px'}}>Sin foto</span>;
    return valor;
  };

  const cargarDatos = useCallback(async () => {
    try {
      const res = await fetch(`http://127.0.0.1:8000${config.tabla.endpoint_data}`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) setTablaData(await res.json());
    } catch (e) { console.error(e); }
  }, [config.tabla.endpoint_data, token]);

  useEffect(() => { 
    cargarDatos();
    if (config.formulario.some(c => c.tipo === 'ingredient_builder')) {
      fetch(`http://127.0.0.1:8000/p/panaderia_pro/insumos`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json()).then(data => setInsumosParaCarga(data)).catch(e => console.error(e));
    }
  }, [cargarDatos, config, token]);

  const ejecutarGuardado = async () => {
    for (let c of config.formulario) {
      const valor = formData[c.name];
      if (c.tipo === 'text' && (!valor || String(valor).trim() === '')) return mostrarAlerta(`El campo "${c.label}" es obligatorio.`, "error");
      if (c.tipo === 'select' && (!valor || String(valor).trim() === '')) return mostrarAlerta(`Selecciona una opción en "${c.label}".`, "error");
      if (c.tipo === 'file' && !valor) return mostrarAlerta(`Es obligatorio subir una imagen.`, "error");
      if (c.tipo === 'number') {
        if (valor === undefined || valor === '') return mostrarAlerta(`El campo "${c.label}" no puede estar vacío.`, "error");
        if (Number(valor) < 0) return mostrarAlerta(`No uses números negativos.`, "error");
        if (c.name === 'rendimiento' && (Number(valor) <= 0 || Number(valor) > 10000)) return mostrarAlerta("El rendimiento debe ser entre 1 y 10,000.", "error");
      }
      if (c.tipo === 'visual_select' && !valor) return mostrarAlerta("Debes seleccionar un producto del catálogo.", "error");
    }

    const tieneIngredientes = config.formulario.find(c => c.tipo === 'ingredient_builder');
    if (tieneIngredientes) {
      if (!formData[tieneIngredientes.name]) return mostrarAlerta("Agrega al menos un ingrediente.", "error");
      try {
        const ingArray = JSON.parse(formData[tieneIngredientes.name]);
        if (ingArray.length === 0) return mostrarAlerta("La receta no puede estar vacía.", "error");
        for (let i = 0; i < ingArray.length; i++) {
          if (!ingArray[i].insumoId || !ingArray[i].cantidad || !ingArray[i].unidad) return mostrarAlerta(`Fila ${i + 1} incompleta.`, "error");
        }
      } catch (e) { return mostrarAlerta("Error leyendo ingredientes.", "error"); }
    }

    setLoading(true);
    try {
      const manejaArchivos = config.formulario.some(c => c.tipo === 'file');
      let opcionesFetch = { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } };
      if (manejaArchivos) {
        const data = new FormData(); Object.keys(formData).forEach(key => data.append(key, formData[key])); opcionesFetch.body = data; 
      } else {
        opcionesFetch.headers['Content-Type'] = 'application/json'; opcionesFetch.body = JSON.stringify(formData);
      }
      const res = await fetch(`http://127.0.0.1:8000${config.tabla.endpoint_data}`, opcionesFetch);
      if (res.ok) { 
        mostrarAlerta("Registrado correctamente.", "exito"); setFormData({}); setResetKey(prev => prev + 1); cargarDatos(); 
      } else {
        const err = await res.json().catch(()=>({})); mostrarAlerta(err.detail || "Error en servidor", "error");
      }
    } catch (e) { mostrarAlerta("Error de conexión.", "error"); } finally { setLoading(false); }
  };

  const confirmarBorradoDefinitivo = async () => {
    if (!confirmacionBorrado) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000${config.tabla.endpoint_data}/${confirmacionBorrado}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) { mostrarAlerta("Registro eliminado.", "exito"); cargarDatos(); }
    } catch (e) { mostrarAlerta("Error al eliminar.", "error"); } finally { setConfirmacionBorrado(null); }
  };

  const handleCSVUpload = async (event) => {
    const file = event.target.files[0]; if (!file) return; setLoading(true);
    const formDataCSV = new FormData(); formDataCSV.append("archivo", file);
    try {
      const res = await fetch(`http://127.0.0.1:8000${config.csv_import}`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` }, body: formDataCSV });
      if (res.ok) { mostrarAlerta("CSV procesado.", "exito"); cargarDatos(); } else { mostrarAlerta("Error de formato CSV.", "error"); }
    } catch(e) { mostrarAlerta("Error de subida.", "error"); } finally { setLoading(false); event.target.value = null; }
  };

  return (
    <div style={{ background: 'white', padding: '30px', borderRadius: '20px', boxShadow: '0 10px 25px rgba(0,0,0,0.05)', position: 'relative' }}>
      
      {alerta && (
        <div style={{ position: 'fixed', top: '30px', right: '30px', background: 'white', borderLeft: `6px solid ${alerta.tipo === 'exito' ? '#10b981' : '#ef4444'}`, padding: '16px 24px', borderRadius: '10px', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)', zIndex: 10000, display: 'flex', alignItems: 'center', gap: '15px' }}>
          <span style={{ fontSize: '1.5rem' }}>{alerta.tipo === 'exito' ? '✅' : '⚠️'}</span><span style={{ color: '#1e293b', fontWeight: '600', fontSize: '0.95rem' }}>{alerta.mensaje}</span>
        </div>
      )}

      {confirmacionBorrado && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(15, 23, 42, 0.65)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 10000, backdropFilter: 'blur(3px)' }}>
          <div style={{ background: 'white', padding: '35px', borderRadius: '20px', width: '380px', textAlign: 'center', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)' }}>
            <div style={{ fontSize: '3.5rem', marginBottom: '10px' }}>🗑️</div>
            <h3 style={{ margin: '0 0 10px 0', color: '#1e293b', fontSize: '1.4rem' }}>¿Eliminar Registro?</h3>
            <div style={{ display: 'flex', gap: '15px' }}>
              <button onClick={() => setConfirmacionBorrado(null)} style={{ flex: 1, padding: '12px', background: '#f1f5f9', color: '#475569', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 'bold' }}>Cancelar</button>
              <button onClick={confirmarBorradoDefinitivo} style={{ flex: 1, padding: '12px', background: '#ef4444', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 'bold' }}>Eliminar</button>
            </div>
          </div>
        </div>
      )}

      <button onClick={onBack} style={{ marginBottom: '20px', cursor: 'pointer', color: color, background: 'none', border: `1px solid ${color}`, padding: '8px 15px', borderRadius: '8px', fontWeight: 'bold' }}>⬅ Volver al Menú</button>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 400px', gap: '30px' }}>
        <div style={{ border: '1px solid #f1f5f9', padding: '20px', borderRadius: '15px', overflowX: 'auto' }}>
          <h3>📋 {config.titulo}</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
            <thead>
              <tr style={{ borderBottom: `2px solid ${color}44`, textAlign: 'left' }}>
                {config.tabla.headers.map(h => <th key={h} style={{padding: '12px'}}>{h}</th>)}
                <th style={{padding: '12px', textAlign: 'center'}}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {tablaData.map((f, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #f9f9f9' }}>
                  {config.tabla.headers.map((header, j) => <td key={j} style={{padding: '12px'}}>{renderCelda(f[header])}</td>)}
                  <td style={{ minWidth: '150px' }}>
                    <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                      {f._raw_ingredientes && <button onClick={() => setModalDetalle(f)} style={{ flex: 1, background: '#e0f2fe', color: '#0ea5e9', border: 'none', padding: '8px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}>👁️ Ver</button>}
                      <button onClick={() => setConfirmacionBorrado(f.ID)} style={{ flex: 1, background: '#fee2e2', color: '#ef4444', border: 'none', padding: '8px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}>🗑️ Borrar</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div style={{ background: '#f8fafc', padding: '25px', borderRadius: '15px', height: 'fit-content' }}>
          <h3 style={{ marginTop: 0 }}>➕ Nuevo Registro</h3>
          {config.formulario.map(c => (
            <div key={c.name} style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 'bold', marginBottom: '5px', color: '#475569' }}>{c.label}</label>
              {c.tipo === 'visual_select' ? <VisualSelect endpoint={c.endpoint} value={formData[c.name]} onChange={(val) => setFormData({...formData, [c.name]: val})} token={token} /> : 
               c.tipo === 'ingredient_builder' ? <IngredientBuilder insumosDisponibles={insumosParaCarga} value={formData[c.name]} onChange={(val) => setFormData({...formData, [c.name]: val})} /> : 
               c.tipo === 'file' ? <input key={resetKey} type="file" accept="image/*" onChange={(e) => setFormData({...formData, [c.name]: e.target.files[0]})} style={{ width: '100%', padding: '8px', background: 'white', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.8rem' }} /> : 
               c.tipo === 'textarea' ? <textarea value={formData[c.name] || ''} onChange={(e) => setFormData({...formData, [c.name]: e.target.value})} style={{ width: '100%', height: '80px', borderRadius: '8px', border: '1px solid #cbd5e1', padding: '10px' }} /> : 
               c.tipo === 'select' ? <select value={formData[c.name] || ''} onChange={(e) => setFormData({...formData, [c.name]: e.target.value})} style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #cbd5e1' }}><option value="">Seleccione...</option>{c.options?.map(opt => <option key={opt} value={opt}>{opt}</option>)}</select> : 
               <input type={c.tipo} max={c.name === 'rendimiento' ? "10000" : undefined} min={c.tipo === 'number' ? "0" : undefined} value={formData[c.name] || ''} onChange={(e) => setFormData({...formData, [c.name]: e.target.value})} style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #cbd5e1' }} />
              }
            </div>
          ))}
          <button onClick={ejecutarGuardado} disabled={loading} style={{ width: '100%', background: color, color: 'white', padding: '14px', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 'bold', marginTop: '10px' }}>{loading ? 'Procesando...' : 'Guardar en el Módulo'}</button>
          {config.csv_import && (
            <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px dashed #cbd5e1', textAlign: 'center' }}>
              <p style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '10px', fontWeight: 'bold' }}>Carga Masiva</p>
              <input type="file" accept=".csv" ref={csvInputRef} onChange={handleCSVUpload} style={{ display: 'none' }} />
              <button onClick={() => csvInputRef.current.click()} disabled={loading} style={{ width: '100%', background: '#f1f5f9', color: '#475569', padding: '10px', border: '1px solid #cbd5e1', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}>📁 Importar desde CSV</button>
            </div>
          )}
        </div>
      </div>
      
      {modalDetalle && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(15, 23, 42, 0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, backdropFilter: 'blur(3px)' }}>
          <div style={{ background: 'white', padding: '30px', borderRadius: '20px', width: '600px', maxWidth: '90%', maxHeight: '90vh', overflowY: 'auto', position: 'relative', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)' }}>
            <button onClick={() => setModalDetalle(null)} style={{ position: 'absolute', top: '15px', right: '15px', background: '#f1f5f9', border: 'none', borderRadius: '50%', width: '35px', height: '35px', fontSize: '1.2rem', cursor: 'pointer' }}>✕</button>
            <h2 style={{ marginTop: 0, color: color, fontSize: '1.8rem' }}>{modalDetalle.Pan}</h2>
            <div style={{ display: 'flex', gap: '30px', marginTop: '20px', flexWrap: 'wrap' }}>
              <div style={{ flex: '1 1 200px' }}>
                 <img src={`http://127.0.0.1:8000/p/panaderia_pro/${modalDetalle.Foto.replace('IMAGE:', '')}`} style={{ width: '100%', borderRadius: '15px', objectFit: 'cover' }} alt="pan"/>
                 <div style={{ background: '#f8fafc', padding: '15px', borderRadius: '10px', marginTop: '15px', textAlign: 'center', border: '1px dashed #cbd5e1' }}><p style={{ margin: 0, fontSize: '0.8rem', fontWeight: 'bold' }}>Rendimiento</p><p style={{ margin: '5px 0 0 0', fontSize: '1.5rem', fontWeight: 'bold' }}>{modalDetalle.Rendimiento}</p></div>
              </div>
              <div style={{ flex: '1 1 250px' }}>
                <h4 style={{ marginTop: 0, color: '#475569' }}>Composición Exacta:</h4>
                <ul style={{ paddingLeft: '0', margin: 0, listStyle: 'none' }}>
                  {modalDetalle._raw_ingredientes?.map((ing, idx) => (
                    <li key={idx} style={{ marginBottom: '10px', paddingBottom: '10px', borderBottom: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between' }}>
                      <span>🥖 {insumosParaCarga.find(i => String(i.ID) === String(ing.insumoId))?.Insumo || 'Eliminado'}</span>
                      <span style={{ background: '#e0f2fe', color: '#0369a1', padding: '3px 8px', borderRadius: '10px', fontWeight: 'bold' }}>{ing.cantidad} {ing.unidad}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const PluginContainer = ({ plugin, token }) => {
  const [subVista, setSubVista] = useState(null); const configUI = plugin.ui || {}; const tema = configUI.color_tema || '#3b82f6';
  if (subVista && configUI.screens?.[subVista]) return <PantallaAutomatica config={configUI.screens[subVista]} color={tema} onBack={() => setSubVista(null)} token={token} />;
  return (
    <div style={{ padding: '20px' }}>
      <h1 style={{ color: tema, textAlign: 'center', marginBottom: '40px', fontSize: '2.5rem' }}>{plugin.label}</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '30px' }}>
        {configUI.screens && Object.entries(configUI.screens).map(([key, screen]) => (
          <button key={key} onClick={() => setSubVista(key)} style={{ padding: '30px', background: 'white', borderRadius: '24px', cursor: 'pointer', border: `1px solid ${tema}22`, boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '4rem', marginBottom: '15px' }}>{screen.icono}</div><h3 style={{ color: tema, margin: '0 0 10px 0' }}>{screen.titulo}</h3><p style={{ margin: 0, color: '#64748b' }}>{screen.descripcion}</p>
          </button>
        ))}
      </div>
    </div>
  );
};

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token')); const [ui, setUi] = useState(null);
  const [tabActual, setTabActual] = useState('Registrar Venta'); const [confirmacionSalida, setConfirmacionSalida] = useState(false);
  useEffect(() => {
    if (token) fetch('http://127.0.0.1:8000/config/ui', { headers: { 'Authorization': `Bearer ${token}` } }).then(res => res.json()).then(data => setUi(data)).catch(() => setConfirmacionSalida(true));
  }, [token]);
  const logout = () => { localStorage.removeItem('token'); setToken(null); setUi(null); setConfirmacionSalida(false); };
  
  if (!token) return <Login setToken={setToken} />;
  if (!ui) return <div style={{ padding: '40px', textAlign: 'center' }}>🔄 Cargando POS Core...</div>;
  
  const renderContenido = () => {
    const pCore = { 'Registrar Venta': <RegistrarVenta />, 'Inventarios': <Inventarios />, 'Empleados': <Empleados />, 'Reportes': <Reportes />, 'Mantenimiento': <Mantenimiento /> };
    if (pCore[tabActual]) return pCore[tabActual];
    const plugin = ui.plugins?.find(p => p.label === tabActual);
    if (plugin) return <PluginContainer plugin={plugin} token={token} />;
    return <div>Seleccione una opción</div>;
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', fontFamily: 'Inter, sans-serif' }}>
      {confirmacionSalida && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(15, 23, 42, 0.65)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 10000 }}>
          <div style={{ background: 'white', padding: '35px', borderRadius: '20px', width: '380px', textAlign: 'center' }}>
            <div style={{ fontSize: '3.5rem', marginBottom: '10px' }}>👋</div><h3 style={{ margin: '0 0 10px 0' }}>¿Cerrar Sesión?</h3>
            <div style={{ display: 'flex', gap: '15px', marginTop: '20px' }}>
              <button onClick={() => setConfirmacionSalida(false)} style={{ flex: 1, padding: '12px', background: '#f1f5f9', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 'bold' }}>Cancelar</button>
              <button onClick={logout} style={{ flex: 1, padding: '12px', background: '#ef4444', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 'bold' }}>Salir</button>
            </div>
          </div>
        </div>
      )}
      <Sidebar ui={ui} tabActual={tabActual} setTabActual={setTabActual} logout={() => setConfirmacionSalida(true)} sidebarColor={ui.plugins?.[0]?.ui?.color_tema || '#1e293b'} />
      <main style={{ flex: 1, padding: '40px', background: '#f1f5f9' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '30px' }}>
          <div><h2 style={{ margin: 0 }}>{ui.nombre}</h2><span style={{ fontSize: '0.7rem', background: '#1e293b', color: 'white', padding: '4px 12px', borderRadius: '20px', fontWeight: 'bold' }}>{ui.rol}</span></div>
          <button onClick={() => setConfirmacionSalida(true)} style={{ background: '#ef4444', color: 'white', border: 'none', borderRadius: '8px', padding: '10px 20px', cursor: 'pointer', fontWeight: 'bold' }}>Cerrar Sesión</button>
        </div>
        <section>{renderContenido()}</section>
      </main>
    </div>
  )
}
"""
    crear_archivo("frontend/src/App.jsx", app_jsx_content)

    print("\n✅ ¡Infraestructura POS Core generada con éxito!")
    print("\n=============================================")
    print(" INSTRUCCIONES:")
    print(" 1. Navega a tu carpeta y levanta el backend.")
    print(" 2. Ejecuta 'npm run dev' en el frontend.")
    print(" 3. Si tienes tu código viejo de RegistrarVenta.jsx, etc., simplemente")
    print("    pégalo encima de los que este script generó para restaurar tus funciones.")
    print("=============================================")

if __name__ == "__main__":
    generar_proyecto_core()
