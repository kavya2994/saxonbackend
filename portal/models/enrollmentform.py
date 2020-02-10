from . import db
from sqlalchemy import Sequence


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
    DOB = db.Column(db.String(255), nullable=True)
    Title = db.Column(db.String(255), nullable=True)
    MaritalStatus = db.Column(db.String(255), nullable=True)
    MailingAddress = db.Column(db.String(255), nullable=True)
    AddressLine2 = db.Column(db.String(255), nullable=True)
    District = db.Column(db.String(255), nullable=True)
    PostalCode = db.Column(db.String(255), nullable=True)
    Country = db.Column(db.String(255), nullable=True)
    EmailAddress = db.Column(db.String(255))
    Telephone = db.Column(db.String(255), nullable=True)
    StartDateofContribution = db.Column(db.DateTime, nullable=True)
    StartDateofEmployment = db.Column(db.DateTime, nullable=True)
    ConfirmationStatus = db.Column(db.String(255), nullable=True)
    SignersName = db.Column(db.String(255), nullable=True)
    Signature = db.Column(db.String(255), nullable=True)
    Estimatedannualincomerange = db.Column(db.String(255), nullable=True)
    ImmigrationStatus = db.Column(db.String(255), nullable=True)
    PendingFrom = db.Column(db.String(255), nullable=True)
    SpouseName = db.Column(db.String(255), nullable=True)
    SpouseDOB = db.Column(db.String(255), nullable=True)
    FilePath = db.Column(db.String(255), nullable=True)
