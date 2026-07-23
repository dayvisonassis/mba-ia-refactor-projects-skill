"""Service de Pedido — regra de negócio movida para fora da camada de dados (T5 / AP-05)
e envolvida em transação explícita (AP-12). Notificação delegada ao service dedicado.
"""
from src.database.connection import get_db
from src.models import pedido_model
from src.services import notification_service
from src.services.errors import ValidationError


def criar_pedido(usuario_id, itens):
    db = get_db()

    # Regra de negócio: validação de estoque e cálculo do total.
    total = 0
    validados = []
    for item in itens:
        produto = pedido_model.get_produto(item["produto_id"])
        if produto is None:
            raise ValidationError(f"Produto {item['produto_id']} não encontrado")
        if produto["estoque"] < item["quantidade"]:
            raise ValidationError(f"Estoque insuficiente para {produto['nome']}")
        total += produto["preco"] * item["quantidade"]
        validados.append((item, produto))

    # Persistência transacional: ou tudo é gravado, ou nada (rollback).
    try:
        pedido_id = pedido_model.inserir_pedido(usuario_id, total)
        for item, produto in validados:
            pedido_model.inserir_item(pedido_id, item["produto_id"], item["quantidade"], produto["preco"])
            pedido_model.baixar_estoque(item["produto_id"], item["quantidade"])
        db.commit()
    except Exception:
        db.rollback()
        raise

    notification_service.pedido_criado(pedido_id, usuario_id)
    return {"pedido_id": pedido_id, "total": total}


def listar_pedidos_usuario(usuario_id):
    return pedido_model.listar(usuario_id)


def listar_todos():
    return pedido_model.listar()


def atualizar_status(pedido_id, novo_status):
    pedido_model.atualizar_status(pedido_id, novo_status)
    notification_service.status_alterado(pedido_id, novo_status)
    return True
