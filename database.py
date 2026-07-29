import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "vendas.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            categoria_id INTEGER,
            descricao TEXT,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comandas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            mesa INTEGER,
            criada_em TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'aberta',
            total REAL DEFAULT 0.0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_comanda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comanda_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            produto_nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL DEFAULT 1,
            preco_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (comanda_id) REFERENCES comandas(id),
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    """)

    if cursor.execute("SELECT COUNT(*) FROM categorias").fetchone()[0] == 0:
        categorias = ["Bebidas", "Lanches", "Pratos", "Sobremesas"]
        for cat in categorias:
            cursor.execute("INSERT INTO categorias (nome) VALUES (?)", (cat,))

    conn.commit()
    conn.close()


def listar_categorias():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM categorias ORDER BY nome").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def adicionar_produto(nome, preco, categoria_id, descricao=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO produtos (nome, preco, categoria_id, descricao) VALUES (?, ?, ?, ?)",
        (nome, preco, categoria_id, descricao),
    )
    conn.commit()
    conn.close()


def listar_produtos(categoria_id=None):
    conn = get_connection()
    if categoria_id:
        rows = conn.execute(
            """SELECT p.*, c.nome as categoria_nome
               FROM produtos p JOIN categorias c ON p.categoria_id = c.id
               WHERE p.categoria_id = ? ORDER BY p.nome""",
            (categoria_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT p.*, c.nome as categoria_nome
               FROM produtos p JOIN categorias c ON p.categoria_id = c.id
               ORDER BY p.nome"""
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def atualizar_produto(produto_id, nome, preco, categoria_id, descricao=""):
    conn = get_connection()
    conn.execute(
        "UPDATE produtos SET nome=?, preco=?, categoria_id=?, descricao=? WHERE id=?",
        (nome, preco, categoria_id, descricao, produto_id),
    )
    conn.commit()
    conn.close()


def remover_produto(produto_id):
    conn = get_connection()
    conn.execute("DELETE FROM produtos WHERE id=?", (produto_id,))
    conn.commit()
    conn.close()


def criar_comanda(cliente, mesa=0):
    conn = get_connection()
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    cursor = conn.execute(
        "INSERT INTO comandas (cliente, mesa, criada_em, status) VALUES (?, ?, ?, 'aberta')",
        (cliente, mesa, agora),
    )
    comanda_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return comanda_id


def listar_comandas_abertas():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM comandas WHERE status='aberta' ORDER BY criada_em DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def listar_comandas_fechadas():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM comandas WHERE status='fechada' ORDER BY criada_em DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def adicionar_item(comanda_id, produto_id, produto_nome, quantidade, preco_unitario):
    conn = get_connection()
    subtotal = quantidade * preco_unitario
    conn.execute(
        "INSERT INTO itens_comanda (comanda_id, produto_id, produto_nome, quantidade, preco_unitario, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
        (comanda_id, produto_id, produto_nome, quantidade, preco_unitario, subtotal),
    )
    conn.execute(
        "UPDATE comandas SET total = (SELECT COALESCE(SUM(subtotal), 0) FROM itens_comanda WHERE comanda_id=?) WHERE id=?",
        (comanda_id, comanda_id),
    )
    conn.commit()
    conn.close()


def listar_itens(comanda_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM itens_comanda WHERE comanda_id=? ORDER BY id",
        (comanda_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fechar_comanda(comanda_id):
    conn = get_connection()
    conn.execute(
        "UPDATE comandas SET status='fechada' WHERE id=?", (comanda_id,)
    )
    conn.commit()
    conn.close()


def remover_item(item_id, comanda_id):
    conn = get_connection()
    conn.execute("DELETE FROM itens_comanda WHERE id=?", (item_id,))
    conn.execute(
        "UPDATE comandas SET total = (SELECT COALESCE(SUM(subtotal), 0) FROM itens_comanda WHERE comanda_id=?) WHERE id=?",
        (comanda_id, comanda_id),
    )
    conn.commit()
    conn.close()
