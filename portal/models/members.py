from . import db


class Members(db.Model):
    __bind_key__ = 'readonly'

    username = db.Column(db.String(255), primary_key=True, nullable=False)

    employers = db.Column(db.String(255))
    Country = db.Column(db.String(255))
    DOB = db.Column(db.String(255))
    Date_of_Employement = db.Column(db.String(255))
    Date_of_Plan_Entry = db.Column(db.String(255))
    Early_Retirement_Date = db.Column(db.String(255))
    KYCode = db.Column(db.String(255))
    Normal_Retirement_Date = db.Column(db.String(255))
    Pobox = db.Column(db.String(255))
    displayname = db.Column(db.String(255))
    email = db.Column(db.String(255))
    member_id = db.Column(db.String(255))
    sessionTime = db.Column(db.String(255))
    status = db.Column(db.String(255))


# [{'Country': 'Cayman Islands',
#   'DOB': '22-AUG-95',
#   'Date_of_Employement': '01-JUL-10',
#   'Date_of_Plan_Entry': '25-SEP-06',
#   'Early_Retirement_Date': '22-AUG-38',
#   'KYCode': '1614',
#   'Normal_Retirement_Date': '22-AUG-48',
#   'Pobox': '165',
#   'displayname': 'Member124',
#   'email': 'deepika.bharatula@manomay.biz',
#   'employers': [<google.cloud.firestore_v1.document.DocumentReference object at 0x1085629d0>],
#   'member_id': '28634',
#   'sessionTime': '600000',
#   'status': 'active',
#   'username': 'member'},
#  {'displayname': 'Member',
#   'email': 'jungle@gmail.com',
#   'employers': [<google.cloud.firestore_v1.document.DocumentReference object at 0x108562e90>],
#   'member_id': '28633',
#   'phoneNumber': '98657412334',
#   'sessionTime': 600000,
#   'status': 'active',
#   'username': '28633'}]
