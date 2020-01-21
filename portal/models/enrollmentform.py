from . import db


class Enrollmentform(db.Model):
    __bind_key__ = 'writeonly'

    FormID = db.Column(db.Integer, primary_key=True, nullable=False)
    SecurityQuestionID = db.Column(db.Integer)

    EmployerName = db.Column(db.String(255))
    EmployerID = db.Column(db.String(255))
    InitiatedDate = db.Column(db.String(255))
    AlreadyEnrolled = db.Column(db.String(255))
    Status = db.Column(db.String(255))
    FirstName = db.Column(db.String(255))
    MiddleName = db.Column(db.String(255))
    LastName = db.Column(db.String(255))
    DOB = db.Column(db.String(255))
    Title = db.Column(db.String(255))
    MaritalStatus = db.Column(db.String(255))
    MailingAddress = db.Column(db.String(255))
    AddressLine2 = db.Column(db.String(255))
    District = db.Column(db.String(255))
    PostalCode = db.Column(db.String(255))
    Country = db.Column(db.String(255))
    EmailAddress = db.Column(db.String(255))
    Telephone = db.Column(db.String(255))
    StartDateofContribution = db.Column(db.String(255))
    StartDateofEmployment = db.Column(db.String(255))
    ConfirmationStatus = db.Column(db.String(255))
    SignersName = db.Column(db.String(255))
    Signature = db.Column(db.String(255))
    Estimatedannualincomerange = db.Column(db.String(255))
    ImmigrationStatus = db.Column(db.String(255))
    PendingFrom = db.Column(db.String(255))
    SpouseName = db.Column(db.String(255))
    SpouseDOB = db.Column(db.String(255))

    File = db.Column(db.String(255))
    FormCreatedDate = db.Column(db.DateTime)
    TokenID = db.Column(db.String(255))

#   'address': '',
#   'addressLine2': '',
#   'comments': '',
#   'country': '',
#   'district': '',
#   'dob': '',
#   'email': 'deepika.bharatula@manomay.biz',
#   'employerComments': '',
#   'employername': 'Saxon Pensions',
#   'employernumber': 'saxon',
#   'file': '',
#   'formCreatedDate': {'nanoseconds': 936510000, 'seconds': 1575456023},
#   'formType': 'Enrollment',
#   'immigrationstatus': '',
#   'incomerange': '',
#   'isExistingMember': 'false',
#   'maidenName': '',
#   'maritalstatus': 'false',
#   'memberLastName': '',
#   'memberfirstName': 'T5',
#   'middlename': '',
#   'pendingFrom': 'reviewermanager',
#   'phoneNumber': '',
#   'postalcode': '',
#   'startdate': '2019-12-03T18:30:00.000Z',
#   'startemployment': '2019-12-03T18:30:00.000Z',
#   'status': 'pending',
#   'title': '',
#   'tokenID': 'JsijaNKnK9GhUEVHm54S'},
