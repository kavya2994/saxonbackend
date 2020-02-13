from . import db
from sqlalchemy import Sequence
from flask_restplus import fields


class Beneficiary(db.Model):
    __bind_key__ = 'writeonly'

    BeneficiaryID = db.Column(db.Integer, Sequence('beneficiary_id_seq'), primary_key=True, nullable=False)
    EnrollmentformID = db.Column(db.Integer)

    FirstName = db.Column(db.String(255))
    LastName = db.Column(db.String(255))
    DOB = db.Column(db.Date)
    Relationship = db.Column(db.String(255))
    Role = db.Column(db.String(255))
    PhoneNumber = db.Column(db.String(255))
    Percentage = db.Column(db.Float)



BeneficiaryResponseModel = {
    'BeneficiaryID': fields.String,
    'EnrollmentformID': fields.String,
    'FirstName': fields.String,
    'LastName': fields.String,
    'DOB': fields.Date,
    'Relationship': fields.String,
    'Role': fields.String,
    'PhoneNumber': fields.String,
    'Percentage': fields.Float,
}
