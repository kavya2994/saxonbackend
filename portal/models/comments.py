from . import db


class Comments(db.Model):
    __bind_key__ = 'writeonly'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    formID = db.Column(db.Integer)

    role = db.Column(db.String(255))
    comment = db.Column(db.String(255))
    date = db.Column(db.String(255))
