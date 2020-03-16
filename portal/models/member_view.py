from . import db


class MemberView(db.Model):
    __bind_key__ = 'readonly'
    __tablename__ = 'CV$IF_MEMBER'

    MKEY = db.Column(db.String(255), primary_key=True, nullable=False)
    MEMNO = db.Column(db.String(255), unique=True)
    FNAME = db.Column(db.String(255))
    LNAME = db.Column(db.String(255))
    EMAIL = db.Column(db.String(255))
    BIRTH = db.Column(db.DateTime)
    ENTRY_DATE = db.Column(db.DateTime)
    NR_DATE = db.Column(db.DateTime)
    HIRE = db.Column(db.DateTime)
    PSTATUS = db.Column(db.String(255))
    EMPOYER = db.Column(db.String(255))
    STREET1 = db.Column(db.String(255))
    STREET2 = db.Column(db.String(255))
    EM_STATUS = db.Column(db.String(255))
    CITY = db.Column(db.String(255))
    POSTAL = db.Column(db.String(255))
    COUNTRY = db.Column(db.String(255))
    BEN_NAMES = db.Column(db.String(255))
    RELNAME = db.Column(db.String(255))
