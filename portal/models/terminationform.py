from . import db


class Terminationform(db.Model):
    FormID = db.Column(db.Integer, primary_key=True, nullable=False)

    EmployerName = db.Column(db.String(255))
    Date = db.Column(db.String(255))
    MemberName = db.Column(db.String(255))
    MemberNumber = db.Column(db.String(255))
    EmailAddress = db.Column(db.String(255))
    Finaldateofemployment = db.Column(db.String(255))
    ReasonforTermination = db.Column(db.String(255))
    LastDeduction = db.Column(db.String(255))
    Address = db.Column(db.String(255))
    AddressLine2 = db.Column(db.String(255))
    District = db.Column(db.String(255))
    PostalCode = db.Column(db.String(255))
    Country = db.Column(db.String(255))
    Estimatedannualincomerange = db.Column(db.String(255))
    Status = db.Column(db.String(255))
    EmployerID = db.Column(db.String(255))
    PendingFrom = db.Column(db.String(255))
