# =============================================================================
# Catálogos Motiva — dados sintéticos (10 catálogos)
# Especificação completa: scripts/synthetic_data_spec.py e docs/SYNTHETIC_DATA_SPEC.md
# Só cria os catálogos no workspace quando enable_motiva_synthetic_catalogs = true.
# Schemas e tabelas: usar script a partir de scripts/synthetic_data_spec.json
# =============================================================================

variable "enable_motiva_synthetic_catalogs" {
  description = "Se true, cria os 10 catálogos Motiva no workspace (schemas/tabelas ficam a cargo do script)."
  type        = bool
  default     = false
}

variable "motiva_external_location_name" {
  description = "Nome da External Location UC a usar como base para managed storage dos catálogos Motiva. Os paths por catálogo são criados como subpaths desta location."
  type        = string
  default     = ""
}

variable "motiva_catalog_storage_root" {
  description = "Alternativa: base path S3/ABFSS para managed storage (ex: s3://bucket/uc). Ignorado se motiva_external_location_name estiver definido."
  type        = string
  default     = ""
}

locals {
  motiva_catalog_names = [
    "motiva_rodovias",
    "motiva_trens",
    "motiva_metro",
    "motiva_pedagios",
    "motiva_rh",
    "motiva_manutencao",
    "motiva_financeiro",
    "motiva_operacoes",
    "motiva_ativos",
    "motiva_clientes",
  ]
  # Base URL: da external location (se nome dado) ou da variável storage_root
  _motiva_base_url   = coalesce(try(data.databricks_external_location.motiva_base[0].external_location_info[0].url, null), var.motiva_catalog_storage_root)
  motiva_storage_root = (var.enable_motiva_synthetic_catalogs && local._motiva_base_url != "") ? local._motiva_base_url : ""
}

data "databricks_external_location" "motiva_base" {
  count = var.enable_motiva_synthetic_catalogs && var.motiva_external_location_name != "" ? 1 : 0
  name  = var.motiva_external_location_name
}

resource "databricks_catalog" "motiva" {
  for_each = var.enable_motiva_synthetic_catalogs && local.motiva_storage_root != "" ? toset(local.motiva_catalog_names) : toset([])

  name         = each.value
  comment      = "Catálogo Motiva (dados sintéticos) — ver scripts/synthetic_data_spec.json"
  properties   = {}
  storage_root = "${trim(local.motiva_storage_root, "/")}/${each.value}"
}

output "motiva_catalogs" {
  description = "Nomes dos catálogos Motiva (criados apenas se enable_motiva_synthetic_catalogs = true)"
  value       = local.motiva_catalog_names
}
