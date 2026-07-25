"""Service de Task — consultas com eager loading para eliminar N+1 (T8 / AP-08)."""
from sqlalchemy.orm import joinedload

from models.task import Task


def _with_relations():
    return Task.query.options(joinedload(Task.user), joinedload(Task.category))


def list_all():
    return _with_relations().all()


def list_by_user(user_id):
    return _with_relations().filter(Task.user_id == user_id).all()


def get(task_id):
    return _with_relations().filter(Task.id == task_id).first()
