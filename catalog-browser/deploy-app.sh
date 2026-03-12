#!/usr/bin/env bash
#
# Deploy Catalog Browser para Databricks Apps.
# - Faz sync do código para o workspace SEM usar .gitignore, para que .env seja enviado.
#   Usa .databricksignore (exclui node_modules, .venv, etc., mas NÃO .env).
# - Cria o app se não existir e faz deploy a partir do path de código.
#
# Uso:
#   cd catalog-browser && ./deploy-app.sh
#   WORKSPACE_APP_PATH=/Workspace/Users/meu@email.com/catalog-browser ./deploy-app.sh
#
# Pré-requisitos:
#   - databricks CLI configurado (databricks auth login ou DEFAULT profile).
#   - WORKSPACE_APP_PATH: path no workspace para onde o código será sincronizado.
#     Se não definido, o script tenta obter o usuário atual e usar /Workspace/Users/<user>/catalog-browser.
#   - Arquivo .env preenchido (DATABRICKS_HOST, DATABRICKS_TOKEN, etc.) para o sync usar o workspace correto.

set -e

APP_NAME="catalog-browser"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Path no workspace onde o código da app ficará (obrigatório para sync e deploy)
if [[ -z "${WORKSPACE_APP_PATH}" ]]; then
  if command -v databricks &>/dev/null; then
    _json=$(databricks current-user me -o json 2>/dev/null) || true
    CURRENT_USER=$(printf '%s\n' "$_json" | grep -o '"userName"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
  fi
  if [[ -n "${CURRENT_USER}" ]]; then
    WORKSPACE_APP_PATH="/Workspace/Users/${CURRENT_USER}/${APP_NAME}"
  else
    echo "Erro: defina WORKSPACE_APP_PATH (ex.: export WORKSPACE_APP_PATH=/Workspace/Users/seu@email.com/${APP_NAME})"
    exit 1
  fi
fi

echo "App: ${APP_NAME}"
echo "Source: ${SCRIPT_DIR}"
echo "Workspace path: ${WORKSPACE_APP_PATH}"
echo ""

# Copiar .env para app.env (ficheiro não oculto) para o runtime do Apps carregar no deploy.
if [[ -f .env ]]; then
  cp .env app.env
  echo "Created app.env from .env for deployed app."
fi

# 1) Sync: enviar código. Incluir .env e app.env para o app deployado ter credenciais.
if [[ -f .databricksignore ]]; then
  echo "Syncing with --exclude-from .databricksignore and --include .env --include app.env..."
  databricks sync . "$WORKSPACE_APP_PATH" --exclude-from .databricksignore --include ".env" --include "app.env" --full
else
  echo "Syncing with --include .env and app.env..."
  databricks sync . "$WORKSPACE_APP_PATH" --include ".env" --include "app.env" --full
fi

# 2) Criar app se não existir
if ! databricks apps get "$APP_NAME" &>/dev/null; then
  echo "Creating app ${APP_NAME}..."
  databricks apps create "$APP_NAME" --description "Catalog Browser — navegação em árvore dos catálogos Unity Catalog (motiva_*)"
fi

# 3) Deploy a partir do path de código (AUTO_SYNC se disponível, senão SNAPSHOT)
echo "Deploying from ${WORKSPACE_APP_PATH}..."
if ! databricks apps deploy "$APP_NAME" --source-code-path "$WORKSPACE_APP_PATH" --mode AUTO_SYNC --no-wait 2>/dev/null; then
  databricks apps deploy "$APP_NAME" --source-code-path "$WORKSPACE_APP_PATH" --mode SNAPSHOT --no-wait
fi

echo ""
echo "Deploy iniciado. Verifique o status com: databricks apps get $APP_NAME"
echo "Logs: databricks apps logs $APP_NAME"
