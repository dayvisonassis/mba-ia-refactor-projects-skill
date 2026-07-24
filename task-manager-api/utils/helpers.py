"""Utilitários — imports mortos removidos (AP-11); `type()==list` → isinstance (AP-10)."""
from datetime import UTC, datetime
import re


def utcnow():
    """UTC atual como datetime naive (substitui datetime.utcnow, deprecated 3.12+)."""
    return datetime.now(UTC).replace(tzinfo=None)


def format_date(date_obj):
    return str(date_obj) if date_obj else None


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    return bool(re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', email))


def sanitize_string(s):
    return s.strip() if s else s


def parse_date(date_string):
    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    return None


def is_valid_color(color):
    return bool(color and len(color) == 7 and color[0] == '#')


def process_task_data(data, existing_task=None):
    """Validação única de task — reutilizada por create e update (T9 / AP-09)."""
    result = {}

    if 'title' in data:
        title = data['title']
        if not title:
            return None, 'Título não pode ser vazio'
        title = title.strip()
        if not (MIN_TITLE_LENGTH <= len(title) <= MAX_TITLE_LENGTH):
            return None, f'Título deve ter entre {MIN_TITLE_LENGTH} e {MAX_TITLE_LENGTH} caracteres'
        result['title'] = title

    if 'description' in data:
        result['description'] = data['description']

    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            return None, 'Status inválido'
        result['status'] = data['status']

    if 'priority' in data:
        try:
            p = int(data['priority'])
        except (ValueError, TypeError):
            return None, 'Prioridade inválida'
        if not (1 <= p <= 5):
            return None, 'Prioridade deve ser entre 1 e 5'
        result['priority'] = p

    if 'due_date' in data:
        if data['due_date']:
            parsed = parse_date(data['due_date'])
            if not parsed:
                return None, 'Data inválida'
            result['due_date'] = parsed
        else:
            result['due_date'] = None

    if 'tags' in data:
        tags = data['tags']
        result['tags'] = ','.join(tags) if isinstance(tags, list) else tags

    return result, None


VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
VALID_ROLES = ['user', 'admin', 'manager']
MAX_TITLE_LENGTH = 200
MIN_TITLE_LENGTH = 3
MIN_PASSWORD_LENGTH = 4
DEFAULT_PRIORITY = 3
DEFAULT_COLOR = '#000000'
