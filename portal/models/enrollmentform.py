from . import db
from sqlalchemy import Sequence
from flask_restplus import fields


class Enrollmentform(db.Model):
    __bind_key__ = 'writeonly'

    FormID = db.Column(db.Integer, Sequence('enrollmentform_id_seq'), primary_key=True, nullable=False)
    EmployerName = db.Column(db.String(255))
    EmployerID = db.Column(db.String(255), nullable=True)
    InitiatedDate = db.Column(db.DateTime(255), nullable=True)
    AlreadyEnrolled = db.Column(db.String(255), nullable=True)
    Status = db.Column(db.String(255), nullable=True)
    FirstName = db.Column(db.String(255), nullable=True)
    MiddleName = db.Column(db.String(255), nullable=True)
    LastName = db.Column(db.String(255), nullable=True)
    DOB = db.Column(db.Date, nullable=True)
    Title = db.Column(db.String(255), nullable=True)
    MaritalStatus = db.Column(db.String(255), nullable=True)
    MailingAddress = db.Column(db.String(255), nullable=True)
    AddressLine2 = db.Column(db.String(255), nullable=True)
    District = db.Column(db.String(255), nullable=True)
    PostalCode = db.Column(db.String(255), nullable=True)
    Country = db.Column(db.String(255), nullable=True)
    EmailAddress = db.Column(db.String(255))
    Telephone = db.Column(db.String(255), nullable=True)
    StartDateofContribution = db.Column(db.Date, nullable=True)
    StartDateofEmployment = db.Column(db.Date, nullable=True)
    ConfirmationStatus = db.Column(db.String(255), nullable=True)
    SignersName = db.Column(db.String(255), nullable=True)
    Signature = db.Column(db.String(255), nullable=True)
    Estimatedannualincomerange = db.Column(db.String(255), nullable=True)
    ImmigrationStatus = db.Column(db.String(255), nullable=True)
    PendingFrom = db.Column(db.String(255), nullable=True)
    SpouseName = db.Column(db.String(255), nullable=True)
    SpouseDOB = db.Column(db.Date, nullable=True)
    FilePath = db.Column(db.String(255), nullable=True)


EnrollmentformResponseModel = {
    'EmployerName': fields.String,
    'EmployerID': fields.String,
    'InitiatedDate': fields.DateTime,
    'AlreadyEnrolled': fields.String,
    'Status': fields.String,
    'FirstName': fields.String,
    'MiddleName': fields.String,
    'LastName': fields.String,
    'DOB': fields.String,
    'Title': fields.String,
    'MaritalStatus': fields.String,
    'MailingAddress': fields.String,
    'AddressLine2': fields.String,
    'District': fields.String,
    'PostalCode': fields.String,
    'Country': fields.String,
    'EmailAddress': fields.String,
    'Telephone': fields.String,
    'StartDateofContribution': fields.DateTime,
    'StartDateofEmployment': fields.DateTime,
    'ConfirmationStatus': fields.String,
    'SignersName': fields.String,
    'Signature': fields.String,
    'Estimatedannualincomerange': fields.String,
    'ImmigrationStatus': fields.String,
    'PendingFrom': fields.String,
    'SpouseName': fields.String,
    'SpouseDOB': fields.String,
    'FilePath': fields.String,
}
