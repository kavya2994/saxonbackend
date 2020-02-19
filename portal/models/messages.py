from sqlalchemy import Sequence

from . import db


class Messages(db.Model):
    __bind_key__ = 'writeonly'

    MessageID = db.Column(db.Integer, Sequence('messages_id_seq'), primary_key=True, nullable=False)
    Subject = db.Column(db.String(255), unique=True)
    Message = db.Column(db.String(255))
    CreatedDate = db.Column(db.DateTime)
    AddedBy = db.Column(db.String(255))


