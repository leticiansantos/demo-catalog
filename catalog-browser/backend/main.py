"""
Catalog Browser API — visualização em árvore do Unity Catalog para perfis não técnicos.
Ambiente compartilhado: apenas catálogos com prefixo "motiva".
"""

from pathlib import Path

from dotenv import load_dotenv

# Carrega .env a partir da raiz do catalog-browser (pasta acima de backend)
_env_dir = Path(__file__).resolve().parent.parent
load_dotenv(_env_dir / ".env")

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import catalog
from .db import get_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_client()
    yield


app = FastAPI(
    title="Catalog Browser",
    description="Navegação em árvore dos catálogos Databricks (apenas motiva_*)",
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
app.include_router(catalog.router, prefix="/api", tags=["catalog"])


@app.get("/health")
def health():
    return {"status": "ok"}
