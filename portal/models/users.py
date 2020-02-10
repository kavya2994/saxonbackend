from . import db


class Users(db.Model):
    __bind_key__ = 'writeonly'

    Username = db.Column(db.String(255), primary_key=True, nullable=False)
    MemberID = db.Column(db.Integer)
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
