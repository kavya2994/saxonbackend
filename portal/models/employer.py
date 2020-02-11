from . import db
from .employer_member_relation import EmpMemRel
from sqlalchemy import Sequence



class Employer(db.Model):
    __bind_key__ = 'writeonly'
    __tablename__ = 'employer'

    EmployerID = db.Column(db.Integer, Sequence('employer_id_seq'), primary_key=True, nullable=False)

    Username = db.Column(db.String(255), unique=True)
    Displayname = db.Column(db.String(255))
    Email = db.Column(db.String(255))
    SessionTime = db.Column(db.String(255))
    Status = db.Column(db.String(255))

    Members = db.relationship('Member', secondary=EmpMemRel, lazy='subquery',
        backref=db.backref('Employers', lazy=True))
