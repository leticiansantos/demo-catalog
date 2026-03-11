#!/usr/bin/env python3
"""
Especificação de dados sintéticos Motiva — 10 catálogos, schemas e tabelas.
Gera a lista completa com nomes (não cria recursos).
Uso: python synthetic_data_spec.py [--list] [--json] [--yaml]
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

# Seed fixo para contagens reproduzíveis (5–30 tabelas por schema)
RANDOM_SEED = 42

# Schema mínimo garantido em cada catálogo: 1 schema "base" com 5 tabelas
BASE_SCHEMA_NAME = "base"
BASE_TABLE_COUNT = 5

# 10 catálogos Motiva: área -> (catalog_name, list of schema names)
MOTIVA_CATALOGS = {
    "rodovias": {
        "catalog": "motiva_rodovias",
        "description": "Concessões, tráfego e indicadores de rodovias",
        "schemas": [
            "raw_concessoes",
            "silver_trafego",
            "gold_indicadores",
            "custos_operacao",
            "incidentes",
        ],
    },
    "trens": {
        "catalog": "motiva_trens",
        "description": "Viagens, frota e passageiros de trens",
        "schemas": [
            "raw_viagens",
            "silver_frota",
            "gold_passageiros",
            "manutencao_vagoes",
            "horarios",
        ],
    },
    "metro": {
        "catalog": "motiva_metro",
        "description": "Estações, linhas e bilhetagem do metrô",
        "schemas": [
            "raw_estacoes",
            "silver_linhas",
            "gold_bilhetagem",
            "seguranca",
            "infraestrutura",
        ],
    },
    "pedagios": {
        "catalog": "motiva_pedagios",
        "description": "Transações, tags e faturamento de pedágios",
        "schemas": [
            "raw_transacoes",
            "silver_tags",
            "gold_faturamento",
            "concessionarias",
            "tarifas",
        ],
    },
    "rh": {
        "catalog": "motiva_rh",
        "description": "Funcionários, folha e indicadores de RH",
        "schemas": [
            "raw_funcionarios",
            "silver_folha",
            "gold_indicadores_rh",
            "treinamentos",
            "beneficios",
        ],
    },
    "manutencao": {
        "catalog": "motiva_manutencao",
        "description": "Ordens de serviço, equipamentos e custos de manutenção",
        "schemas": [
            "raw_ordens_servico",
            "silver_equipamentos",
            "gold_custos_manutencao",
            "contratos",
            "historico",
        ],
    },
    "financeiro": {
        "catalog": "motiva_financeiro",
        "description": "Lançamentos, contas e DRE",
        "schemas": [
            "raw_lancamentos",
            "silver_contas",
            "gold_dre",
            "orcamento",
            "conciliacao",
        ],
    },
    "operacoes": {
        "catalog": "motiva_operacoes",
        "description": "Eventos, turnos e produção operacional",
        "schemas": [
            "raw_eventos",
            "silver_turnos",
            "gold_producao",
            "dashboards",
            "alertas",
        ],
    },
    "ativos": {
        "catalog": "motiva_ativos",
        "description": "Veículos, equipamentos e depreciação",
        "schemas": [
            "raw_veiculos",
            "silver_equipamentos",
            "gold_depreciacao",
            "localizacao",
            "documentos",
        ],
    },
    "clientes": {
        "catalog": "motiva_clientes",
        "description": "Cadastros, contratos e consumo de clientes/usuários",
        "schemas": [
            "raw_cadastros",
            "silver_contratos",
            "gold_consumo",
            "suporte",
            "preferencias",
        ],
    },
}


def _table_count_for(schema_key: str, schema_name: str, index: int) -> int:
    """Número de tabelas no schema (5 a 30), determinístico por seed."""
    rng = random.Random(f"{RANDOM_SEED}_{schema_key}_{schema_name}_{index}")
    return rng.randint(5, 30)


def _table_name(schema_name: str, i: int) -> str:
    """Nome da tabela: schema_tab_N (UC exige snake_case, sem caracteres especiais)."""
    return f"{schema_name}_tab_{i}"


def build_spec():
    """Constrói a especificação completa: catálogos -> schemas -> tabelas.
    Cada catálogo tem garantido pelo menos 1 schema ('base') com 5 tabelas, além dos demais.
    """
    random.seed(RANDOM_SEED)
    spec = []
    for area, info in MOTIVA_CATALOGS.items():
        catalog_name = info["catalog"]
        catalog_entry = {
            "catalog": catalog_name,
            "description": info["description"],
            "schemas": [],
        }
        # Garantir pelo menos 1 schema e 5 tabelas: schema "base" com base_tab_1..base_tab_5
        base_tables = [_table_name(BASE_SCHEMA_NAME, i) for i in range(1, BASE_TABLE_COUNT + 1)]
        catalog_entry["schemas"].append({
            "schema": BASE_SCHEMA_NAME,
            "tables": base_tables,
            "table_count": BASE_TABLE_COUNT,
        })
        for idx, schema_name in enumerate(info["schemas"]):
            n_tables = _table_count_for(area, schema_name, idx)
            tables = [_table_name(schema_name, i) for i in range(1, n_tables + 1)]
            catalog_entry["schemas"].append({
                "schema": schema_name,
                "tables": tables,
                "table_count": n_tables,
            })
        spec.append(catalog_entry)
    return spec


def print_list(spec: list) -> None:
    """Imprime a lista legível de tudo a ser criado."""
    total_catalogs = len(spec)
    total_schemas = sum(len(c["schemas"]) for c in spec)
    total_tables = sum(
        s["table_count"] for c in spec for s in c["schemas"]
    )
    print("=" * 70)
    print("MOTIVA — LISTA DE RECURSOS A CRIAR (dados sintéticos)")
    print("=" * 70)
    print(f"Total: {total_catalogs} catálogos | {total_schemas} schemas | {total_tables} tabelas")
    print()
    for cat in spec:
        print(f"CATALOG  {cat['catalog']}")
        print(f"  ({cat['description']})")
        for sch in cat["schemas"]:
            print(f"  SCHEMA  {sch['schema']}  ({sch['table_count']} tabelas)")
            for t in sch["tables"]:
                print(f"    TABLE  {t}")
        print()
    print("=" * 70)


def export_json(spec: list, path: Path | None = None) -> str:
    out = json.dumps(spec, indent=2, ensure_ascii=False)
    if path:
        path.write_text(out, encoding="utf-8")
    return out


def export_yaml(spec: list, path: Path | None = None) -> str:
    try:
        import yaml
    except ImportError:
        return export_json(spec, path)
    out = yaml.dump(spec, allow_unicode=True, default_flow_style=False, sort_keys=False)
    if path:
        Path(path).write_text(out, encoding="utf-8")
    return out


def main():
    parser = argparse.ArgumentParser(description="Especificação dados sintéticos Motiva")
    parser.add_argument("--list", action="store_true", help="Imprimir lista legível")
    parser.add_argument("--json", action="store_true", help="Exportar JSON para stdout")
    parser.add_argument("--yaml", action="store_true", help="Exportar YAML para stdout")
    parser.add_argument("--out-json", type=Path, help="Escrever spec em JSON neste ficheiro")
    parser.add_argument("--out-yaml", type=Path, help="Escrever spec em YAML neste ficheiro")
    args = parser.parse_args()

    spec = build_spec()

    if args.list or not (args.json or args.yaml or args.out_json or args.out_yaml):
        print_list(spec)

    if args.json:
        print(export_json(spec))
    if args.out_json:
        export_json(spec, args.out_json)
        print(f"Spec JSON escrita em {args.out_json}", file=sys.stderr)

    if args.yaml:
        print(export_yaml(spec))
    if args.out_yaml:
        export_yaml(spec, args.out_yaml)
        print(f"Spec YAML escrita em {args.out_yaml}", file=sys.stderr)


if __name__ == "__main__":
    main()
