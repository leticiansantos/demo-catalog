"""API de solicitações de acesso a dados — listagem para admin e criação pelo usuário."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Armazenamento em memória (demo). Em produção usar DB ou fila.
_requests: list[dict] = []


class AccessRequestCreate(BaseModel):
    catalog: str
    schema: str
    table: str
    reason: Optional[str] = None
    requested_by: Optional[str] = None


class AccessRequestResponse(BaseModel):
    id: str
    created_at: str
    catalog: str
    schema: str
    table: str
    full_name: str
    reason: Optional[str] = None
    requested_by: Optional[str] = None
    status: str = "pending"


@router.post("/access-requests", response_model=AccessRequestResponse)
def create_access_request(body: AccessRequestCreate):
    """Registra uma nova solicitação de acesso ao dado (tabela)."""
    req_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    full_name = f"{body.catalog}.{body.schema}.{body.table}"
    record = {
        "id": req_id,
        "created_at": now,
        "catalog": body.catalog,
        "schema": body.schema,
        "table": body.table,
        "full_name": full_name,
        "reason": body.reason,
        "requested_by": body.requested_by or "",
        "status": "pending",
    }
    _requests.append(record)
    return record


@router.get("/access-requests", response_model=list[AccessRequestResponse])
def list_access_requests():
    """Lista todas as solicitações de acesso (página admin)."""
    return sorted(_requests, key=lambda r: r["created_at"], reverse=True)
