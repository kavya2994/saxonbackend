from . import db


EmpMemRel = db.Table('employers_members',
    db.Column('EmployerID', db.Integer, db.ForeignKey('employer.EmployerID'), primary_key=True),
    db.Column('EmployerName', db.String(255)),
    db.Column('MemberID', db.Integer, db.ForeignKey('member.MemberID'), primary_key=True),
    db.Column('MemberName', db.String(255)),
    info={'bind_key': 'writeonly'}
)
