"""
Catalog Browser API — visualização em árvore do Unity Catalog para perfis não técnicos.
Lista todos os catálogos e schemas (filtro opcional via CATALOG_PREFIX).
Serve a API e, em produção, os estáticos do frontend (frontend/dist).
"""

from pathlib import Path

from dotenv import load_dotenv

# Carrega credenciais: .env (local) e app.env (deploy; ficheiro não oculto para o runtime do Apps).
_env_dir = Path(__file__).resolve().parent.parent
for _name in (".env", "app.env"):
    for _base in (Path.cwd(), _env_dir):
        _p = _base / _name
        if _p.exists():
            try:
                load_dotenv(_p)
            except Exception:
                pass
# Em Databricks Apps a plataforma injeta OAuth (CLIENT_ID, CLIENT_SECRET). Se temos token no app.env,
# forçar uso só do PAT removendo as variáveis OAuth para evitar "more than one authorization method".
import os as _os
if _os.environ.get("DATABRICKS_TOKEN"):
    for _k in ("DATABRICKS_CLIENT_ID", "DATABRICKS_CLIENT_SECRET", "DATABRICKS_WORKSPACE_ID"):
        _os.environ.pop(_k, None)
_host = _os.environ.get("DATABRICKS_HOST", "").strip()
if _host and not _host.startswith(("http://", "https://")):
    _os.environ["DATABRICKS_HOST"] = f"https://{_host}"

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes import catalog
from .routes import access_requests
from .db import get_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    import os
    host = os.environ.get("DATABRICKS_HOST", "")
    if host:
        print(f"Catalog Browser: workspace {host}", flush=True)
    # Não chamar get_client() aqui: evita crash no deploy se .env/app.env não for lido a tempo
    yield


app = FastAPI(
    title="Catalog Browser",
    description="Navegação em árvore dos catálogos e schemas Unity Catalog",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# access_requests antes do catalog para garantir que /api/access-requests não seja confundido com /api/catalogs/...
app.include_router(access_requests.router, prefix="/api", tags=["access-requests"])
app.include_router(catalog.router, prefix="/api", tags=["catalog"])


@app.get("/health")
def health():
    import os
    host = os.environ.get("DATABRICKS_HOST", "")
    return {"status": "ok", "workspace_configured": bool(host), "workspace": host or "(not set)"}

# Servir frontend estático (build React) quando existir frontend/dist — ex.: após deploy no Databricks Apps
_frontend_dist = _env_dir / "frontend" / "dist"
if _frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="frontend")
