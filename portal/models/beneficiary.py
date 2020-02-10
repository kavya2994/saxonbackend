from . import db
from sqlalchemy import Sequence


class Beneficiary(db.Model):
    __bind_key__ = 'writeonly'

    BeneficiaryID = db.Column(db.Integer, Sequence('beneficiary_id_seq'), primary_key=True, nullable=False)
    BeneficiaryEnrollmentformID = db.Column(db.Integer)

    BeneficiaryBeneficiaryFirstName = db.Column(db.String(255))
    BeneficiaryBeneficiaryLastName = db.Column(db.String(255))
    BeneficiaryBeneficiaryDOB = db.Column(db.String(255))
    BeneficiaryRelationship = db.Column(db.String(255))
    BeneficiaryRole = db.Column(db.String(255))
    BeneficiaryPhoneNumber = db.Column(db.String(255))
