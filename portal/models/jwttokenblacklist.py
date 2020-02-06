from . import db


class JWTTokenBlacklist(db.Model):
    __bind_key__ = 'writeonly'

    JWTToken = db.Column(db.String(255), primary_key=True, nullable=False)
    LoggedOutTime = db.Column(db.String(255))
