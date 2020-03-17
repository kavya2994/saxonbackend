from . import db
from sqlalchemy import Sequence
from flask_restx import fields


class BeneficiaryFromRead(db.Model):
    __bind_key__ = 'readonly'
    __tablename__ = 'CV$IF_BENEFICIARY'

    MKEY = db.Column(db.String(255), primary_key=True, nullable=False)
    BEN_NAME = db.Column(db.String(255))
    RELNAME = db.Column(db.String(255))
