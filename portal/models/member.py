from . import db
from .employer_member_relation import EmpMemRel
from sqlalchemy import Sequence


class Member(db.Model):
    __bind_key__ = 'writeonly'
    __tablename__ = 'member'

    MemberID = db.Column(db.Integer, Sequence('member_id_seq'), primary_key=True, nullable=False)

    Username = db.Column(db.String(255), unique=True)
    DisplayName = db.Column(db.String(255))
    Email = db.Column(db.String(255))
    Country = db.Column(db.String(255))
    DOB = db.Column(db.DateTime)
    DateOfEmployment = db.Column(db.DateTime)
    DateOfPlanEntry = db.Column(db.DateTime)
    EarlyRetirementDate = db.Column(db.DateTime)
    KYCode = db.Column(db.String(255))
    NormalRetirementDate = db.Column(db.DateTime)
    Pobox = db.Column(db.String(255))
    SessionTime = db.Column(db.String(255))
    Status = db.Column(db.String(255))
