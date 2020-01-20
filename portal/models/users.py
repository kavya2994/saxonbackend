from . import db


class Users(db.Model):
    __bind_key__ = 'writeonly'

    Username = db.Column(db.String(255), primary_key=True, nullable=False)
    MemberID = db.Column(db.Integer) #, db.ForeignKey('tag.id'))
    securityQuestionID = db.Column(db.Integer)

    password = db.Column(db.String(255))
    TemporaryPassword = db.Column(db.String(255))
    Email = db.Column(db.String(255))
    DisplayName = db.Column(db.String(255))
    SessionExpiry = db.Column(db.String(255))
    PhoneNumber = db.Column(db.String(255))
    securityAnswer = db.Column(db.String(255))
    Role = db.Column(db.String(255))
    Status = db.Column(db.String(255))
    UserCreatedTime = db.Column(db.String(255))

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
