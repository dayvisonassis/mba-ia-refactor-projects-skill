"""Controller de Usuário — orquestra o request; hashing/auth ficam no service."""
from flask import jsonify, request

from src.services import usuario_service
from src.services.errors import ValidationError


def listar_usuarios():
    return jsonify({"dados": usuario_service.listar(), "sucesso": True}), 200


def buscar_usuario(id):
    usuario = usuario_service.obter(id)
    if usuario:
        return jsonify({"dados": usuario, "sucesso": True}), 200
    return jsonify({"erro": "Usuário não encontrado"}), 404


def criar_usuario():
    dados = request.get_json() or {}
    try:
        novo_id = usuario_service.criar(
            dados.get("nome", ""), dados.get("email", ""), dados.get("senha", "")
        )
    except ValidationError as e:
        return jsonify({"erro": str(e)}), 400
    return jsonify({"dados": {"id": novo_id}, "sucesso": True}), 201


def login():
    dados = request.get_json() or {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400

    usuario = usuario_service.autenticar(email, senha)
    if usuario:
        return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
    return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
