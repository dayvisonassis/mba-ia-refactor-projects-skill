"""Service de autenticação — token assinado com expiração (T7 / AP-07).

Substitui o "fake-jwt-token-<id>" previsível por um token assinado (itsdangerous,
já dependência do Flask) que carrega uid/role e expira.
"""
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from config import settings

_serializer = URLSafeTimedSerializer(settings.SECRET_KEY, salt="auth-token")


def issue_token(user):
    return _serializer.dumps({"uid": user.id, "role": user.role})


def verify_token(token, max_age=None):
    if not token:
        return None
    try:
        return _serializer.loads(token, max_age=max_age or settings.TOKEN_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
