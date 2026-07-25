from datetime import UTC, datetime

from werkzeug.security import check_password_hash, generate_password_hash

from database import db


def _utcnow():
    """UTC atual como datetime naive (substitui datetime.utcnow, deprecated 3.12+)."""
    return datetime.now(UTC).replace(tzinfo=None)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=_utcnow)

    def to_dict(self):
        # NÃO inclui o campo `password` (nunca deve trafegar ao cliente).
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at),
        }

    def set_password(self, pwd):
        # Hash salgado e forte (substitui MD5).
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)

    def is_admin(self):
        return self.role == 'admin'
