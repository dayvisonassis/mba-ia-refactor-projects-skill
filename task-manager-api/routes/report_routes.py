import logging
from datetime import timedelta

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from database import db
from middlewares.auth import login_required
from models.category import Category
from models.task import Task
from models.user import User
from services import task_service
from utils.helpers import utcnow

logger = logging.getLogger(__name__)
report_bp = Blueprint('reports', __name__)


@report_bp.route('/reports/summary', methods=['GET'])
@login_required
def summary_report():
    all_tasks = task_service.list_all()

    by_status = {'pending': 0, 'in_progress': 0, 'done': 0, 'cancelled': 0}
    by_priority = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    overdue_list = []
    for t in all_tasks:
        by_status[t.status] = by_status.get(t.status, 0) + 1
        by_priority[t.priority] = by_priority.get(t.priority, 0) + 1
        if t.is_overdue():  # regra centralizada
            overdue_list.append({
                'id': t.id,
                'title': t.title,
                'due_date': str(t.due_date),
                'days_overdue': (utcnow() - t.due_date).days,
            })

    seven_days_ago = utcnow() - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == 'done', Task.updated_at >= seven_days_ago
    ).count()

    users = User.query.all()
    user_stats = []
    for u in users:
        user_tasks = [t for t in all_tasks if t.user_id == u.id]
        total = len(user_tasks)
        completed = sum(1 for t in user_tasks if t.status == 'done')
        user_stats.append({
            'user_id': u.id,
            'user_name': u.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0,
        })

    report = {
        'generated_at': str(utcnow()),
        'overview': {
            'total_tasks': len(all_tasks),
            'total_users': len(users),
            'total_categories': Category.query.count(),
        },
        'tasks_by_status': by_status,
        'tasks_by_priority': {
            'critical': by_priority[1], 'high': by_priority[2], 'medium': by_priority[3],
            'low': by_priority[4], 'minimal': by_priority[5],
        },
        'overdue': {'count': len(overdue_list), 'tasks': overdue_list},
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }
    return jsonify(report), 200


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
@login_required
def user_report(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    tasks = task_service.list_by_user(user_id)
    total = len(tasks)
    counts = {'done': 0, 'pending': 0, 'in_progress': 0, 'cancelled': 0}
    overdue = 0
    high_priority = 0
    for t in tasks:
        counts[t.status] = counts.get(t.status, 0) + 1
        if t.priority <= 2:
            high_priority += 1
        if t.is_overdue():  # regra centralizada
            overdue += 1

    report = {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            'done': counts['done'],
            'pending': counts['pending'],
            'in_progress': counts['in_progress'],
            'cancelled': counts['cancelled'],
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': round((counts['done'] / total) * 100, 2) if total > 0 else 0,
        },
    }
    return jsonify(report), 200


@report_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    result = []
    for c in categories:
        data = c.to_dict()
        data['task_count'] = Task.query.filter_by(category_id=c.id).count()
        result.append(data)
    return jsonify(result), 200


@report_bp.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    if not data.get('name'):
        return jsonify({'error': 'Nome é obrigatório'}), 400

    category = Category()
    category.name = data['name']
    category.description = data.get('description', '')
    category.color = data.get('color', '#000000')

    try:
        db.session.add(category)
        db.session.commit()
        return jsonify(category.to_dict()), 201
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Erro ao criar categoria")
        return jsonify({'error': 'Erro ao criar categoria'}), 500


@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    cat = Category.query.get(cat_id)
    if not cat:
        return jsonify({'error': 'Categoria não encontrada'}), 404

    data = request.get_json()
    if 'name' in data:
        cat.name = data['name']
    if 'description' in data:
        cat.description = data['description']
    if 'color' in data:
        cat.color = data['color']

    try:
        db.session.commit()
        return jsonify(cat.to_dict()), 200
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Erro ao atualizar categoria")
        return jsonify({'error': 'Erro ao atualizar'}), 500


@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    cat = Category.query.get(cat_id)
    if not cat:
        return jsonify({'error': 'Categoria não encontrada'}), 404

    try:
        db.session.delete(cat)
        db.session.commit()
        return jsonify({'message': 'Categoria deletada'}), 200
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Erro ao deletar categoria")
        return jsonify({'error': 'Erro ao deletar'}), 500
