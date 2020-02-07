from . import db


class SecurityQuestion(db.Model):
    __bind_key__ = 'writeonly'

    SecurityQuestionID = db.Column(db.Integer, primary_key=True, nullable=False)
    Question = db.Column(db.String(255))
