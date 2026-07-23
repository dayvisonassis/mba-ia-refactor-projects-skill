"""Configuração da aplicação — carregada de variáveis de ambiente (T2).

Nenhum segredo fica hardcoded no código-fonte. Em produção, defina as variáveis
de ambiente; os defaults abaixo servem apenas para desenvolvimento local.
"""
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "5000"))
DB_PATH = os.environ.get("DB_PATH", "loja.db")
