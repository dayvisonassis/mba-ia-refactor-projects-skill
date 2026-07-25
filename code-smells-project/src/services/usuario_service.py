"""Service de Usuário — hashing de senha e autenticação (T3 / AP-03)."""
from werkzeug.security import check_password_hash, generate_password_hash

from src.models import usuario_model
from src.services.errors import ValidationError


def listar():
    return usuario_model.get_todos()


def obter(usuario_id):
    return usuario_model.get_por_id(usuario_id)


def criar(nome, email, senha):
    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    senha_hash = generate_password_hash(senha)
    return usuario_model.criar(nome, email, senha_hash)


def autenticar(email, senha):
    """Compara a senha com o hash armazenado; retorna dados públicos ou None."""
    row = usuario_model.get_por_email(email)
    if row and check_password_hash(row["senha"], senha):
        return {"id": row["id"], "nome": row["nome"], "email": row["email"], "tipo": row["tipo"]}
    return None
