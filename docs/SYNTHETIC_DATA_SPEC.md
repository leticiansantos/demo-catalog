# Motiva — Lista de recursos para dados sintéticos

Empresa simulada: **Motiva** (rodovias, trens, metrô, pedágios, RH e áreas internas).

**Estrutura atual:** um único catálogo **`leticia_demo_catalog_catalog`** com **60 schemas** e **963 tabelas**.  
Os schemas têm nome **`{domínio}_{schema}`** (ex.: `motiva_ativos_base`, `motiva_rodovias_silver_trafego`), como no antigo `motiva_ativos` em que o schema era `base` — agora fica `motiva_ativos_base`.

**Totais:** 1 catálogo | 60 schemas | 963 tabelas.

---

## Catálogo único: leticia_demo_catalog_catalog

Todos os domínios Motiva ficam neste catálogo, com schemas concatenados:

| Domínio (prefixo do schema) | Exemplos de schemas |
|-----------------------------|---------------------|
| motiva_rodovias | `motiva_rodovias_base`, `motiva_rodovias_raw_concessoes`, `motiva_rodovias_silver_trafego`, … |
| motiva_trens | `motiva_trens_base`, `motiva_trens_raw_viagens`, … |
| motiva_metro | `motiva_metro_base`, `motiva_metro_raw_estacoes`, … |
| motiva_pedagios | `motiva_pedagios_base`, `motiva_pedagios_raw_transacoes`, … |
| motiva_rh | `motiva_rh_base`, `motiva_rh_raw_funcionarios`, … |
| motiva_manutencao | `motiva_manutencao_base`, `motiva_manutencao_raw_ordens_servico`, … |
| motiva_financeiro | `motiva_financeiro_base`, `motiva_financeiro_raw_lancamentos`, … |
| motiva_operacoes | `motiva_operacoes_base`, `motiva_operacoes_raw_eventos`, … |
| motiva_ativos | `motiva_ativos_base`, `motiva_ativos_raw_veiculos`, `motiva_ativos_silver_equipamentos`, … |
| motiva_clientes | `motiva_clientes_base`, `motiva_clientes_raw_cadastros`, … |

---

## Estrutura lógica por domínio (schemas no catálogo único)

Os schemas no catálogo único seguem a mesma estrutura lógica; o nome do schema é `{domínio}_{schema}`.

### motiva_rodovias

**Schemas no catálogo único:** `motiva_rodovias_base` | `motiva_rodovias_raw_concessoes` | `motiva_rodovias_silver_trafego` | etc.

- **base** — 5 tabelas: `base_tab_1` … `base_tab_5` (mínimo garantido em todos os catálogos)
- **raw_concessoes** — 23 tabelas: `raw_concessoes_tab_1` … `raw_concessoes_tab_23`
- **silver_trafego** — 29 tabelas: `silver_trafego_tab_1` … `silver_trafego_tab_29`
- **gold_indicadores** — 19 tabelas: `gold_indicadores_tab_1` … `gold_indicadores_tab_19`
- **custos_operacao** — 20 tabelas: `custos_operacao_tab_1` … `custos_operacao_tab_20`
- **incidentes** — 25 tabelas: `incidentes_tab_1` … `incidentes_tab_25`

---

## 2. motiva_trens

**Schemas:** `raw_viagens` | `silver_frota` | `gold_passageiros` | `manutencao_vagoes` | `horarios`

- **raw_viagens** — 20 tabelas: `raw_viagens_tab_1` … `raw_viagens_tab_20`
- **silver_frota** — 22 tabelas: `silver_frota_tab_1` … `silver_frota_tab_22`
- **gold_passageiros** — 24 tabelas: `gold_passageiros_tab_1` … `gold_passageiros_tab_24`
- **manutencao_vagoes** — 16 tabelas: `manutencao_vagoes_tab_1` … `manutencao_vagoes_tab_16`
- **horarios** — 15 tabelas: `horarios_tab_1` … `horarios_tab_15`

---

## 3. motiva_metro

**Schemas:** `raw_estacoes` | `silver_linhas` | `gold_bilhetagem` | `seguranca` | `infraestrutura`

- **raw_estacoes** — 15 tabelas
- **silver_linhas** — 23 tabelas
- **gold_bilhetagem** — 29 tabelas
- **seguranca** — 9 tabelas
- **infraestrutura** — 24 tabelas

---

## 4. motiva_pedagios

**Schemas:** `raw_transacoes` | `silver_tags` | `gold_faturamento` | `concessionarias` | `tarifas`

- **raw_transacoes** — 18 tabelas
- **silver_tags** — 28 tabelas
- **gold_faturamento** — 22 tabelas
- **concessionarias** — 12 tabelas
- **tarifas** — 13 tabelas

---

## 5. motiva_rh

**Schemas:** `raw_funcionarios` | `silver_folha` | `gold_indicadores_rh` | `treinamentos` | `beneficios`

- **raw_funcionarios** — 19 tabelas
- **silver_folha** — 28 tabelas
- **gold_indicadores_rh** — 14 tabelas
- **treinamentos** — 12 tabelas
- **beneficios** — 16 tabelas

---

## 6. motiva_manutencao

**Schemas:** `raw_ordens_servico` | `silver_equipamentos` | `gold_custos_manutencao` | `contratos` | `historico`

- **raw_ordens_servico** — 22 tabelas
- **silver_equipamentos** — 26 tabelas
- **gold_custos_manutencao** — 18 tabelas
- **contratos** — 14 tabelas
- **historico** — 15 tabelas

---

## 7. motiva_financeiro

**Schemas:** `raw_lancamentos` | `silver_contas` | `gold_dre` | `orcamento` | `conciliacao`

- **raw_lancamentos** — 24 tabelas
- **silver_contas** — 24 tabelas
- **gold_dre** — 27 tabelas
- **orcamento** — 21 tabelas
- **conciliacao** — 20 tabelas

---

## 8. motiva_operacoes

**Schemas:** `raw_eventos` | `silver_turnos` | `gold_producao` | `dashboards` | `alertas`

- **raw_eventos** — 7 tabelas
- **silver_turnos** — 5 tabelas
- **gold_producao** — 14 tabelas
- **dashboards** — 11 tabelas
- **alertas** — 24 tabelas

---

## 9. motiva_ativos

**Schemas:** `raw_veiculos` | `silver_equipamentos` | `gold_depreciacao` | `localizacao` | `documentos`

- **raw_veiculos** — 8 tabelas
- **silver_equipamentos** — 29 tabelas
- **gold_depreciacao** — 16 tabelas
- **localizacao** — 15 tabelas
- **documentos** — 25 tabelas

---

## 10. motiva_clientes

**Schemas:** `raw_cadastros` | `silver_contratos` | `gold_consumo` | `suporte` | `preferencias`

- **raw_cadastros** — 8 tabelas
- **silver_contratos** — 17 tabelas
- **gold_consumo** — 5 tabelas
- **suporte** — 14 tabelas
- **preferencias** — 26 tabelas

---

## Como usar

- **Lista completa (nomes exatos):** `python3 scripts/synthetic_data_spec.py --list`
- **Spec em JSON:** `scripts/synthetic_data_spec.json` (usado por `scripts/create_schemas_tables.py`)
- **Criar catálogo, schemas e tabelas:** `scripts/create_schemas_tables.py` — cria o catálogo `leticia_demo_catalog_catalog` (se não existir), depois os 60 schemas e 963 tabelas. Requer `DATABRICKS_HOST`, token e um SQL Warehouse.
