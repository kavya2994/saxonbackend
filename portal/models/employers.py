from . import db


class Employers(db.Model):
    __bind_key__ = 'readonly'

    username = db.Column(db.String(255), primary_key=True, nullable=False)

    displayname = db.Column(db.String(255))
    email = db.Column(db.String(255))
    employer_id = db.Column(db.String(255))
    managedEmployers = db.Column(db.String(255))
    sessionTime = db.Column(db.String(255))
    status = db.Column(db.String(255))

# [{
#   'displayname': 'Manomay cs',
#   'email': 'deepika.bharatula@manomay.biz',
#   'employer_id': 'manomay',
#   'managedEmployers': [<google.cloud.firestore_v1.document.DocumentReference object at 0x108562610>],
#   'sessionTime': '3600000',
#   'status': 'active',
#   'username': 'manomay'},
#  {'displayname': 'Saxon Pensions',
#   'email': 'saxon@saxon.cy',
#   'employer_id': '000501',
#   'frequency': '',
#   'language': 'English UK',
#   'managedEmployers': [<google.cloud.firestore_v1.document.DocumentReference object at 0x108562d50>],
#   'sessionTimeout': 'One Hour',
#   'status': 'inactive',
#   'timezone': '',
#   'username': 'saxon'}]
