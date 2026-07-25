"""Model de Usuário — queries parametrizadas (T1) e senha nunca serializada (T3 / AP-03).

`get_todos`/`get_por_id` retornam apenas campos públicos (sem o campo `senha`).
`get_por_email` devolve a linha completa para uso interno de autenticação.
"""
from src.database.connection import get_db

CAMPOS_PUBLICOS = ("id", "nome", "email", "tipo", "criado_em")


def _publico(row):
    return {campo: row[campo] for campo in CAMPOS_PUBLICOS}


def get_todos():
    db = get_db()
    rows = db.execute("SELECT * FROM usuarios").fetchall()
    return [_publico(r) for r in rows]


def get_por_id(usuario_id):
    db = get_db()
    row = db.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    return _publico(row) if row else None


def get_por_email(email):
    """Uso interno (autenticação) — inclui o hash da senha. Nunca exposto em rota."""
    db = get_db()
    return db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()


def criar(nome, email, senha_hash, tipo="cliente"):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    db.commit()
    return cursor.lastrowid
