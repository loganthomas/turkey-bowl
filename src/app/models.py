import datetime
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db


class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def __repr__(self):
        return f'<User {self.username}>'


# TODOS
# - Add user to result like author
class Result(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    year: so.Mapped[datetime.datetime] = so.mapped_column(
        index=True, default=lambda: datetime.datetime.now(datetime.UTC).year
    )
    points: so.Mapped[float] = so.mapped_column(sa.Float(), index=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    def __repr__(self):
        return f'<Result {self.year} {self.user_id} {self.points}>'
