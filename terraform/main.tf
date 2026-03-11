# =============================================================================
# Provider Databricks — usa variáveis centralizadas para facilitar troca de
# workspace. Autenticação: databricks auth login --host <databricks_host>
# ou env DATABRICKS_HOST + DATABRICKS_TOKEN.
# =============================================================================

provider "databricks" {
  host = var.databricks_host
}

# Outputs para uso em scripts e CI
output "workspace_id" {
  description = "Workspace ID"
  value       = var.workspace_id
}

output "workspace_name" {
  description = "Nome do workspace"
  value       = var.workspace_name
}

output "databricks_host" {
  description = "Host do workspace"
  value       = var.databricks_host
  sensitive   = false
}

output "environment" {
  description = "Ambiente"
  value       = var.environment
}
