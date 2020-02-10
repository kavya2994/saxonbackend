from . import db
from sqlalchemy import Sequence


class Comments(db.Model):
    __bind_key__ = 'writeonly'

    CommentsID = db.Column(db.Integer, Sequence('comments_id_seq'), primary_key=True, nullable=False)
    FormID = db.Column(db.Integer)

    Role = db.Column(db.String(255))
    Comment = db.Column(db.String(255))
    Date = db.Column(db.String(255))
