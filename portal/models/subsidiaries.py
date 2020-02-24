from . import db
from flask_restplus import fields
from sqlalchemy import Sequence


class Subsidiaries(db.Model):
    __bind_key__ = 'writeonly'

    TransID = db.Column(db.Integer, Sequence('trans_id_seq'), primary_key=True, nullable=False)
    SubsidiaryID = db.Column(db.String(255), nullable=False)
    SubsidiaryName = db.Column(db.String(255))

    EmployerName = db.Column(db.String(255))
    EmployerID = db.Column(db.String(255), nullable=False)
