from . import db


class EmployerDealingDayRPT(db.Model):
    __bind_key__ = 'readonly'
    __tablename__ = 'CV$IF_EMPLOYER_DEALING_DAY_RPT'

    PROCESSID = db.Column(db.Integer, primary_key=True, nullable=False)
    ERKEY = db.Column(db.String(255), nullable=False)
    DATE_FROM = db.Column(db.DateTime)
    DATE_TO = db.Column(db.DateTime)
    FILENAME = db.Column(db.String(255))
    FILEITEM = db.Column(db.Binary)
