from . import db
from flask_restplus import fields
from sqlalchemy import Sequence


class Subsidiaries(db.Model):
    __bind_key__ = 'writeonly'

    SubsidiaryID = db.Column(db.Integer, Sequence('subsidiaries_id_seq'), primary_key=True, nullable=False)
    SubsidiaryName = db.Column(db.String(255))

    EmployerName = db.Column(db.String(255))
    EmployerID = db.Column(db.String(255))
