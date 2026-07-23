"""Service de Health — status da aplicação SEM vazar segredos (T2 / AP-02).

A antiga rota /health retornava a SECRET_KEY e flags de ambiente. Aqui devolve
apenas status e contagens.
"""
from src.database.connection import get_db


def status():
    db = get_db()

    def contar(tabela):
        return db.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]

    return {
        "status": "ok",
        "database": "connected",
        "counts": {
            "produtos": contar("produtos"),
            "usuarios": contar("usuarios"),
            "pedidos": contar("pedidos"),
        },
        "versao": "1.0.0",
    }
