# Demo Catalog

Repositório com configuração e scripts para workspace Databricks usado em demos: Terraform para o workspace de teste e script para criar novos workspaces via FE Vending Machine.

## Estrutura

```
demo-catalog/
├── README.md           # este ficheiro
├── deploy-workspace.sh # cria um workspace via FE Vending Machine (AWS Stable Classic)
├── .gitignore
└── terraform/          # workspace de teste (variáveis centralizadas)
    ├── README.md
    ├── main.tf
    ├── variables.tf
    ├── versions.tf
    ├── terraform.tfvars.example
    └── terraform.tfvars             # não versionado (cópia do .example e editar)
```

## Terraform (workspace de teste)

O Terraform define o **workspace de teste** atual (ID, nome, host). Use-o como referência para recursos e para trocar de workspace no futuro.

- **Configuração:** editar `terraform/terraform.tfvars` (não está no Git; usar `terraform.tfvars.example` como base).
- **Uso:** ver [terraform/README.md](terraform/README.md).

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # se ainda não existir
# editar terraform.tfvars com o teu workspace
terraform init
terraform plan
```

## Criar um novo workspace (FE Vending Machine)

O script `deploy-workspace.sh` cria um workspace Databricks com o template **AWS Stable Classic** via FE Vending Machine. Use-o quando quiser criar ou mudar para outro workspace.

- **Nome do workspace:** variável `DEPLOY_WORKSPACE_NAME` no script (por defeito `leticia-demo-catalog`) ou:

  ```bash
  DEPLOY_WORKSPACE_NAME=meu-workspace ./deploy-workspace.sh
  ```

- **Pré-requisitos:** autenticação na [FE Vending Machine](https://vending-machine-main-2481552415672103.aws.databricksapps.com/) (ver mensagens do script).

```bash
./deploy-workspace.sh
```

## Dados sintéticos (Motiva)

Simulação de 10 catálogos da empresa **Motiva** (rodovias, trens, metrô, pedágios, RH, etc.): 50 schemas e ~913 tabelas (5–30 por schema).

- **Lista completa com nomes:** [docs/SYNTHETIC_DATA_SPEC.md](docs/SYNTHETIC_DATA_SPEC.md)
- **Ver lista no terminal:** `python3 scripts/synthetic_data_spec.py --list`
- **Spec em JSON:** `scripts/synthetic_data_spec.json` (para criação programática)
- **Criar schemas e tabelas:** depois dos catálogos criados pelo Terraform, corre `scripts/create_schemas_tables.py` (requer `databricks-sdk`, `DATABRICKS_HOST`/token e um SQL Warehouse). Ver `scripts/requirements.txt`.

## Catalog Browser (app)

App para **pessoas não técnicas** visualizarem o que existe no Databricks: árvore de catálogos → schemas → tabelas (estilo armazenamento de ficheiros). Ao clicar numa tabela: descrição, colunas (tipo e descrição), esquema e dono. Para a demo, só são listados catálogos com prefixo **motiva**.

- **Código:** [catalog-browser/](catalog-browser/) (backend FastAPI + frontend React)
- **Como correr:** ver [catalog-browser/README.md](catalog-browser/README.md)

## Requisitos

- [Terraform](https://www.terraform.io/) (≥ 1.0) e provider Databricks
- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/index.html) para `databricks auth login`
- Python 3 (para o cliente da Vending Machine e script de spec)
