from . import db
from sqlalchemy import Sequence


class Contributionform(db.Model):
    __bind_key__ = 'writeonly'

    FormID = db.Column(db.Integer, Sequence('contributionform_id_seq'), primary_key=True, nullable=False)

    EmployerName = db.Column(db.String(255))
    StartDate = db.Column(db.Date)
    EndDate = db.Column(db.Date)
    Comments = db.Column(db.String(255))
    Status = db.Column(db.String(255))
    Date = db.Column(db.Date)
    PendingFrom = db.Column(db.String(255))
    EmployerID = db.Column(db.String(255))
    FilePath = db.Column(db.String(255))
    LastModifiedDate = db.Column(db.DateTime)
