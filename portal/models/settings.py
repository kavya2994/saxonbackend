from . import db
from sqlalchemy import Sequence


class Settings(db.Model):
    __bind_key__ = 'writeonly'

    SettingID = db.Column(db.Integer, Sequence('setting_id_seq'), primary_key=True, nullable=False)
    NotificationEmail = db.Column(db.String(255))
    ArchiveDays = db.Column(db.String(255))
    ReviewIP = db.Column(db.String(255))
    RMIP = db.Column(db.String(255))
    LastRun = db.Column(db.String(255))
    Sync = db.Column(db.String(255))
