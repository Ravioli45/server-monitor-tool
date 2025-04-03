from flask_login import UserMixin

import sqlalchemy as sa
import sqlalchemy.orm as so

from argon2.exceptions import VerificationError

from app import db
from app import ph
from app import login

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)

    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))

    def set_password(self, password):
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        try:
            return ph.verify(self.password_hash, password)
        except VerificationError:
            return False

    def __repr__(self):
        return f"<User {self.id}:{self.username}>"
