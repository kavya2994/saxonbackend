from . import db


class Token(db.Model):
    TokenID = db.Column(db.Integer, primary_key=True, nullable=False)
    FormID = db.Column(db.Integer)

    FormCreatedDate = db.Column(db.String(255))
    FormStatus = db.Column(db.String(255))
    FormType = db.Column(db.String(255))
    InitiatedBy = db.Column(db.String(255))
    InitiatedDate = db.Column(db.String(255))
    PendingFrom = db.Column(db.String(255))
    TokenStatus = db.Column(db.String(255))
    EmployerID = db.Column(db.String(255))
    OlderTokenID = db.Column(db.String(255))
