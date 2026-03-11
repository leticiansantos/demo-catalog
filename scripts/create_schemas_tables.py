#!/usr/bin/env python3
"""
Cria schemas e tabelas no Databricks a partir da spec Motiva (synthetic_data_spec.json).
Cada tabela recebe entre 3 e 15 colunas com nomes coerentes ao catálogo/schema (table_columns.py).
Requer: DATABRICKS_HOST e DATABRICKS_TOKEN (ou databricks auth login) e um SQL Warehouse.
Uso: python create_schemas_tables.py [--spec path/to/spec.json] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Path para a spec (relativo ao script ou repo root)
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_SPEC = SCRIPT_DIR / "synthetic_data_spec.json"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from table_columns import get_columns_for_table, get_table_comment


def load_spec(path: Path) -> list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _escape_sql_string(s: str) -> str:
    """Escapa aspas simples para uso em strings SQL ('')."""
    return s.replace("'", "''")


def get_warehouse_id(w):
    warehouse_id = os.environ.get("DATABRICKS_SQL_WAREHOUSE_ID")
    if warehouse_id:
        return warehouse_id
    warehouses = list(w.warehouses.list())
    if not warehouses:
        raise SystemExit(
            "Nenhum SQL Warehouse encontrado. Crie um no workspace ou defina DATABRICKS_SQL_WAREHOUSE_ID."
        )
    return warehouses[0].id


def main():
    parser = argparse.ArgumentParser(description="Cria schemas e tabelas Motiva no Databricks")
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC, help="Ficheiro JSON da spec")
    parser.add_argument("--dry-run", action="store_true", help="Apenas mostrar o que seria criado")
    args = parser.parse_args()

    if not args.spec.exists():
        print(f"Erro: spec não encontrada: {args.spec}", file=sys.stderr)
        sys.exit(1)

    spec = load_spec(args.spec)
    if args.dry_run:
        total_s, total_t = 0, 0
        for cat in spec:
            for sch in cat["schemas"]:
                total_s += 1
                total_t += len(sch["tables"])
        print(f"[dry-run] Seriam criados {total_s} schemas e {total_t} tabelas.")
        return

    try:
        from databricks.sdk import WorkspaceClient
    except ImportError:
        print("Instale o Databricks SDK: pip install databricks-sdk", file=sys.stderr)
        sys.exit(1)

    w = WorkspaceClient()
    warehouse_id = get_warehouse_id(w)
    print(f"Warehouse ID: {warehouse_id}", flush=True)

    created_schemas = 0
    created_tables = 0
    errors = []

    for cat in spec:
        catalog_name = cat["catalog"]
        for sch in cat["schemas"]:
            schema_name = sch["schema"]
            full_schema = f"{catalog_name}.{schema_name}"
            try:
                w.statement_execution.execute_statement(
                    warehouse_id=warehouse_id,
                    statement=f"CREATE SCHEMA IF NOT EXISTS {full_schema}",
                    wait_timeout="50s",
                )
                created_schemas += 1
            except Exception as e:
                errors.append((f"SCHEMA {full_schema}", str(e)))
                continue

            for table_name in sch["tables"]:
                full_table = f"{full_schema}.{table_name}"
                columns = get_columns_for_table(catalog_name, schema_name, table_name)
                col_list = ", ".join(
                    f"{name} {dtype} COMMENT '{_escape_sql_string(comment)}'"
                    for name, dtype, comment in columns
                )
                sql = f"CREATE OR REPLACE TABLE {full_table} ({col_list}) USING DELTA"
                try:
                    w.statement_execution.execute_statement(
                        warehouse_id=warehouse_id,
                        statement=sql,
                        wait_timeout="50s",
                    )
                    created_tables += 1
                except Exception as e:
                    errors.append((f"TABLE {full_table}", str(e)))
                    continue
                # Comentário da tabela
                table_comment = get_table_comment(catalog_name, schema_name, table_name)
                comment_sql = f"COMMENT ON TABLE {full_table} IS '{_escape_sql_string(table_comment)}'"
                try:
                    w.statement_execution.execute_statement(
                        warehouse_id=warehouse_id,
                        statement=comment_sql,
                        wait_timeout="30s",
                    )
                except Exception as e:
                    errors.append((f"COMMENT TABLE {full_table}", str(e)))

            if created_tables % 100 == 0 and created_tables > 0:
                print(f"  ... {created_schemas} schemas, {created_tables} tabelas", flush=True)

    print(f"\nConcluído: {created_schemas} schemas, {created_tables} tabelas criados.")
    if errors:
        print(f"\nErros ({len(errors)}):", file=sys.stderr)
        for target, msg in errors[:20]:
            print(f"  {target}: {msg}", file=sys.stderr)
        if len(errors) > 20:
            print(f"  ... e mais {len(errors) - 20} erros", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
