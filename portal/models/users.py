from . import db


class Users(db.Model):
    Username = db.Column(db.String(255), primary_key=True, nullable=False)
    MemberID = db.Column(db.Integer) #, db.ForeignKey('tag.id'))
    SecurityQuestionID = db.Column(db.Integer)

    Password = db.Column(db.String(255))
    TemporaryPassword = db.Column(db.String(255))
    Email = db.Column(db.String(255))
    DisplayName = db.Column(db.String(255))
    SessionDuration = db.Column(db.String(255))
    PhoneNumber = db.Column(db.String(255))
    SecurityAnswer = db.Column(db.String(255))
    Role = db.Column(db.String(255))
