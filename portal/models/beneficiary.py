from . import db


class Beneficiary(db.Model):
    __bind_key__ = 'writeonly'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    enrollmentformID = db.Column(db.Integer)

    beneficiaryFirstName = db.Column(db.String(255))
    beneficiaryLastName = db.Column(db.String(255))
    beneficiaryDOB = db.Column(db.String(255))
    relationship = db.Column(db.String(255))
    role = db.Column(db.String(255))
    phoneNumber = db.Column(db.String(255))
