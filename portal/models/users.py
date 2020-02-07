from . import db


class Users(db.Model):
    __bind_key__ = 'writeonly'

    Username = db.Column(db.String(255), primary_key=True, nullable=False)
    MemberID = db.Column(db.Integer)
    SecurityQuestionID = db.Column(db.Integer, db.ForeignKey('security_question.SecurityQuestionID'))
    SecurityQuestion = db.relationship('SecurityQuestion', backref='users')

    Password = db.Column(db.String(255))
    TemporaryPassword = db.Column(db.String(255))
    Email = db.Column(db.String(255))
    DisplayName = db.Column(db.String(255))
    SessionDuration = db.Column(db.String(255))
    PhoneNumber = db.Column(db.String(255))
    SecurityAnswer = db.Column(db.String(255))
    Role = db.Column(db.String(255))
    Status = db.Column(db.String(255))
    UserCreatedTime = db.Column(db.DateTime)

#  {'Pass': '28634',
#   'answer': 'hello',
#   'displayname': 'Member124',
#   'email': 'helloo@gmail.com',
#   'member_id': '28634',
#   'password': 'xyz',
#   'role': 'member',
#   'securityQuestion': '2',
#   'status': 'active',
#   'temppass': False,
#   'type': 'member',
#   'username': '28634'},
