"""Controller de Pedido — orquestra o request; regra/transação ficam no service."""
from flask import jsonify, request

from src.config.constants import STATUS_VALIDOS
from src.services import pedido_service
from src.services.errors import ValidationError


def criar_pedido():
    dados = request.get_json() or {}
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        return jsonify({"erro": "Usuario ID é obrigatório"}), 400
    if not itens:
        return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400

    try:
        resultado = pedido_service.criar_pedido(usuario_id, itens)
    except ValidationError as e:
        return jsonify({"erro": str(e), "sucesso": False}), 400

    return jsonify({
        "dados": resultado,
        "sucesso": True,
        "mensagem": "Pedido criado com sucesso",
    }), 201


def listar_pedidos_usuario(usuario_id):
    return jsonify({"dados": pedido_service.listar_pedidos_usuario(usuario_id), "sucesso": True}), 200


def listar_todos_pedidos():
    return jsonify({"dados": pedido_service.listar_todos(), "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    dados = request.get_json() or {}
    novo_status = dados.get("status", "")
    if novo_status not in STATUS_VALIDOS:
        return jsonify({"erro": "Status inválido"}), 400
    pedido_service.atualizar_status(pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
