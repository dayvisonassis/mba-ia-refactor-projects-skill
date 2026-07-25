"""Decorators de autenticação/autorização (T7 / AP-07).

Aplicados às rotas sensíveis. Rotas públicas seguem abertas; o cliente autentica
via POST /login e envia `Authorization: Bearer <token>`.
"""
from functools import wraps

from flask import g, jsonify, request

from services import auth_service


def _extract_token():
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[len("Bearer "):]
    return None


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        data = auth_service.verify_token(_extract_token())
        if not data:
            return jsonify({"error": "Não autorizado"}), 401
        g.current_user = data
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        data = auth_service.verify_token(_extract_token())
        if not data:
            return jsonify({"error": "Não autorizado"}), 401
        if data.get("role") != "admin":
            return jsonify({"error": "Requer privilégio de admin"}), 403
        g.current_user = data
        return fn(*args, **kwargs)
    return wrapper
