#!/usr/bin/env python3
"""
Atualiza tabelas existentes no Databricks (workspace fevm-leticia-demo-catalog):
- Adiciona colunas extras de forma aleatória com nomes que fazem sentido para o domínio.
- Define descrição (comment) em cada tabela e em cada coluna.

Usa a mesma spec (synthetic_data_spec.json) e table_columns.py para domínio e comentários.
Requer: DATABRICKS_HOST e DATABRICKS_TOKEN (ou .env). Uso: python update_tables_columns_comments.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_SPEC = SCRIPT_DIR / "synthetic_data_spec.json"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

# Carregar .env: catalog-browser/.env sobrescreve (workspace fevm-leticia-demo-catalog)
_env_override = REPO_ROOT / "catalog-browser" / ".env"
_env_fallback = REPO_ROOT / ".env"
for _env_path in (_env_fallback, _env_override):
    if _env_path.exists():
        _override = _env_path == _env_override
        with open(_env_path, encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _, _v = _line.partition("=")
                    _k, _v = _k.strip(), _v.strip().strip("'\"")
                    if _k and _v and (_override or _k not in os.environ):
                        os.environ[_k] = _v

from table_columns import (
    COLUMN_POOLS,
    _comment_for_column,
    _domain_key_from_schema,
    get_table_comment,
)


def _escape(s: str) -> str:
    return s.replace("'", "''")


def get_warehouse_id(w):
    wid = os.environ.get("DATABRICKS_SQL_WAREHOUSE_ID")
    if wid:
        return wid
    whs = list(w.warehouses.list())
    if not whs:
        raise SystemExit("Nenhum SQL Warehouse encontrado. Defina DATABRICKS_SQL_WAREHOUSE_ID ou crie um warehouse.")
    return whs[0].id


def execute_sql(w, warehouse_id: str, sql: str, timeout: str = "30s") -> bool:
    try:
        w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=sql,
            wait_timeout=timeout,
        )
        return True
    except Exception as e:
        print(f"  ERRO: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Atualiza tabelas existentes: colunas extras e comentários")
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC, help="JSON da spec")
    parser.add_argument("--dry-run", action="store_true", help="Só listar o que seria feito")
    parser.add_argument("--min-add", type=int, default=2, help="Mínimo de colunas a adicionar por tabela")
    parser.add_argument("--max-add", type=int, default=8, help="Máximo de colunas a adicionar por tabela")
    args = parser.parse_args()

    if not args.spec.exists():
        print(f"Erro: spec não encontrada: {args.spec}", file=sys.stderr)
        sys.exit(1)

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)

    if args.dry_run:
        total = sum(len(s["tables"]) for c in spec for s in c["schemas"])
        print(f"[dry-run] Seriam atualizadas {total} tabelas (colunas extras + comentários).")
        return

    try:
        from databricks.sdk import WorkspaceClient
    except ImportError:
        print("Instale: pip install databricks-sdk", file=sys.stderr)
        sys.exit(1)

    w = WorkspaceClient()
    warehouse_id = get_warehouse_id(w)
    print(f"Warehouse ID: {warehouse_id}", flush=True)
    print(f"Host: {os.environ.get('DATABRICKS_HOST', '?')}", flush=True)

    updated = 0
    errors = []
    for cat in spec:
        catalog_name = cat["catalog"]
        for sch in cat["schemas"]:
            schema_name = sch["schema"]
            domain_key = _domain_key_from_schema(catalog_name, schema_name) or catalog_name
            pool = COLUMN_POOLS.get(domain_key)
            if not pool:
                pool = [("id", "BIGINT"), ("nome", "STRING"), ("valor", "DOUBLE"), ("observacao", "STRING")]

            for table_name in sch["tables"]:
                full_name = f"{catalog_name}.{schema_name}.{table_name}"
                try:
                    table_info = w.tables.get(full_name=full_name)
                except Exception as e:
                    errors.append((full_name, f"get: {e}"))
                    continue

                existing = {c.name for c in (table_info.columns or [])}
                all_column_names = [c.name for c in (table_info.columns or [])]

                # Colunas novas a adicionar (aleatório, nomes que fazem sentido)
                candidates = [(n, t) for n, t in pool if n not in existing]
                n_add = min(
                    random.randint(args.min_add, args.max_add),
                    len(candidates),
                )
                to_add = random.sample(candidates, n_add) if candidates else []

                # 1) ADD COLUMN para cada nova coluna
                for col_name, col_type in to_add:
                    comment = _comment_for_column(col_name)
                    sql = f"ALTER TABLE {full_name} ADD COLUMN (`{col_name}` {col_type} COMMENT '{_escape(comment)}')"
                    if not execute_sql(w, warehouse_id, sql):
                        errors.append((full_name, f"ADD COLUMN {col_name}"))
                    else:
                        all_column_names.append(col_name)

                # 2) COMMENT ON TABLE
                table_comment = get_table_comment(catalog_name, schema_name, table_name)
                sql = f"COMMENT ON TABLE {full_name} IS '{_escape(table_comment)}'"
                if not execute_sql(w, warehouse_id, sql):
                    errors.append((full_name, "COMMENT ON TABLE"))

                # 3) COMMENT em cada coluna (ALTER COLUMN SET COMMENT)
                for col_name in all_column_names:
                    comment = _comment_for_column(col_name)
                    sql = f"ALTER TABLE {full_name} ALTER COLUMN `{col_name}` SET COMMENT '{_escape(comment)}'"
                    if not execute_sql(w, warehouse_id, sql):
                        errors.append((full_name, f"COMMENT COLUMN {col_name}"))

                updated += 1
                if updated % 50 == 0:
                    print(f"  ... {updated} tabelas atualizadas", flush=True)

    print(f"\nConcluído: {updated} tabelas atualizadas.")
    if errors:
        print(f"Erros ({len(errors)}):", file=sys.stderr)
        for target, msg in errors[:30]:
            print(f"  {target}: {msg}", file=sys.stderr)
        if len(errors) > 30:
            print(f"  ... e mais {len(errors) - 30}", file=sys.stderr)


if __name__ == "__main__":
    main()
