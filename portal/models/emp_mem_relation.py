from sqlalchemy import Sequence

from . import db


class EmpMemRelation(db.Model):
    __bind_key__ = 'writeonly'
    EmpMemID = db.Column(db.Integer, Sequence('empmem_id_seq'), primary_key=True, nullable=False)
    EmployerID = db.Column(db.String(255), nullable=False),
    EmployerName = db.Column(db.String(255)),
    MemberID = db.Column(db.String(255), nullable=False),
    MemberName = db.Column(db.String(255))
