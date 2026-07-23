"""Controller de Relatório e Health."""
from flask import jsonify

from src.services import health_service, relatorio_service


def relatorio_vendas():
    return jsonify({"dados": relatorio_service.relatorio_vendas(), "sucesso": True}), 200


def health_check():
    return jsonify(health_service.status()), 200
