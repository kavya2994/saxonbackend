from . import db


class JWTTokenBlacklist(db.Model):
    __bind_key__ = 'writeonly'

    loggedOutTime = db.Column(db.String(255))
    JWTToken = db.Column(db.String(255))
