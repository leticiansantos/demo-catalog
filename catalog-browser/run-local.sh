#!/usr/bin/env bash
# Sobe o app local (backend + frontend) apontando para o workspace definido em .env.
# Backend usa DATABRICKS_HOST e DATABRICKS_TOKEN de catalog-browser/.env.
# Uso: cd catalog-browser && ./run-local.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ ! -f .env ]]; then
  echo "Crie .env a partir de .env.example e defina DATABRICKS_HOST e DATABRICKS_TOKEN do workspace."
  exit 1
fi

export $(grep -v '^#' .env | grep '=' | xargs)

echo "Workspace: ${DATABRICKS_HOST:-?(não definido)}"
echo "Backend: http://127.0.0.1:8000 | Frontend: http://127.0.0.1:5174"
echo ""

# Backend em background
uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
PID_BACKEND=$!
trap "kill $PID_BACKEND 2>/dev/null || true" EXIT

sleep 2
cd frontend && npm run dev
