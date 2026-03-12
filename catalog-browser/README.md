# Catalog Browser

Visualização em árvore do Unity Catalog para perfis **não técnicos**: navegação tipo armazenamento de ficheiros e, ao clicar numa tabela, ver descrição, colunas (com tipo e descrição), esquema e dono.

**Demo:** em ambiente compartilhado mostramos apenas catálogos com prefixo **`motiva`** (configurável via `CATALOG_PREFIX`).

## Requisitos

- Python 3.10+ com `databricks-sdk` e FastAPI
- Node 18+ (para o frontend)
- Databricks workspace com Unity Catalog e token/host configurados

## Configuração

1. Copie o ficheiro de exemplo e preencha:
   ```bash
   cd catalog-browser
   cp .env.example .env
   # Edite .env: defina DATABRICKS_HOST e DATABRICKS_TOKEN (ou use databricks auth login)
   ```
2. **Variáveis:**
   - `DATABRICKS_HOST` — URL do workspace (ex.: https://fe-sandbox-....cloud.databricks.com)
   - `DATABRICKS_TOKEN` — token de acesso (opcional se usar `databricks auth login`)
   - `CATALOG_PREFIX` — prefixo dos catálogos a listar (default: `motiva`)

## Como correr

### 1. Backend (FastAPI)

A partir da pasta **`catalog-browser`** (para que o pacote `backend` seja encontrado). Usa o venv da aplicação:

```bash
cd catalog-browser
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
cp .env.example .env       # e edite .env com DATABRICKS_HOST e token
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend (React + Vite)

Noutro terminal:

```bash
cd catalog-browser/frontend
npm install
npm run dev
```

Abre o browser em **http://localhost:5174**. O frontend faz proxy de `/api` e `/health` para o backend na porta 8000.

## Deploy no Databricks Apps

O app pode ser implantado como [Databricks App](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/). O sync usa **`.databricksignore`** (e não `.gitignore`), para que o ficheiro **`.env`** seja enviado ao workspace sem alterar o `.gitignore`.

1. **Configure o `.env`** (DATABRICKS_HOST, DATABRICKS_TOKEN, etc.) e autentique o CLI:
   ```bash
   databricks auth login
   ```
2. **Defina o path do código no workspace** (obrigatório):
   ```bash
   export WORKSPACE_APP_PATH="/Workspace/Users/SEU_EMAIL@empresa.com/catalog-browser"
   ```
3. **Execute o script de deploy** a partir da pasta do app:
   ```bash
   cd catalog-browser
   ./deploy-app.sh
   ```
O script faz: sync com `--exclude-from .databricksignore` (inclui `.env`), cria o app se não existir e executa `databricks apps deploy` em modo AUTO_SYNC.

## Estrutura

- **backend/** — FastAPI; lista catálogos (motiva_*), schemas, tabelas; detalhe da tabela (descrição, colunas, dono).
- **frontend/** — React; árvore (catálogo → schema → tabela) e painel de detalhe ao clicar na tabela.
