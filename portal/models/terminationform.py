from . import db


class Terminationform(db.Model):
    __bind_key__ = 'writeonly'

    id = db.Column(db.Integer, primary_key=True, nullable=False)

    employername = db.Column(db.String(255))
    date = db.Column(db.DateTime)
    memberName = db.Column(db.String(255))
    employernumber = db.Column(db.String(255))
    email = db.Column(db.String(255))
    finaldateofemployment = db.Column(db.DateTime)
    reasonforTermination = db.Column(db.String(255))
    lastDeduction = db.Column(db.String(255))
    address = db.Column(db.String(255))
    addressLine2 = db.Column(db.String(255))
    district = db.Column(db.String(255))
    postalcode = db.Column(db.String(255))
    country = db.Column(db.String(255))
    incomerange = db.Column(db.String(255))
    status = db.Column(db.String(255))
    employerID = db.Column(db.String(255))
    pendingFrom = db.Column(db.String(255))


#  {'address': '503, Cherry Street Apartment',
#   'addressLine2': '118',
#   'comments': 'term',
#   'country': 'AF',
#   'district': 'k',
#   'email': 'helloo@gmail.com',
#   'employername': 'Saxon Pensions',
#   'employernumber': 'saxon',
#   'finalDateofEmployement': DatetimeWithNanoseconds(2019, 12, 5, 18, 30, tzinfo=<UTC>),
#   'formCreatedDate': DatetimeWithNanoseconds(2019, 12, 6, 8, 4, 22, 565843, tzinfo=<UTC>),
#   'formType': 'termination',
#   'incomerange': '20',
#   'lastDeductionPeriod': DatetimeWithNanoseconds(2019, 12, 5, 18, 30, tzinfo=<UTC>),
#   'member_id': '28634',
#   'memberfirstName': 'Member124',
#   'pendingFrom': 'member',
#   'phoneNumber': '9866989999',
#   'postalcode': '77844',
#   'reasonForTermination': 'Left Employment',
#   'status': 'pending'},
