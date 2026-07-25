import logging

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from services import task_service
from utils.helpers import process_task_data

logger = logging.getLogger(__name__)
task_bp = Blueprint('tasks', __name__)


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    # Eager loading (sem N+1) + serialização única com campos derivados.
    tasks = task_service.list_all()
    return jsonify([t.to_dict(include_relations=True) for t in tasks]), 200


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = task_service.get(task_id)
    if not task:
        return jsonify({'error': 'Task não encontrada'}), 404
    return jsonify(task.to_dict(include_relations=True)), 200


@task_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    if not data.get('title'):
        return jsonify({'error': 'Título é obrigatório'}), 400

    processed, error = process_task_data(data)
    if error:
        return jsonify({'error': error}), 400

    user_id = data.get('user_id')
    category_id = data.get('category_id')
    if user_id and not User.query.get(user_id):
        return jsonify({'error': 'Usuário não encontrado'}), 404
    if category_id and not Category.query.get(category_id):
        return jsonify({'error': 'Categoria não encontrada'}), 404

    task = Task()
    task.title = processed['title']
    task.description = processed.get('description', '')
    task.status = processed.get('status', 'pending')
    task.priority = processed.get('priority', 3)
    task.user_id = user_id
    task.category_id = category_id
    if 'due_date' in processed:
        task.due_date = processed['due_date']
    if 'tags' in processed:
        task.tags = processed['tags']

    try:
        db.session.add(task)
        db.session.commit()
        logger.info("Task criada: %s - %s", task.id, task.title)
        return jsonify(task.to_dict(include_relations=True)), 201
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Erro ao criar task")
        return jsonify({'error': 'Erro ao criar task'}), 500


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task não encontrada'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    processed, error = process_task_data(data)
    if error:
        return jsonify({'error': error}), 400

    if 'user_id' in data:
        if data['user_id'] and not User.query.get(data['user_id']):
            return jsonify({'error': 'Usuário não encontrado'}), 404
        task.user_id = data['user_id']
    if 'category_id' in data:
        if data['category_id'] and not Category.query.get(data['category_id']):
            return jsonify({'error': 'Categoria não encontrada'}), 404
        task.category_id = data['category_id']

    for field in ('title', 'description', 'status', 'priority', 'due_date', 'tags'):
        if field in processed:
            setattr(task, field, processed[field])

    try:
        db.session.commit()
        logger.info("Task atualizada: %s", task.id)
        return jsonify(task.to_dict(include_relations=True)), 200
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Erro ao atualizar task")
        return jsonify({'error': 'Erro ao atualizar'}), 500


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task não encontrada'}), 404

    try:
        db.session.delete(task)
        db.session.commit()
        logger.info("Task deletada: %s", task_id)
        return jsonify({'message': 'Task deletada com sucesso'}), 200
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Erro ao deletar task")
        return jsonify({'error': 'Erro ao deletar'}), 500


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    query = request.args.get('q', '')
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')
    user_id = request.args.get('user_id', '')

    tasks = Task.query
    if query:
        tasks = tasks.filter(
            db.or_(Task.title.like(f'%{query}%'), Task.description.like(f'%{query}%'))
        )
    if status:
        tasks = tasks.filter(Task.status == status)
    if priority:
        tasks = tasks.filter(Task.priority == int(priority))
    if user_id:
        tasks = tasks.filter(Task.user_id == int(user_id))

    return jsonify([t.to_dict() for t in tasks.all()]), 200


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    total = Task.query.count()
    # Centraliza "overdue" via Task.is_overdue() (sem lógica inline duplicada).
    overdue_count = sum(1 for t in Task.query.all() if t.is_overdue())
    done = Task.query.filter_by(status='done').count()

    stats = {
        'total': total,
        'pending': Task.query.filter_by(status='pending').count(),
        'in_progress': Task.query.filter_by(status='in_progress').count(),
        'done': done,
        'cancelled': Task.query.filter_by(status='cancelled').count(),
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }
    return jsonify(stats), 200
