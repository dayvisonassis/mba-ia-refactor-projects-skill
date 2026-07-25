"""Model de Produto — acesso a dados com queries parametrizadas (T1 / AP-01).

Camada de dados: apenas persiste/consulta. Nenhuma regra de negócio aqui.
"""
from src.database.connection import get_db


def _to_dict(row):
    return {k: row[k] for k in row.keys()}


def get_todos():
    db = get_db()
    rows = db.execute("SELECT * FROM produtos").fetchall()
    return [_to_dict(r) for r in rows]


def get_por_id(produto_id):
    db = get_db()
    row = db.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    return _to_dict(row) if row else None


def criar(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    db.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    db.commit()
    return True


def deletar(produto_id):
    db = get_db()
    db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    db.commit()
    return True


def buscar(termo, categoria=None, preco_min=None, preco_max=None):
    db = get_db()
    query = "SELECT * FROM produtos WHERE 1=1"
    params = []
    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        params += [f"%{termo}%", f"%{termo}%"]
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        query += " AND preco <= ?"
        params.append(preco_max)
    rows = db.execute(query, params).fetchall()
    return [_to_dict(r) for r in rows]
