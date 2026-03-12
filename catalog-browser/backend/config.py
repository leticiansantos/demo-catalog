import os

# Prefixo dos catálogos a listar (ex.: leticia_demo_catalog -> mostra leticia_demo_catalog_catalog). Vazio = todos.
CATALOG_PREFIX = (os.environ.get("CATALOG_PREFIX") or "leticia_demo_catalog").strip()
