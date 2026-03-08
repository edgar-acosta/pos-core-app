from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os, json, sys, importlib

from backend.routers import empleados as empleados_router
from backend.routers import usuarios as usuarios_router
from backend.auth import parse_token
from backend.permissions import get_allowed_modules

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


@app.get("/config/ui")
async def get_ui_config(request: Request):
    plugins_activos = []
    for plugin in os.listdir(PLUGIN_DIR):
        manifest_path = os.path.join(PLUGIN_DIR, plugin, "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                plugins_activos.append(json.load(f))

    # derive role from token if provided
    auth = request.headers.get('authorization', '')
    role = 'dueno'
    if auth:
        token = auth.split()[-1]
        role = parse_token(token).get('rol', 'dueno')

    return {
        "nombre": "Soporte Técnico",
        "rol": role,
        "allowed_modules": get_allowed_modules(role),
        "plugins": plugins_activos
    }


# include routers from dedicated modules
app.include_router(empleados_router.router)
app.include_router(usuarios_router.router)