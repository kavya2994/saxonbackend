from . import db
from sqlalchemy import Sequence


class Users(db.Model):
    __bind_key__ = 'writeonly'

    UserID = db.Column(db.Integer, Sequence('user_id_seq'), primary_key=True, nullable=False)
    Username = db.Column(db.String(255), unique=True, nullable=False)

    SecurityQuestionID = db.Column(db.Integer, db.ForeignKey('security_question.SecurityQuestionID'))
    SecurityQuestion = db.relationship('SecurityQuestion', backref='users')

    Password = db.Column(db.String(255))
    TemporaryPassword = db.Column(db.Boolean, default=False, nullable=False)
    Email = db.Column(db.String(255))
    DisplayName = db.Column(db.String(255))
    SessionDuration = db.Column(db.String(255))
    PhoneNumber = db.Column(db.String(255))
    SecurityAnswer = db.Column(db.String(255))
    Role = db.Column(db.String(255))
    Status = db.Column(db.String(255))
    UserCreatedTime = db.Column(db.DateTime)
    Timezone = db.Column(db.String(255))
    Language = db.Column(db.String(255))
    Last5Passwords = db.Column(db.String(255))
    PassLastUpdatedDate = db.Column(db.DateTime)
