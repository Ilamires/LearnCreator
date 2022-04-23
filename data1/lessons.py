import datetime
import sqlalchemy
import json
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Lesson(SqlAlchemyBase):
    __tablename__ = 'lessons'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    added_to_favorites_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    rate = sqlalchemy.Column(sqlalchemy.Float, default=0)
    rates_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
    favourites = orm.relation("Favourites", back_populates='lesson')

    def __repr__(self):
        return f'<Lessons> {self.id} {self.user.name}, {self.title}: "{self.content}", {self.created_date}'

    def loads_json(self):
        return json.loads(Lesson.rates)
