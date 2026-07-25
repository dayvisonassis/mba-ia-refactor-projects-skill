import logging
import re

from flask import Blueprint, g, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from database import db
from middlewares.auth import admin_required, login_required
from models.user import User
from services import auth_service, task_service

logger = logging.getLogger(__name__)
user_bp = Blueprint('users', __name__)

EMAIL_RE = r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$'
VALID_ROLES = ('user', 'admin', 'manager')
MIN_PASSWORD_LENGTH = 4
DEFAULT_ROLE = 'user'

# T13 — allow-list de campos graváveis pelo cliente.
# Validar o VALOR de um campo não autoriza a ESCRITA dele: `role` só entra pela
# lista de admin, senão qualquer anônimo emite o próprio admin (AP-13).
SELF_WRITABLE = frozenset({'name', 'email', 'password'})
ADMIN_WRITABLE = SELF_WRITABLE | {'role', 'active'}


def _campos_permitidos(caller, target_id):
    """Campos que este chamador pode gravar neste usuário."""
    if caller.get('role') == 'admin':
        return ADMIN_WRITABLE
    return SELF_WRITABLE if caller.get('uid') == target_id else frozenset()


@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    result = []
    for u in users:
        data = u.to_dict()
        data['task_count'] = len(u.tasks)
        result.append(data)
    return jsonify(result), 200


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    data = user.to_dict()  # sem o campo password
    tasks = task_service.list_by_user(user_id)
    data['tasks'] = [t.to_dict() for t in tasks]
    return jsonify(data), 200


@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name:
        return jsonify({'error': 'Nome é obrigatório'}), 400
    if not email:
        return jsonify({'error': 'Email é obrigatório'}), 400
    if not password:
        return jsonify({'error': 'Senha é obrigatória'}), 400
    if not re.match(EMAIL_RE, email):
        return jsonify({'error': 'Email inválido'}), 400
    if len(password) < MIN_PASSWORD_LENGTH:
        return jsonify({'error': 'Senha deve ter no mínimo 4 caracteres'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email já cadastrado'}), 409

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    # T13/AP-13: auto-cadastro nunca lê `role` do payload — sempre o papel padrão.
    # Promoção só por PUT autenticado com token de admin.
    user.role = DEFAULT_ROLE

    try:
        db.session.add(user)
        db.session.commit()
        logger.info("Usuário criado: %s - %s", user.id, user.name)
        return jsonify(user.to_dict()), 201  # sem password na resposta
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Erro ao criar usuário")
        return jsonify({'error': 'Erro ao criar usuário'}), 500


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    # T13: o chamador só grava o que a allow-list do seu papel permite.
    # Campos fora dela são ignorados silenciosamente (fail-closed): uma coluna
    # nova no model não vira gravável pelo cliente por acidente.
    permitidos = _campos_permitidos(g.current_user, user_id)
    if not permitidos:
        return jsonify({'error': 'Não autorizado a alterar este usuário'}), 403

    if 'name' in permitidos and 'name' in data:
        user.name = data['name']
    if 'email' in permitidos and 'email' in data:
        if not re.match(EMAIL_RE, data['email']):
            return jsonify({'error': 'Email inválido'}), 400
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': 'Email já cadastrado'}), 409
        user.email = data['email']
    if 'password' in permitidos and 'password' in data:
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            return jsonify({'error': 'Senha muito curta'}), 400
        user.set_password(data['password'])
    if 'role' in permitidos and 'role' in data:
        if data['role'] not in VALID_ROLES:
            return jsonify({'error': 'Role inválido'}), 400
        user.role = data['role']
    if 'active' in permitidos and 'active' in data:
        user.active = data['active']

    try:
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Erro ao atualizar usuário")
        return jsonify({'error': 'Erro ao atualizar'}), 500


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    for task in task_service.list_by_user(user_id):
        db.session.delete(task)

    try:
        db.session.delete(user)
        db.session.commit()
        logger.info("Usuário deletado: %s", user_id)
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Erro ao deletar usuário")
        return jsonify({'error': 'Erro ao deletar'}), 500


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    tasks = task_service.list_by_user(user_id)
    return jsonify([t.to_dict() for t in tasks]), 200


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Credenciais inválidas'}), 401
    if not user.active:
        return jsonify({'error': 'Usuário inativo'}), 403

    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),  # sem password
        'token': auth_service.issue_token(user),  # token assinado com expiração
    }), 200
