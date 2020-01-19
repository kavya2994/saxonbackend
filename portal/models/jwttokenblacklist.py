from . import db


class JWTTokenBlacklist(db.Model):
    LoggedOutTime = db.Column(db.String(255))
    JWTToken = db.Column(db.String(255))
