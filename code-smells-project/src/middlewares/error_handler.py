"""Middleware de tratamento de erros centralizado + logging (T10 / AP-11).

Detalhes do erro vão para o log; o cliente recebe mensagens genéricas.
"""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({"erro": e.description, "codigo": e.code}), e.code

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        logger.exception("Erro não tratado")
        return jsonify({"erro": "Erro interno do servidor"}), 500
