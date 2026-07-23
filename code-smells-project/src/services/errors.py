"""Exceções de domínio compartilhadas pelos services."""


class ValidationError(Exception):
    """Erro de validação de entrada — mapeado para HTTP 400 nos controllers."""
    pass
