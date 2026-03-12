"""Rotas da API: catálogos, schemas, tabelas (todos ou filtro por prefixo opcional)."""

from fastapi import APIRouter, HTTPException

from ..db import get_client
from ..config import CATALOG_PREFIX

router = APIRouter()


def _catalog_matches(name: str) -> bool:
    """Se CATALOG_PREFIX estiver vazio, aceita qualquer catálogo; senão filtra por prefixo."""
    if not CATALOG_PREFIX:
        return True
    return name.startswith(CATALOG_PREFIX)


@router.get("/catalogs")
def list_catalogs():
    """Lista todos os catálogos (ou apenas os que começam com CATALOG_PREFIX, se definido)."""
    try:
        w = get_client()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Databricks connection failed: {e}. Check DATABRICKS_HOST and DATABRICKS_TOKEN in .env / app.env.",
        )
    catalogs = []
    try:
        for c in w.catalogs.list(max_results=1000):
            name = c.name or ""
            if _catalog_matches(name):
                catalogs.append({
                    "name": name,
                    "comment": getattr(c, "comment", None) or "",
                })
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to list catalogs: {e}")
    return {"catalogs": sorted(catalogs, key=lambda x: x["name"])}


@router.get("/catalogs/{catalog_name}/schemas")
def list_schemas(catalog_name: str):
    """Lista schemas de um catálogo."""
    if not _catalog_matches(catalog_name):
        raise HTTPException(status_code=404, detail="Catalog not allowed")
    try:
        w = get_client()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Databricks connection failed: {e}")
    schemas = []
    try:
        for s in w.schemas.list(catalog_name=catalog_name, max_results=1000):
            schemas.append({
                "name": s.name or "",
                "comment": getattr(s, "comment", None) or "",
            })
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to list schemas: {e}")
    return {"schemas": sorted(schemas, key=lambda x: x["name"])}


@router.get("/catalogs/{catalog_name}/schemas/{schema_name}/tables")
def list_tables(catalog_name: str, schema_name: str):
    """Lista tabelas de um schema."""
    if not _catalog_matches(catalog_name):
        raise HTTPException(status_code=404, detail="Catalog not allowed")
    try:
        w = get_client()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Databricks connection failed: {e}")
    tables = []
    try:
        for t in w.tables.list(
            catalog_name=catalog_name,
            schema_name=schema_name,
            max_results=5000,
            omit_columns=True,
        ):
            tables.append({
                "name": t.name or "",
                "full_name": t.full_name or "",
                "table_type": getattr(t.table_type, "value", str(t.table_type)) if t.table_type else "TABLE",
                "comment": (t.comment or "")[:200] if t.comment else "",
            })
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to list tables: {e}")
    return {"tables": sorted(tables, key=lambda x: x["name"])}


@router.get("/catalogs/{catalog_name}/schemas/{schema_name}/tables/{table_name}")
def get_table(catalog_name: str, schema_name: str, table_name: str):
    """Detalhes da tabela: descrição, colunas (nome, tipo, descrição), dono, esquema."""
    if not _catalog_matches(catalog_name):
        raise HTTPException(status_code=404, detail="Catalog not allowed")
    full_name = f"{catalog_name}.{schema_name}.{table_name}"
    w = get_client()
    try:
        t = w.tables.get(full_name=full_name)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    columns = []
    for col in (t.columns or []):
        type_text = getattr(col, "type_text", None) or str(getattr(col, "type_name", ""))
        columns.append({
            "name": col.name or "",
            "type": type_text,
            "comment": getattr(col, "comment", None) or "",
            "nullable": getattr(col, "nullable", True),
            "position": getattr(col, "position", None),
        })
    return {
        "full_name": t.full_name or full_name,
        "name": t.name or table_name,
        "catalog_name": t.catalog_name or catalog_name,
        "schema_name": t.schema_name or schema_name,
        "description": t.comment or "",
        "owner": t.owner or "",
        "table_type": getattr(t.table_type, "value", str(t.table_type)) if t.table_type else "TABLE",
        "columns": sorted(columns, key=lambda c: (c["position"] if c["position"] is not None else 999, c["name"])),
        "created_at": t.created_at,
        "updated_at": t.updated_at,
    }
