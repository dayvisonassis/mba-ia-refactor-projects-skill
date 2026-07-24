"""Configuração da aplicação — carregada de variáveis de ambiente (T2 / AP-02).

Nenhum segredo hardcoded. Os defaults servem apenas para desenvolvimento local.
"""
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "5000"))

# Credenciais de SMTP — nunca hardcoded (antes em notification_service.py).
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")

# Tempo de expiração do token de autenticação (segundos).
TOKEN_MAX_AGE = int(os.environ.get("TOKEN_MAX_AGE", "3600"))
