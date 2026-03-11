# =============================================================================
# Workspace demo-catalog — variáveis centralizadas
# Para trocar de workspace no futuro: altere apenas terraform.tfvars (ou
# variáveis de ambiente / -var) e reaplique o Terraform.
# =============================================================================

variable "workspace_id" {
  description = "Databricks workspace ID (numérico)."
  type        = string
}

variable "workspace_name" {
  description = "Nome do workspace (ex: leticia-santos-test)."
  type        = string
}

variable "databricks_host" {
  description = "URL do workspace (ex: https://adb-XXXX.7.azuredatabricks.net ou https://xxx.cloud.databricks.com). Obtenha da barra de endereços ao abrir o workspace."
  type        = string
}

variable "environment" {
  description = "Ambiente (ex: demo, dev, prod)."
  type        = string
  default     = "demo"
}
