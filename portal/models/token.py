from . import db


class Token(db.Model):
    __bind_key__ = 'writeonly'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    formID = db.Column(db.Integer)

    FormCreatedDate = db.Column(db.DateTime)
    FormStatus = db.Column(db.String(255))
    FormType = db.Column(db.String(255))
    InitiatedBy = db.Column(db.String(255))
    InitiatedDate = db.Column(db.DateTime)
    pendingFrom = db.Column(db.String(255))
    TokenStatus = db.Column(db.String(255))
    EmployerID = db.Column(db.String(255))
    OlderTokenID = db.Column(db.String(255))

# {'employernumber': 'saxon',
#   'formCreatedDate': DatetimeWithNanoseconds(2019, 12, 4, 13, 36, 26, 842370, tzinfo=<UTC>),
#   'formType': 'Enrollment',
#   'id': '5C8qylkUSFlCmNjMfzqy',
#   'initiatedBy': 'saxon',
#   'memberfirstName': 'Raj1',
#   'pendingFrom': 'member',
#   'status': 'submitted',
#   'tokenStatus': 'inactive'},
#  {'employernumber': 'saxon',
#   'formCreatedDate': DatetimeWithNanoseconds(2019, 11, 30, 7, 18, 16, 526460, tzinfo=<UTC>),
#   'formType': 'Enrollment',
#   'id': 'hE1QuXkpCd5V5QbvsXRo',
#   'initiatedBy': 'saxon',
#   'memberfirstName': 'test-notification mail',
#   'pendingFrom': 'member',
#   'status': 'submitted',
#   'tokenStatus': 'inactive'},
