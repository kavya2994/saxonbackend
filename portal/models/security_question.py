from . import db
from flask_restx import fields
from sqlalchemy import Sequence


class SecurityQuestion(db.Model):
    __bind_key__ = 'writeonly'
    # __tablename__ = 'SecurityQuestion'

    SecurityQuestionID = db.Column(db.Integer, Sequence('securityquestion_id_seq'), primary_key=True, nullable=False)
    Question = db.Column(db.String(255))

