#!/usr/bin/env python3
"""
Colunas por domínio (catálogo/schema) para tabelas sintéticas Motiva.
Cada tabela recebe entre 3 e 15 colunas com nomes coerentes ao catálogo e schema.
Comentários por coluna e por tabela derivados do nome (português).
Seleção determinística por (catalog, schema, table) para reprodutibilidade.
"""

from __future__ import annotations

import re
import random
from typing import List, Tuple

# (nome, tipo, comentário)
ColumnDef = Tuple[str, str, str]

# Mínimo e máximo de colunas por tabela
MIN_COLUMNS = 3
MAX_COLUMNS = 15

# Comentários por nome de coluna (português). Usado para COMMENT na definição da coluna.
COLUMN_COMMENTS: dict[str, str] = {
    "id": "Identificador único do registro",
    "concessionaria": "Nome da concessionária responsável",
    "rodovia": "Identificação ou nome da rodovia",
    "km_inicial": "Quilômetro inicial do trecho",
    "km_final": "Quilômetro final do trecho",
    "data_concessao": "Data de assinatura ou vigência da concessão",
    "data_medicao": "Data em que foi realizada a medição",
    "trafego_veiculos": "Volume de veículos no tráfego",
    "trafego_pesados": "Volume de veículos pesados no tráfego",
    "tarifa_media": "Valor médio da tarifa aplicada",
    "valor_contrato": "Valor total ou referência do contrato",
    "trecho": "Identificação do trecho da via",
    "sentido": "Sentido da via (ex.: norte, sul)",
    "pista": "Identificação da pista",
    "ano": "Ano de referência",
    "mes": "Mês de referência",
    "created_at": "Data e hora de criação do registro",
    "updated_at": "Data e hora da última atualização",
    "ativo": "Indica se o registro está ativo",
    "observacao": "Observações ou notas adicionais",
    "codigo_br": "Código BR da rodovia",
    "extensao_km": "Extensão em quilômetros",
    "volume_diario": "Volume diário de tráfego",
    "linha": "Identificação da linha (trem/metrô)",
    "estacao_origem": "Estação de origem da viagem",
    "estacao_destino": "Estação de destino da viagem",
    "data_viagem": "Data em que a viagem foi realizada",
    "hora_partida": "Data e hora de partida",
    "hora_chegada": "Data e hora de chegada",
    "vagao": "Identificação do vagão",
    "composicao": "Identificação da composição (conjunto de vagões)",
    "passageiros": "Quantidade de passageiros",
    "km_percorridos": "Quilômetros percorridos",
    "atraso_minutos": "Atraso em minutos em relação ao previsto",
    "operadora": "Nome da operadora do serviço",
    "tipo_servico": "Tipo de serviço prestado",
    "numero_viagem": "Número ou código da viagem",
    "capacidade": "Capacidade máxima (passageiros, etc.)",
    "ocupacao_percentual": "Percentual de ocupação",
    "data_manutencao": "Data em que foi realizada a manutenção",
    "estacao": "Nome ou código da estação",
    "codigo_estacao": "Código único da estação",
    "data_bilhetagem": "Data do registro de bilhetagem",
    "entrada_saida": "Tipo de passagem (entrada ou saída)",
    "quantidade_passageiros": "Quantidade de passageiros no registro",
    "valor_tarifa": "Valor da tarifa cobrada",
    "equipamento": "Identificação do equipamento",
    "nome_linha": "Nome da linha de transporte",
    "km_estacao": "Quilômetro da estação na linha",
    "horario_pico": "Indica se o registro é de horário de pico",
    "acessibilidade": "Indica se há acessibilidade",
    "integracao": "Informação de integração com outras linhas",
    "tag_id": "Identificador da tag (pedágio)",
    "placa": "Placa do veículo",
    "data_passagem": "Data e hora da passagem",
    "praca": "Praça ou cabine de pedágio",
    "categoria_veiculo": "Categoria do veículo para tarifação",
    "faixa": "Faixa de cobrança",
    "forma_pagamento": "Forma de pagamento utilizada",
    "contrato_cliente": "Número ou código do contrato do cliente",
    "km_praca": "Quilômetro em que a praça está localizada",
    "matricula": "Número de matrícula do funcionário",
    "nome": "Nome completo",
    "cargo": "Cargo ou função",
    "departamento": "Departamento ou área",
    "data_admissao": "Data de admissão do funcionário",
    "salario": "Valor do salário",
    "cpf": "CPF do titular",
    "email": "Endereço de e-mail",
    "data_nascimento": "Data de nascimento",
    "gestor": "Nome ou matrícula do gestor direto",
    "area": "Área ou setor",
    "tipo_contrato": "Tipo de vínculo contratual",
    "carga_horaria": "Carga horária em horas",
    "ordem_servico": "Número da ordem de serviço",
    "equipamento_id": "Identificador do equipamento",
    "data_abertura": "Data de abertura do registro",
    "data_fechamento": "Data de fechamento ou conclusão",
    "custo": "Valor do custo",
    "tipo_servico": "Tipo de serviço realizado",
    "fornecedor": "Nome do fornecedor",
    "prioridade": "Nível de prioridade",
    "status": "Status atual do registro",
    "descricao": "Descrição do item ou registro",
    "localizacao": "Localização física ou lógica",
    "horas_mao_obra": "Horas de mão de obra utilizadas",
    "pecas_trocadas": "Quantidade de peças trocadas",
    "conta": "Número ou código da conta",
    "valor": "Valor monetário",
    "data_lancamento": "Data do lançamento contábil",
    "tipo": "Tipo ou classificação",
    "centro_custo": "Centro de custo associado",
    "documento": "Número ou referência do documento",
    "contrapartida": "Conta ou registro de contrapartida",
    "projeto": "Código ou nome do projeto",
    "moeda": "Moeda do valor",
    "conciliado": "Indica se foi conciliado",
    "evento_id": "Identificador do evento",
    "tipo_evento": "Tipo do evento registrado",
    "data_evento": "Data e hora do evento",
    "turno": "Turno de trabalho ou operação",
    "producao": "Quantidade ou valor de produção",
    "equipe": "Identificação da equipe",
    "maquina": "Identificação da máquina ou equipamento",
    "quantidade": "Quantidade produzida ou processada",
    "unidade": "Unidade de medida",
    "patrimonio": "Número patrimonial do bem",
    "data_aquisicao": "Data de aquisição do bem",
    "depreciacao": "Valor da depreciação acumulada",
    "categoria": "Categoria de classificação",
    "numero_serie": "Número de série do equipamento",
    "vida_util_anos": "Vida útil em anos",
    "responsavel": "Responsável pelo bem ou processo",
    "cliente_id": "Identificador do cliente",
    "documento": "Número do documento (CPF/CNPJ)",
    "data_cadastro": "Data de cadastro do cliente",
    "contrato": "Número ou código do contrato",
    "consumo": "Valor ou volume de consumo",
    "telefone": "Número de telefone",
    "segmento": "Segmento do cliente",
    "endereco": "Endereço completo",
    "data_criacao": "Data e hora de criação do registro",
}


def _comment_for_column(name: str) -> str:
    """Comentário padrão a partir do nome da coluna (snake_case -> texto)."""
    if name in COLUMN_COMMENTS:
        return COLUMN_COMMENTS[name]
    # Fallback: "nome_coluna" -> "Nome coluna"
    return re.sub(r"_", " ", name).strip().capitalize() + "."


# Pools de colunas por catálogo (nome, tipo). Comentário é resolvido depois por nome.
COLUMN_POOLS: dict[str, List[Tuple[str, str]]] = {
    "motiva_rodovias": [
        ("id", "BIGINT"),
        ("concessionaria", "STRING"),
        ("rodovia", "STRING"),
        ("km_inicial", "DOUBLE"),
        ("km_final", "DOUBLE"),
        ("data_concessao", "DATE"),
        ("data_medicao", "DATE"),
        ("trafego_veiculos", "BIGINT"),
        ("trafego_pesados", "BIGINT"),
        ("tarifa_media", "DOUBLE"),
        ("valor_contrato", "DOUBLE"),
        ("trecho", "STRING"),
        ("sentido", "STRING"),
        ("pista", "STRING"),
        ("ano", "INT"),
        ("mes", "INT"),
        ("created_at", "TIMESTAMP"),
        ("updated_at", "TIMESTAMP"),
        ("ativo", "BOOLEAN"),
        ("observacao", "STRING"),
        ("codigo_br", "STRING"),
        ("extensao_km", "DOUBLE"),
        ("volume_diario", "BIGINT"),
    ],
    "motiva_trens": [
        ("id", "BIGINT"),
        ("linha", "STRING"),
        ("estacao_origem", "STRING"),
        ("estacao_destino", "STRING"),
        ("data_viagem", "DATE"),
        ("hora_partida", "TIMESTAMP"),
        ("hora_chegada", "TIMESTAMP"),
        ("vagao", "STRING"),
        ("composicao", "STRING"),
        ("passageiros", "INT"),
        ("km_percorridos", "DOUBLE"),
        ("atraso_minutos", "INT"),
        ("created_at", "TIMESTAMP"),
        ("operadora", "STRING"),
        ("tipo_servico", "STRING"),
        ("numero_viagem", "STRING"),
        ("capacidade", "INT"),
        ("ocupacao_percentual", "DOUBLE"),
        ("data_manutencao", "DATE"),
        ("observacao", "STRING"),
    ],
    "motiva_metro": [
        ("id", "BIGINT"),
        ("estacao", "STRING"),
        ("linha", "STRING"),
        ("codigo_estacao", "STRING"),
        ("data_bilhetagem", "DATE"),
        ("entrada_saida", "STRING"),
        ("quantidade_passageiros", "INT"),
        ("valor_tarifa", "DOUBLE"),
        ("equipamento", "STRING"),
        ("created_at", "TIMESTAMP"),
        ("nome_linha", "STRING"),
        ("km_estacao", "DOUBLE"),
        ("horario_pico", "BOOLEAN"),
        ("acessibilidade", "BOOLEAN"),
        ("integracao", "STRING"),
        ("observacao", "STRING"),
    ],
    "motiva_pedagios": [
        ("id", "BIGINT"),
        ("tag_id", "STRING"),
        ("placa", "STRING"),
        ("data_passagem", "TIMESTAMP"),
        ("praca", "STRING"),
        ("valor_tarifa", "DOUBLE"),
        ("concessionaria", "STRING"),
        ("categoria_veiculo", "STRING"),
        ("created_at", "TIMESTAMP"),
        ("faixa", "STRING"),
        ("forma_pagamento", "STRING"),
        ("contrato_cliente", "STRING"),
        ("km_praca", "DOUBLE"),
        ("observacao", "STRING"),
    ],
    "motiva_rh": [
        ("id", "BIGINT"),
        ("matricula", "STRING"),
        ("nome", "STRING"),
        ("cargo", "STRING"),
        ("departamento", "STRING"),
        ("data_admissao", "DATE"),
        ("salario", "DOUBLE"),
        ("cpf", "STRING"),
        ("email", "STRING"),
        ("data_nascimento", "DATE"),
        ("created_at", "TIMESTAMP"),
        ("gestor", "STRING"),
        ("area", "STRING"),
        ("tipo_contrato", "STRING"),
        ("carga_horaria", "INT"),
        ("ativo", "BOOLEAN"),
        ("observacao", "STRING"),
    ],
    "motiva_manutencao": [
        ("id", "BIGINT"),
        ("ordem_servico", "STRING"),
        ("equipamento_id", "STRING"),
        ("data_abertura", "DATE"),
        ("data_fechamento", "DATE"),
        ("custo", "DOUBLE"),
        ("tipo_servico", "STRING"),
        ("fornecedor", "STRING"),
        ("created_at", "TIMESTAMP"),
        ("prioridade", "STRING"),
        ("status", "STRING"),
        ("descricao", "STRING"),
        ("localizacao", "STRING"),
        ("horas_mao_obra", "DOUBLE"),
        ("pecas_trocadas", "INT"),
        ("observacao", "STRING"),
    ],
    "motiva_financeiro": [
        ("id", "BIGINT"),
        ("conta", "STRING"),
        ("descricao", "STRING"),
        ("valor", "DOUBLE"),
        ("data_lancamento", "DATE"),
        ("tipo", "STRING"),
        ("centro_custo", "STRING"),
        ("created_at", "TIMESTAMP"),
        ("documento", "STRING"),
        ("contrapartida", "STRING"),
        ("projeto", "STRING"),
        ("moeda", "STRING"),
        ("conciliado", "BOOLEAN"),
        ("observacao", "STRING"),
    ],
    "motiva_operacoes": [
        ("id", "BIGINT"),
        ("evento_id", "STRING"),
        ("tipo_evento", "STRING"),
        ("data_evento", "TIMESTAMP"),
        ("turno", "STRING"),
        ("producao", "DOUBLE"),
        ("created_at", "TIMESTAMP"),
        ("equipe", "STRING"),
        ("maquina", "STRING"),
        ("quantidade", "DOUBLE"),
        ("unidade", "STRING"),
        ("status", "STRING"),
        ("observacao", "STRING"),
    ],
    "motiva_ativos": [
        ("id", "BIGINT"),
        ("patrimonio", "STRING"),
        ("descricao", "STRING"),
        ("data_aquisicao", "DATE"),
        ("valor", "DOUBLE"),
        ("depreciacao", "DOUBLE"),
        ("localizacao", "STRING"),
        ("created_at", "TIMESTAMP"),
        ("categoria", "STRING"),
        ("fornecedor", "STRING"),
        ("numero_serie", "STRING"),
        ("vida_util_anos", "INT"),
        ("centro_custo", "STRING"),
        ("responsavel", "STRING"),
        ("observacao", "STRING"),
    ],
    "motiva_clientes": [
        ("id", "BIGINT"),
        ("cliente_id", "STRING"),
        ("nome", "STRING"),
        ("documento", "STRING"),
        ("data_cadastro", "DATE"),
        ("contrato", "STRING"),
        ("consumo", "DOUBLE"),
        ("created_at", "TIMESTAMP"),
        ("email", "STRING"),
        ("telefone", "STRING"),
        ("segmento", "STRING"),
        ("ativo", "BOOLEAN"),
        ("endereco", "STRING"),
        ("observacao", "STRING"),
    ],
}


def get_columns_for_table(catalog_name: str, schema_name: str, table_name: str) -> List[ColumnDef]:
    """
    Retorna entre 3 e 15 colunas (nome, tipo, comentário) para a tabela, de forma determinística.
    Usa o pool do catálogo; nomes e comentários fazem sentido para o domínio.
    """
    pool = COLUMN_POOLS.get(catalog_name)
    if not pool or len(pool) < MIN_COLUMNS:
        pool = [
            ("id", "BIGINT"),
            ("nome", "STRING"),
            ("valor", "DOUBLE"),
            ("data_criacao", "TIMESTAMP"),
            ("ativo", "BOOLEAN"),
            ("observacao", "STRING"),
        ]

    seed = hash((catalog_name, schema_name, table_name)) % (2**32)
    rng = random.Random(seed)
    n = rng.randint(MIN_COLUMNS, min(MAX_COLUMNS, len(pool)))
    chosen = rng.sample(pool, n)
    def order_key(c: Tuple[str, str]) -> int:
        return 0 if c[0] == "id" else 1
    chosen.sort(key=order_key)
    return [(name, dtype, _comment_for_column(name)) for name, dtype in chosen]


def get_table_comment(catalog_name: str, schema_name: str, table_name: str) -> str:
    """
    Gera um comentário em português para a tabela a partir do catálogo, schema e nome.
    """
    # Descrições curtas por prefixo de schema (quando não é "base")
    schema_hint = {
        "raw_": "dados brutos",
        "silver_": "dados tratados",
        "gold_": "dados agregados ou analíticos",
        "custos_": "custos",
        "incidentes": "incidentes",
        "concessionarias": "concessionárias",
        "tarifas": "tarifas",
        "treinamentos": "treinamentos",
        "beneficios": "benefícios",
        "contratos": "contratos",
        "historico": "histórico",
        "orcamento": "orçamento",
        "conciliacao": "conciliação",
        "dashboards": "dashboards",
        "alertas": "alertas",
        "localizacao": "localização",
        "documentos": "documentos",
        "suporte": "suporte",
        "preferencias": "preferências",
    }
    hint = "dados base"
    for prefix, desc in schema_hint.items():
        if schema_name.startswith(prefix) or schema_name == prefix.rstrip("_"):
            hint = desc
            break

    # Nome do domínio a partir do catálogo (motiva_rodovias -> rodovias)
    domain = catalog_name.replace("motiva_", "").replace("_", " ")
    # Ex.: "Tabela de dados tratados (silver) do domínio rodovias."
    return f"Tabela de {hint} do domínio {domain}."
