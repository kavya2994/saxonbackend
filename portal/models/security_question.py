from . import db
from flask_restplus import fields
# from ..api import api


class SecurityQuestion(db.Model):
    __bind_key__ = 'writeonly'

    SecurityQuestionID = db.Column(db.Integer, primary_key=True, nullable=False)
    Question = db.Column(db.String(255))


SecurityQuestionModel = {
    'SecurityQuestionID': fields.Integer,
    'Question': fields.String,
}
