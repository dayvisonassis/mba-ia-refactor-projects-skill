"""Controller de Produto — orquestra o request; sem SQL nem regra de negócio."""
from flask import jsonify, request

from src.services import produto_service
from src.services.errors import ValidationError


def listar_produtos():
    produtos = produto_service.listar()
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produto(id):
    produto = produto_service.obter(id)
    if produto:
        return jsonify({"dados": produto, "sucesso": True}), 200
    return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", type=float)
    preco_max = request.args.get("preco_max", type=float)
    resultados = produto_service.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


def criar_produto():
    try:
        dados = produto_service.validar_produto(request.get_json())
    except ValidationError as e:
        return jsonify({"erro": str(e)}), 400
    novo_id = produto_service.criar(dados)
    return jsonify({"dados": {"id": novo_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(id):
    if not produto_service.obter(id):
        return jsonify({"erro": "Produto não encontrado"}), 404
    try:
        dados = produto_service.validar_produto(request.get_json())
    except ValidationError as e:
        return jsonify({"erro": str(e)}), 400
    produto_service.atualizar(id, dados)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(id):
    if not produto_service.obter(id):
        return jsonify({"erro": "Produto não encontrado"}), 404
    produto_service.deletar(id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
