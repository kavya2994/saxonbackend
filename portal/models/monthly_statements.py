from . import db


class MonthlyStatements(db.Model):
    __bind_key__ = 'readonly'
    __tablename__ = 'CV$IF_MONTHLY_STMT'

    PROCESSID = db.Column(db.Integer, primary_key=True, nullable=False)
    MKEY = db.Column(db.String(255), nullable=False)
    MEMNO = db.Column(db.String(255), nullable=False)
    DATE_FROM = db.Column(db.DateTime)
    DATE_TO = db.Column(db.DateTime)
    FILENAME = db.Column(db.String(255))
    FILEITEM = db.Column(db.Binary)