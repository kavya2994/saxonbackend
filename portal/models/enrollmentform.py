from . import db


class Enrollmentform(db.Model):
    __bind_key__ = 'writeonly'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    address = db.Column(db.String(255))
    addressLine2 = db.Column(db.String(255))
    comments = db.Column(db.String(255))
    country = db.Column(db.String(255))
    district = db.Column(db.String(255))
    dob = db.Column(db.String(255))
    email = db.Column(db.String(255))
    employerComments = db.Column(db.String(255))
    employername = db.Column(db.String(255))
    employernumber = db.Column(db.String(255))
    file = db.Column(db.String(255))
    formCreatedDate = db.Column(db.String(255))
    immigrationstatus = db.Column(db.String(255))
    incomerange = db.Column(db.String(255))
    isExistingMember = db.Column(db.String(255))
    maidenName = db.Column(db.String(255))
    maritalstatus = db.Column(db.String(255))
    memberLastName = db.Column(db.String(255))
    memberfirstName = db.Column(db.String(255))
    middlename = db.Column(db.String(255))
    pendingFrom = db.Column(db.String(255))
    phoneNumber = db.Column(db.String(255))
    postalcode = db.Column(db.String(255))
    startdate = db.Column(db.String(255))
    startemployment = db.Column(db.String(255))
    status = db.Column(db.String(255))
    title = db.Column(db.String(255))
    tokenID = db.Column(db.String(255))

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