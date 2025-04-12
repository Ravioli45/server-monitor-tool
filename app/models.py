from datetime import datetime, timezone
from typing import List

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

    monitors: so.WriteOnlyMapped[List['Monitor']] = so.relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def set_password(self, password):
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        try:
            return ph.verify(self.password_hash, password)
        except VerificationError:
            return False

    def __repr__(self):
        return f"<User {self.id}:{self.username}>"

class Monitor(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    url: so.Mapped[str] = so.mapped_column(sa.String(512))

    time_next_ping: so.Mapped[datetime] = so.mapped_column(index=True)
    seconds_to_next_ping: so.Mapped[int] = so.mapped_column()

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id, ondelete="CASCADE"), index=True)
    user: so.Mapped['User'] = so.relationship(back_populates="monitors")

    status_checks: so.WriteOnlyMapped[List['Status']] = so.relationship(
        back_populates="monitor",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self):
        return f"<Monitor {self.id}:{self.url}>"

class Status(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))

    response: so.Mapped[str] = so.mapped_column(sa.String(64))
    ssl_expired: so.Mapped[bool] = so.mapped_column()

    monitor_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Monitor.id, ondelete="CASCADE"), index=True)
    monitor: so.Mapped['Monitor'] = so.relationship(back_populates="status_checks")

    def __repr__(self):
        return f"<Status {self.id}:{self.response}>"
