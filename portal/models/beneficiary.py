from . import db


class Beneficiary(db.Model):
    BeneficiaryID = db.Column(db.Integer, primary_key=True, nullable=False)
    EnrollmentformID = db.Column(db.Integer)

    BeneficiaryFirstName = db.Column(db.String(255))
    BeneficiaryLastName = db.Column(db.String(255))
    BeneficiaryDOB = db.Column(db.String(255))
    Relationship = db.Column(db.String(255))
    Role = db.Column(db.String(255))
    PhoneNumber = db.Column(db.String(255))
