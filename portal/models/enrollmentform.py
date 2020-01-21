from . import db


class Enrollmentform(db.Model):
    __bind_key__ = 'writeonly'

    EnrollmentID = db.Column(db.Integer, primary_key=True, nullable=False)
    Address = db.Column(db.String(255))
    AddressLine2 = db.Column(db.String(255))
    Comments = db.Column(db.String(255))
    Country = db.Column(db.String(255))
    District = db.Column(db.String(255))
    Dob = db.Column(db.String(255))
    Email = db.Column(db.String(255))
    EmployerComments = db.Column(db.String(255))
    Employername = db.Column(db.String(255))
    Employernumber = db.Column(db.String(255))
    File = db.Column(db.String(255))
    FormCreatedDate = db.Column(db.DateTime)
    Immigrationstatus = db.Column(db.String(255))
    Incomerange = db.Column(db.String(255))
    IsExistingMember = db.Column(db.String(255))
    MaidenName = db.Column(db.String(255))
    Maritalstatus = db.Column(db.String(255))
    MemberLastName = db.Column(db.String(255))
    MemberfirstName = db.Column(db.String(255))
    Middlename = db.Column(db.String(255))
    PendingFrom = db.Column(db.String(255))
    PhoneNumber = db.Column(db.String(255))
    Postalcode = db.Column(db.String(255))
    Startdate = db.Column(db.DateTime)
    Startemployment = db.Column(db.String(255))
    Status = db.Column(db.String(255))
    Title = db.Column(db.String(255))
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
