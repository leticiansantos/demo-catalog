# Terraform — Workspace demo-catalog

Configuração centralizada do workspace Databricks para a demo. **Qualquer alteração de workspace (ID, nome, host) deve ser feita aqui** para manter scripts e recursos alinhados.

## Workspace atual

| Variável | Valor |
|----------|--------|
| `workspace_id` | 7474651371892136 |
| `workspace_name` | leticia-demo-catalog |
| `environment` | demo |

## Como mudar de workspace

1. Edite **`terraform.tfvars`** com o novo `workspace_id`, `workspace_name` e `databricks_host`.
2. Atualize também **`../deploy-workspace.sh`** (variáveis `WORKSPACE_ID` e `WORKSPACE_NAME`) para manter consistência.
3. Execute `terraform plan` e `terraform apply` se tiver recursos além do provider.

## Uso

```bash
# Autenticar (uma vez)
databricks auth login --host https://fevm-leticia-demo-catalog.cloud.databricks.com

# Inicializar e plan
cd terraform
terraform init
terraform plan
```

Os outputs (`workspace_id`, `workspace_name`, `databricks_host`) podem ser usados por outros scripts ou CI.

## Catálogos Motiva (dados sintéticos)

Para criar os 10 catálogos no workspace, defina em `terraform.tfvars`:

- **Opção A** — usar uma external location já existente no workspace:
  ```hcl
  enable_motiva_synthetic_catalogs = true
  motiva_external_location_name   = "NOME_DA_EXTERNAL_LOCATION"  # em UC > External locations
  ```
- **Opção B** — usar um path S3/ABFSS diretamente:
  ```hcl
  enable_motiva_synthetic_catalogs = true
  motiva_catalog_storage_root      = "s3://SEU_BUCKET/uc/motiva"
  ```

`motiva_catalog_storage_root` ou `motiva_external_location_name` é obrigatório se o metastore não tiver storage root (ex.: workspace com Default Storage).
