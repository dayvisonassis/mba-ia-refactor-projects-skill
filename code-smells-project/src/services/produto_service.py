"""Service de Produto — regra de negócio e validação única (T9 / AP-09)."""
from src.config.constants import CATEGORIAS_VALIDAS, NOME_MAX_LEN, NOME_MIN_LEN
from src.models import produto_model
from src.services.errors import ValidationError


def validar_produto(dados):
    """Validador único, reutilizado por criar e atualizar (elimina duplicação)."""
    if not dados:
        raise ValidationError("Dados inválidos")
    for campo in ("nome", "preco", "estoque"):
        if campo not in dados:
            raise ValidationError(f"{campo.capitalize()} é obrigatório")

    nome = dados["nome"]
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if not (NOME_MIN_LEN <= len(nome) <= NOME_MAX_LEN):
        raise ValidationError(f"Nome deve ter entre {NOME_MIN_LEN} e {NOME_MAX_LEN} caracteres")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValidationError(f"Categoria inválida. Válidas: {CATEGORIAS_VALIDAS}")

    return {
        "nome": nome,
        "descricao": dados.get("descricao", ""),
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }


def listar():
    return produto_model.get_todos()


def obter(produto_id):
    return produto_model.get_por_id(produto_id)


def buscar(termo, categoria=None, preco_min=None, preco_max=None):
    return produto_model.buscar(termo, categoria, preco_min, preco_max)


def criar(dados_validados):
    return produto_model.criar(
        dados_validados["nome"],
        dados_validados["descricao"],
        dados_validados["preco"],
        dados_validados["estoque"],
        dados_validados["categoria"],
    )


def atualizar(produto_id, dados_validados):
    return produto_model.atualizar(
        produto_id,
        dados_validados["nome"],
        dados_validados["descricao"],
        dados_validados["preco"],
        dados_validados["estoque"],
        dados_validados["categoria"],
    )


def deletar(produto_id):
    return produto_model.deletar(produto_id)
