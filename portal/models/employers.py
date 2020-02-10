from . import db


class Employers(db.Model):
    __bind_key__ = 'readonly'

    EmployerID = db.Column(db.String(255))
    Username = db.Column(db.String(255), primary_key=True, nullable=False)

    Displayname = db.Column(db.String(255))
    Email = db.Column(db.String(255))
    ManagedEmployers = db.Column(db.String(255))
    SessionTime = db.Column(db.String(255))
    Status = db.Column(db.String(255))
