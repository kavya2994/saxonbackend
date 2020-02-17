from . import db
from ..helpers import uuid_generator


class Token(db.Model):
    __bind_key__ = 'writeonly'
    # __tablename__ = 'Token'

    TokenID = db.Column(db.String(36), primary_key=True, default=uuid_generator, nullable=False)
    FormID = db.Column(db.Integer, primary_key=True, nullable=False)

    FormStatus = db.Column(db.String(255))
    FormType = db.Column(db.String(255))
    InitiatedBy = db.Column(db.String(255))
    InitiatedDate = db.Column(db.DateTime)
    PendingFrom = db.Column(db.String(255))
    TokenStatus = db.Column(db.String(255))
    EmployerID = db.Column(db.String(255))
    OlderTokenID = db.Column(db.String(255))


