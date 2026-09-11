import os
import re
import shutil
import sys
from urllib.parse import quote

from flask import Flask, render_template

BASE_SISTEMA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_SISTEMA not in sys.path:
    sys.path.insert(0, BASE_SISTEMA)

from servicos.gerenciador_config import carregar_dados_empresa  # noqa: E402
from servicos.perfil_loja import obter_perfil  # noqa: E402

app = Flask(__name__)

PASTA_LOGO_STATIC = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "static", "imagens"
)


def _wa(whatsapp, mensagem):
    """Monta link do WhatsApp com número e mensagem codificada."""
    num = "".join(d for d in str(whatsapp or "") if d.isdigit())
    if not num:
        num = "5592992211893"
    return f"https://wa.me/{num}?text={quote(mensagem)}"


# Logo do site por perfil de loja (arquivos na pasta logo/ do sistema)
LOGOS_PERFIL = {
    "loja1_controle_pragas": "logo_site.jpg",
    "loja3_vila_da_barra": "logo_vila.png",
}


def _montar_contexto():
    """Reúne os dados do site conforme a empresa do perfil ativo."""
    empresa = carregar_dados_empresa()
    nome = (empresa.get("nome") or "").strip()
    if not nome:
        nome = "BRASIL CONTROLE DE PRAGAS"

    cidade_uf = (empresa.get("cidade_uf") or "Manaus / AM").strip()
    cidade = re.sub(r"\s*/\s*", "-", cidade_uf).strip()
    if not cidade:
        cidade = "Manaus-AM"
    cd = cidade.split("-")[0].strip() or "Sua cidade"
    uf = cidade.split("-")[-1].strip() or ""

    telefone = ""
    telefones = str(empresa.get("telefone") or "").strip()
    if telefones:
        partes = [p.strip() for p in telefones.split("/") if p.strip()]
        telefone = " • ".join(partes) if len(partes) > 1 else telefones

    wa = str(empresa.get("whatsapp") or "5592992211893").strip()

    msg_geral = (
        f"Olá! Vim pelo site da {nome} e gostaria de solicitar um "
        "orçamento de controle de pragas."
    )
    msg_contato = f"Olá! Vim pelo site da {nome}."

    servicos = [
        {"emoji": "🐀", "nome": "Controle de Ratos",
         "desc": "Desratização segura e planejada para residências, empresas e depósitos.",
         "msg": "Tenho interesse no controle de ratos.", "img": ""},
        {"emoji": "🪳", "nome": "Controle de Baratas",
         "desc": "Tratamento para eliminar baratas e reduzir o risco de novas infestações.",
         "msg": "Tenho interesse no controle de baratas.", "img": "barata_site.svg"},
        {"emoji": "🐜", "nome": "Controle de Formigas",
         "desc": "Combate a formigueiros e infestações persistentes em todo tipo de ambiente.",
         "msg": "Tenho interesse no controle de formigas.", "img": ""},
        {"emoji": "🪵", "nome": "Controle de Cupins",
         "desc": "Proteção de móveis, madeiras e estruturas contra cupins.",
         "msg": "Tenho interesse no controle de cupins.", "img": "cupins_site.svg"},
        {"emoji": "🦂", "nome": "Controle de Escorpiões",
         "desc": "Proteção especializada contra escorpiões urbanos.",
         "msg": "Tenho interesse no controle de escorpiões.", "img": "escorpiao_site.svg"},
        {"emoji": "🦟", "nome": "Controle de Mosquitos",
         "desc": "Combate ao Aedes aegypti e outros mosquitos vetores.",
         "msg": "Tenho interesse no controle de mosquitos.", "img": "mosquito_site.svg"},
        {"emoji": "🕷️", "nome": "Controle de Aranhas",
         "desc": "Tratamento para reduzir a presença de aranhas no ambiente.",
         "msg": "Tenho interesse no controle de aranhas.", "img": ""},
        {"emoji": "🕊️", "nome": "Controle de Pombos",
         "desc": "Manejo ético e afugentamento de aves urbanas.",
         "msg": "Tenho interesse no controle de pombos.", "img": ""},
    ]

    logo_origem = ""
    logo_usada = False
    perfil = obter_perfil()
    nome_logo = LOGOS_PERFIL.get(perfil.get("id"))
    if nome_logo:
        logo_padrao = os.path.join(BASE_SISTEMA, "logo", nome_logo)
        if os.path.exists(logo_padrao):
            logo_origem = logo_padrao
            logo_usada = True
    if not logo_usada:
        logo_cfg = (empresa.get("logo_path") or "").strip()
        if logo_cfg and os.path.exists(logo_cfg):
            logo_origem = logo_cfg
            logo_usada = True
    if logo_usada:
        shutil.copy2(logo_origem, os.path.join(PASTA_LOGO_STATIC, "logo_site.png"))

    slider_dir = os.path.join(BASE_SISTEMA, "logo", "imagem_site")
    slider_imgs = []
    if os.path.isdir(slider_dir):
        for arq in sorted(os.listdir(slider_dir)):
            if arq.lower().endswith((".jpg", ".jpeg", ".png")):
                shutil.copy2(
                    os.path.join(slider_dir, arq),
                    os.path.join(PASTA_LOGO_STATIC, "slider", arq),
                )
                slider_imgs.append(arq)

    iniciais = "".join(
        [p[0] for p in nome.split() if p and p[0].isalpha()][:2]
    ).upper() or "CP"

    return {
        "empresa": nome,
        "cidade": cidade,
        "cd": cidade.split("-")[0].strip(),
        "uf": cidade.split("-")[-1].strip(),
        "telefone": telefone,
        "email": (empresa.get("email") or "").strip(),
        "endereco": (empresa.get("endereco") or "").strip(),
        "bairro": (empresa.get("bairro") or "").strip(),
        "lat": (empresa.get("lat") or "-3.0803046").strip(),
        "lng": (empresa.get("lng") or "-60.0407661").strip(),
        "wa_geral": _wa(wa, msg_geral),
        "wa_contato": _wa(wa, msg_contato),
        "servicos": [
            {"emoji": s["emoji"], "nome": s["nome"], "desc": s["desc"],
             "link": _wa(wa, s["msg"]), "img": s.get("img", "")}
            for s in servicos
        ],
        "has_logo": logo_usada,
        "iniciais": iniciais,
        "slider_imgs": slider_imgs,
    }


@app.route("/")
def home():
    return render_template("index.html", **_montar_contexto())


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False, port=5050)