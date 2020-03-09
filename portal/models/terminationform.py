from sqlalchemy.orm import relationship

from . import db
from sqlalchemy import Sequence


class Terminationform(db.Model):
    __bind_key__ = 'writeonly'
    # __tablename__ = "Terminationform"

    FormID = db.Column(db.Integer, Sequence('terminationform_id_seq'),
                       primary_key=True, nullable=False)

    EmployerName = db.Column(db.String(255), nullable=True)
    EmployerID = db.Column(db.String(255))
    InitiatedDate = db.Column(db.DateTime)
    MemberName = db.Column(db.String(255))
    MemberNumber = db.Column(db.String(255), nullable=True)
    EmailAddress = db.Column(db.String(255), nullable=True)
    FinalDateOfEmployment = db.Column(db.Date, nullable=True)
    ReasonforTermination = db.Column(db.String(255), nullable=True)
    LastDeduction = db.Column(db.String(255), nullable=True)
    Address = db.Column(db.String(255), nullable=True)
    AddressLine2 = db.Column(db.String(255), nullable=True)
    District = db.Column(db.String(255), nullable=True)
    PostalCode = db.Column(db.String(255), nullable=True)
    Country = db.Column(db.String(255), nullable=True)
    EstimatedAnnualIncomeRange = db.Column(db.String(255), nullable=True)
    Status = db.Column(db.String(255), nullable=True)
    PendingFrom = db.Column(db.String(255), nullable=True)
    PhoneNumber = db.Column(db.String(255), nullable=True)
    LastNotifiedDate = db.Column(db.Date, nullable=True)
    Signature = db.Column(db.Text, nullable=True)
    SignatureType = db.Column(db.String(255), nullable=True)
    # FilePath = db.Column(db.String(255), nullable=True)

    # termination_form = relationship('Token', foreign_keys='Token.FormID')

