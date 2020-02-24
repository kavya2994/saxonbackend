from . import db


class EmpMemRelation(db.Model):
    __bind_key__ = 'writeonly'
    EmployerID = db.Column(db.String(255), nullable=False),
    EmployerName = db.Column(db.String(255)),
    MemberID = db.Column(db.String(255), nullable=False),
    MemberName = db.Column(db.String(255))
