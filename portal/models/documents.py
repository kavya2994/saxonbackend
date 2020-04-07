from . import db
from sqlalchemy import Sequence


class Documents(db.Model):
    __bind_key__ = 'writeonly'

    FormID = db.Column(db.Integer, Sequence('Document_id_seq'), primary_key=True, nullable=False)

    EmployerName = db.Column(db.String(255))
    Comments = db.Column(db.String(255))
    Status = db.Column(db.String(255))
    Date = db.Column(db.DateTime)
    PendingFrom = db.Column(db.String(255))
    EmployerID = db.Column(db.String(255))
    FilePath = db.Column(db.String(255))
    LastModifiedDate = db.Column(db.DateTime)
