from . import db


EmpMemRel = db.Table('employers_members',
    db.Column('EmployerID', db.Integer, db.ForeignKey('employer.EmployerID'), primary_key=True),
    db.Column('MemberID', db.Integer, db.ForeignKey('member.MemberID'), primary_key=True),
    info={'bind_key': 'writeonly'}
)
