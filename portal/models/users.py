from . import db


class Users(db.Model):
    __bind_key__ = 'writeonly'

    username = db.Column(db.String(255), primary_key=True, nullable=False)
    memberID = db.Column(db.Integer) #, db.ForeignKey('tag.id'))
    securityQuestionID = db.Column(db.Integer)

    password = db.Column(db.String(255))
    temporaryPassword = db.Column(db.String(255))
    email = db.Column(db.String(255))
    displayName = db.Column(db.String(255))
    sessionExpiry = db.Column(db.String(255))
    phoneNumber = db.Column(db.String(255))
    securityAnswer = db.Column(db.String(255))
    role = db.Column(db.String(255))
    status = db.Column(db.String(255))
    userCreatedTime = db.Column(db.String(255))

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
