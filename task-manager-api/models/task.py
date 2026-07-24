from datetime import UTC, datetime

from database import db


def _utcnow():
    """UTC atual como datetime naive (substitui datetime.utcnow, deprecated 3.12+)."""
    return datetime.now(UTC).replace(tzinfo=None)


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending')
    priority = db.Column(db.Integer, default=3)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=_utcnow)
    updated_at = db.Column(db.DateTime, default=_utcnow, onupdate=_utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    def to_dict(self, include_relations=False):
        """Fonte única de serialização da task (sempre inclui `overdue`).

        include_relations=True adiciona user_name/category_name a partir dos
        relacionamentos já mapeados (use com joinedload para evitar N+1).
        """
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'tags': self.tags.split(',') if self.tags else [],
            'overdue': self.is_overdue(),
        }
        if include_relations:
            data['user_name'] = self.user.name if self.user else None
            data['category_name'] = self.category.name if self.category else None
        return data

    def validate_status(self, new_status):
        return new_status in ('pending', 'in_progress', 'done', 'cancelled')

    def validate_priority(self, p):
        return 1 <= p <= 5

    def is_overdue(self):
        """Única definição de "atrasado" — antes duplicada inline em 5+ lugares."""
        if not self.due_date:
            return False
        return self.due_date < _utcnow() and self.status not in ('done', 'cancelled')
