# -*- coding: utf-8 -*-
"""Perfis de loja do SIMP (sistema camaleão).

Um único instalador atende vários segmentos. O config.json define qual perfil
está ativo; o menu principal mostra apenas os módulos do perfil e os demais
ficam ocultos (preservados) até que o perfil seja trocado.

Chaves de PERFIS:
  nome            -> título usado no menu/barra
  cor             -> cor de destaque (botão Início)
  banco           -> arquivo .db individual desta loja (padrão do perfil)
  ocultos         -> ids de módulos que ficam escondidos neste perfil

O arquivo de banco pode ser sobrescrito no config.json
(PERFIL_LOJA.banco), que sempre vence o padrão do perfil.
"""

import os
import json

CAMINHO_CONFIG = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "servicos",
    "config.json",
)

# Ids de todos os módulos possíveis
TODOS_MODULOS = [
    "inicio",
    "clientes",
    "funcionarios",
    "produtos",
    "os_por_cliente",
    "orcamentos",
    "documentos",
    "rotas",
    "vencimentos",
    "financeiro",
    "estoque",
    "porta_iscas",
    "agenda",
    "site",
    "manual",
    "suporte",
    # Módulos exclusivos Moto Peças (loja2)
    "mp_caixa",
    "mp_compras",
    "mp_funcionarios",
    "mp_vendedores",
    "mp_orcamentos",
    "mp_financeiro",
    "mp_relatorios",
]

# Módulos MP que ficam ocultos em perfis que NÃO são loja2
_MP_OCULTOS = [
    "mp_caixa",
    "mp_compras",
    "mp_funcionarios",
    "mp_vendedores",
    "mp_orcamentos",
    "mp_financeiro",
    "mp_relatorios",
]

# Cor padrão da barra de cabeçalho das telas de O.S. (cada perfil pode
# definir a sua; loja da Vila da Barra usa a cor do logo dela).
COR_OS_PADRAO = "#1E3A8A"

PERFIS = {
    # Perfil padrão (loja 1) - Controle de Pragas (Brasil Imunizadora)
    "loja1_controle_pragas": {
        "nome": "Controle de Pragas",
        "cor": "#00B37E",
        "banco": "datasimp.db",
        "ocultos": list(_MP_OCULTOS),
    },
    "loja2_moto_pecas": {
        "nome": "Moto Peças",
        "cor": "#3B82F6",
        "banco": "moto_pecas.db",
        "ocultos": ["rotas", "vencimentos", "agenda", "site"],
    },
    "loja3_vila_da_barra": {
        "nome": "Vila da Barra",
        "cor": "#9C9C9C",
        "banco": "vila_da_barra.db",
        "empresa_config": "EMPRESA_2",
        "cor_os": "#9C9C9C",
        "ocultos": ["rotas", "vencimentos"] + list(_MP_OCULTOS),
    },
    "loja4_roupas": {
        "nome": "Roupas",
        "cor": "#8B5CF6",
        "banco": "roupas.db",
        "ocultos": ["rotas", "vencimentos", "site"] + list(_MP_OCULTOS),
    },
    "loja5_brinquedos": {
        "nome": "Brinquedos",
        "cor": "#F59E0B",
        "banco": "brinquedos.db",
        "ocultos": ["rotas", "vencimentos", "site"] + list(_MP_OCULTOS),
    },
    "loja6_nova": {
        "nome": "Nova Loja",
        "cor": "#EC4899",
        "banco": "nova_loja.db",
        "empresa_config": "EMPRESA_3",
        "ocultos": [],
    },
}


def carregar_config_perfil():
    """Lê o bloco PERFIL_LOJA do config.json (com padrão seguro).

    Cada perfil vem pronto no config.json com a chave "ativo": true/false.
    Para trocar de loja basta ligar uma e desligar a outra - sem digitar.
    """
    try:
        with open(CAMINHO_CONFIG, "r", encoding="utf-8") as f:
            config = json.load(f)
        perfil = config.get("PERFIL_LOJA", {}) or {}
    except Exception:
        perfil = {}
    return {
        "nome_loja": str(perfil.get("nome_loja", "") or ""),
        "banco": str(perfil.get("banco", "") or ""),
        "mostrar_ocultos": bool(perfil.get("mostrar_ocultos", False)),
        "perfis": perfil.get("perfis", {}) or {},
    }


def obter_perfil():
    """Retorna o perfil ativo resolvido (nome, cor, banco, módulos ocultos).

    O perfil ativo é o primeiro com "ativo": true no config.json.
    Padrão de segurança: loja 1 se nenhum estiver ligado.
    """
    cfg = carregar_config_perfil()

    # Combina os perfis do config.json com os padrões do sistema
    perfis = {}
    for pid, dados in PERFIS.items():
        item = dict(dados)
        item.update(cfg["perfis"].get(pid, {}) or {})
        perfis[pid] = item

    # Descobre qual perfil está com "ativo": true
    ativo = None
    for pid, dados in perfis.items():
        if dados.get("ativo"):
            ativo = pid
            break
    if ativo is None or ativo not in perfis:
        ativo = "loja1_controle_pragas"

    dados = perfis[ativo]

    # Nome da loja configurado prevalece sobre o nome genérico do perfil
    nome = cfg["nome_loja"] or dados["nome"]

    ocultos = list(dados.get("ocultos", []) or [])
    # Em loja de teste: opção de exibir todos os módulos mesmo assim
    if cfg["mostrar_ocultos"]:
        ocultos = []

    # Banco individual: config.json vence o padrão do perfil
    banco = cfg["banco"] or dados.get("banco", "")

    return {
        "id": ativo,
        "nome": nome,
        "cor": dados["cor"],
        "banco": banco,
        "ocultos": ocultos,
        "cor_os": dados.get("cor_os", COR_OS_PADRAO),
        "empresa_config": dados.get("empresa_config", "EMPRESA"),
    }


def modulos_visiveis(todos_modulos):
    """Filtra a lista de módulos (tuplas com id no último item) pelo perfil."""
    perfil = obter_perfil()
    if not perfil["ocultos"]:
        return todos_modulos
    return [m for m in todos_modulos if m[0] not in perfil["ocultos"]]


def obter_cor_os():
    """Retorna a cor da barra de cabeçalho das telas de O.S. conforme o perfil ativo."""
    return obter_perfil().get("cor_os", COR_OS_PADRAO)


def cor_texto_sobre(cor_hex, claro="white", escuro="black"):
    """Escolhe a cor de texto legível sobre um fundo (barra de cabeçalho).

    Fundo claro -> texto escuro; fundo escuro -> texto claro.
    Retorna o literal (padrão: 'white'/'black''), chamador converte conforme o canvas.
    """
    try:
        h = cor_hex.lstrip("#")
        r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
        luminancia = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return escuro if luminancia > 0.55 else claro
    except Exception:
        return claro
