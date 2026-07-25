"""Model de Pedido — queries parametrizadas (T1) e listagem sem N+1 (T8 / AP-08).

Os helpers de escrita (inserir_pedido/inserir_item/baixar_estoque) NÃO fazem commit:
a transação é controlada pela camada de service (T5 / AP-12).
"""
from src.database.connection import get_db


def get_produto(produto_id):
    db = get_db()
    return db.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()


def inserir_pedido(usuario_id, total):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total),
    )
    return cursor.lastrowid


def inserir_item(pedido_id, produto_id, quantidade, preco_unitario):
    db = get_db()
    db.execute(
        "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
        (pedido_id, produto_id, quantidade, preco_unitario),
    )


def baixar_estoque(produto_id, quantidade):
    db = get_db()
    db.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", (quantidade, produto_id))


def atualizar_status(pedido_id, novo_status):
    db = get_db()
    db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()
    return True


def listar(usuario_id=None):
    """Lista pedidos com seus itens usando 2 queries no total (sem N+1)."""
    db = get_db()
    if usuario_id is not None:
        pedidos = db.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,)).fetchall()
    else:
        pedidos = db.execute("SELECT * FROM pedidos").fetchall()

    if not pedidos:
        return []

    ids = [p["id"] for p in pedidos]
    placeholders = ",".join("?" * len(ids))
    itens = db.execute(
        f"""SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario,
                   pr.nome AS produto_nome
            FROM itens_pedido ip
            LEFT JOIN produtos pr ON pr.id = ip.produto_id
            WHERE ip.pedido_id IN ({placeholders})""",
        ids,
    ).fetchall()

    itens_por_pedido = {}
    for item in itens:
        itens_por_pedido.setdefault(item["pedido_id"], []).append({
            "produto_id": item["produto_id"],
            "produto_nome": item["produto_nome"] or "Desconhecido",
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
        })

    return [{
        "id": p["id"],
        "usuario_id": p["usuario_id"],
        "status": p["status"],
        "total": p["total"],
        "criado_em": p["criado_em"],
        "itens": itens_por_pedido.get(p["id"], []),
    } for p in pedidos]


def metricas_vendas():
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    faturamento = db.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos").fetchone()[0]
    por_status = {}
    for row in db.execute("SELECT status, COUNT(*) AS c FROM pedidos GROUP BY status").fetchall():
        por_status[row["status"]] = row["c"]
    return {"total_pedidos": total, "faturamento": faturamento, "por_status": por_status}
