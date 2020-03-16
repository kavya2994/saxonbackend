from . import db


class EmployerView(db.Model):
    __bind_key__ = 'readonly'
    __tablename__ = 'CV$IF_EMPLOYER'

    ERKEY = db.Column(db.String(255), primary_key=True, nullable=False)
    ERNO = db.Column(db.String(255), unique=True)
    ENAME = db.Column(db.String(255))
    SNAME = db.Column(db.String(255))
    EMAIL = db.Column(db.String(255))
    ENTRY = db.Column(db.DateTime)
    TERMDATE = db.Column(db.DateTime)
