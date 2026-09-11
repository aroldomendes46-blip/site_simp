import json
import os

CAMINHO_CONFIG = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "servicos",
    "config.json",
)


def carregar_configuracoes():
    """Lê o arquivo JSON e retorna as configurações como um dicionário Python."""
    # Valores padrão de segurança (caso o arquivo seja apagado por erro)
    config_padrao = {
        "EMPRESA": {
            "nome": "BRASIL CONTROLE DE PRAGAS",
            "cnpj": "68.303.963/0001-06",
            "inscricao_municipal": "742628001",
            "cnae": "8129-0/00.99",
            "endereco": "RUA LORIS CORDOVIL, 92 - SALA: 02",
            "bairro": "Centro",
            "cep": "69043-010",
            "cidade_uf": "Manaus / AM",
            "telefone": "(92) 993028-1000 / (92)99221-1893 / (92) 99382-6233",
            "whatsapp": "5592992211893",
            "lat": "-3.0803046",
            "lng": "-60.0407661",
            "email": "contato@datasimp.com.br",
            "logo_path": "",
        },
        "EMPRESA_2": {
            "nome": "VILA DA BARRA SERVIÇOS",
            "razao_social": "VILA DA BARRA COMÉRCIO REPRESENTAÇÃO SERVIÇOS DE DEDETIZAÇÃO LTDA.",
            "nome_fantasia": "VILA DA BARRA SERVIÇOS",
            "cnpj": "00.492.578/0001-02",
            "inscricao_municipal": "69.952.01",
            "endereco": "Rua. Canário",
            "numero": "27",
            "bairro": "Quadra 52 - Cond. Cidade Nova I",
            "cidade_uf": "Manaus / AM",
            "telefone": "(92) 99170-9310",
            "whatsapp": "5592991709310",
            "lat": "-3.0274425",
            "lng": "-59.9830799",
            "logo_path": "",
            "registro_dvisa": "S1321",
        },
        "DESIGN_PDF": {
            "cor_linhas": "#1F2937",
            "espessura_linhas": 0.8,
            "cor_titulo_barra": "#1E3A8A",
            "cor_secao_barra": "#374151",
        },
        "ASSINATURA": {
            "responsavel": "RESPONSÁVEL TÉCNICO",
            "cargo": "Proponente / Responsável",
            "local": "Manaus / AM",
        },
        "PERFIL_LOJA": {
            "nome_loja": "",
            "banco": "",
            "mostrar_ocultos": False,
            "perfis": {
                "loja1_controle_pragas": {
                    "ativo": True,
                    "nome": "Controle de Pragas",
                    "cor": "#00B37E",
                    "banco": "datasimp.db",
                    "ocultos": [],
                },
                "loja2_moto_pecas": {
                    "ativo": False,
                    "nome": "Moto Peças",
                    "cor": "#3B82F6",
                    "banco": "moto_pecas.db",
                    "ocultos": ["rotas", "vencimentos"],
                },
                "loja3_vila_da_barra": {
                    "ativo": False,
                    "nome": "Vila da Barra",
                    "cor": "#9C9C9C",
                    "banco": "vila_da_barra.db",
                    "empresa_config": "EMPRESA_2",
                    "ocultos": ["rotas", "vencimentos"],
                },
                "loja4_roupas": {
                    "ativo": False,
                    "nome": "Roupas",
                    "cor": "#8B5CF6",
                    "banco": "roupas.db",
                    "ocultos": ["rotas", "vencimentos"],
                },
                "loja5_brinquedos": {
                    "ativo": False,
                    "nome": "Brinquedos",
                    "cor": "#F59E0B",
                    "banco": "brinquedos.db",
                    "ocultos": ["rotas", "vencimentos"],
                },
            },
        },
    }

    if not os.path.exists(CAMINHO_CONFIG):
        # Se o arquivo não existir, cria um padrão para o sistema não quebrar
        with open(CAMINHO_CONFIG, "w", encoding="utf-8") as f:
            json.dump(config_padrao, f, indent=4, ensure_ascii=False)
        return config_padrao

    try:
        with open(CAMINHO_CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return config_padrao


def salvar_configuracoes(config):
    """Persiste as configurações no arquivo config.json."""
    try:
        with open(CAMINHO_CONFIG, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False


def carregar_assinatura():
    """Retorna o bloco ASSINATURA (nome/cargo/local do responsável)."""
    config = carregar_configuracoes()
    assin = config.get("ASSINATURA", {})
    if not isinstance(assin, dict):
        assin = {}
    padrao = {
        "responsavel": "RESPONSÁVEL TÉCNICO",
        "cargo": "Proponente / Responsável",
        "local": "Manaus / AM",
    }
    for chave, valor in padrao.items():
        assin.setdefault(chave, valor)
    return {
        "responsavel": str(assin.get("responsavel", "") or ""),
        "cargo": str(assin.get("cargo", "") or ""),
        "local": str(assin.get("local", "") or ""),
        "caminho_imagem": assin.get("caminho_imagem", "") or buscar_caminho_assinatura(),
    }


def salvar_assinatura(responsavel="", cargo="", local="", caminho_imagem=""):
    """Salva o bloco ASSINATURA no config.json."""
    config = carregar_configuracoes()
    config["ASSINATURA"] = {
        "responsavel": str(responsavel),
        "cargo": str(cargo),
        "local": str(local),
        "caminho_imagem": str(caminho_imagem) or buscar_caminho_assinatura(),
    }
    return salvar_configuracoes(config)


def buscar_caminho_assinatura():
    """Localiza a imagem da assinatura (assinatura_orçamento.jpg/png).

    Prioriza o caminho configurado em ASSINATURA.caminho_imagem; se não
    existir, procura na pasta fotos/ ao lado do sistema.
    """
    try:
        config = carregar_configuracoes()
        assin = config.get("ASSINATURA", {}) or {}
        caminho_cfg = assin.get("caminho_imagem", "")
        if caminho_cfg and os.path.exists(str(caminho_cfg)):
            return str(caminho_cfg)
    except Exception:
        pass

    base = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "fotos",
    )
    for ext in ("jpg", "jpeg", "png"):
        candidato = os.path.join(base, f"assinatura_orçamento.{ext}")
        if os.path.exists(candidato):
            return candidato
    return ""


def preparar_assinatura_limpa(caminho_origem):
    """Remove o fundo da imagem da assinatura e a deixa sobre fundo branco.

    Retorna o caminho da imagem já limpa (pronta para ser embutida no PDF),
    ou o caminho original se o processamento falhar.
    """
    if not caminho_origem or not os.path.exists(str(caminho_origem)):
        return ""
    caminho_origem = str(caminho_origem)
    pasta = os.path.dirname(caminho_origem)
    cache = os.path.join(pasta, "assinatura_orçamento_limpa.png")
    try:
        # Reaproveita a limpeza anterior se a imagem original não mudou
        if os.path.exists(cache) and os.path.getmtime(
            cache
        ) >= os.path.getmtime(caminho_origem):
            return cache

        from PIL import Image

        im = Image.open(caminho_origem).convert("RGBA")
        w, h = im.size
        px = im.load()

        # 1) Estima a cor de fundo (mediana da borda)
        borda = []
        for x in range(w):
            borda.append(px[x, 0][:3])
            borda.append(px[x, h - 1][:3])
        for y in range(h):
            borda.append(px[0, y][:3])
            borda.append(px[w - 1, y][:3])
        borda.sort()
        bg = borda[len(borda) // 2]

        # 2) Fundo -> transparente (com transição suave nas bordas)
        t_lo, t_hi = 14.0, 40.0

        def _dist(a, b):
            return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5

        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                d = _dist((r, g, b), bg)
                if d <= t_lo:
                    a = 0
                elif d >= t_hi:
                    a = 255
                else:
                    a = int(255 * (d - t_lo) / (t_hi - t_lo))
                px[x, y] = (r, g, b, a)

        # 3) Compõe sobre fundo branco (o PDF é branco; o ReportLab desta
        #    versão não lê alpha de PNG por caminho de arquivo)
        fundo_branco = Image.new("RGBA", im.size, (255, 255, 255, 255))
        limpa = Image.alpha_composite(fundo_branco, im).convert("RGB")
        limpa.save(cache)
        return cache
    except Exception:
        return caminho_origem


def carregar_dados_empresa():
    """Retorna os dados da empresa correta conforme o perfil ativo.

    Cada perfil pode ter um campo 'empresa_config' que indica qual chave
    ler do config.json (ex: 'EMPRESA', 'EMPRESA_2'). Se não tiver, usa
    'EMPRESA' por padrão.
    """
    config = carregar_configuracoes()

    # Descobre qual perfil está ativo
    perfil_ativo = "loja1_controle_pragas"
    perfis_cfg = config.get("PERFIL_LOJA", {}).get("perfis", {})
    for pid, dados in perfis_cfg.items():
        if dados.get("ativo"):
            perfil_ativo = pid
            break

    # Lê a chave da empresa do perfil (padrão: "EMPRESA")
    perfil_padroes = {
        "loja1_controle_pragas": {},
        "loja2_moto_pecas": {},
        "loja3_vila_da_barra": {"empresa_config": "EMPRESA_2"},
        "loja4_roupas": {},
        "loja5_brinquedos": {},
        "loja6_nova": {"empresa_config": "EMPRESA_3"},
    }
    defaults = perfil_padroes.get(perfil_ativo, {})
    empresa_chave = perfis_cfg.get(perfil_ativo, {}).get(
        "empresa_config", defaults.get("empresa_config", "EMPRESA")
    )

    empresa = config.get(empresa_chave, config.get("EMPRESA", {}))
    if not empresa:
        empresa = config.get("EMPRESA", {})
    empresa = dict(empresa)

    # Resolve o logo_path para a pasta logo/ real da instalação (quando o
    # caminho absoluto do desenvolvedor não existir na máquina alvo).
    if "logo_path" in empresa:
        try:
            from servicos.caminhos import resolver_logo

            empresa["logo_path"] = resolver_logo(empresa.get("logo_path"))
        except Exception:
            pass
    return empresa
