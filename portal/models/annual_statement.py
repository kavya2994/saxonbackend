from . import db


class AnnualStatements(db.Model):
    __bind_key__ = 'readonly'
    __tablename__ = 'CV$IF_ANNUAL_STMT'

    MKEY = db.Column(db.String(255), primary_key=True, nullable=False)
    MEMNO = db.Column(db.String(255), unique=True, nullable=False)
    DATE_FROM = db.Column(db.DateTime)
    DATE_TO = db.Column(db.DateTime)
    FILENAME = db.Column(db.String(255))
    FILEITEM = db.Column(db.Binary)