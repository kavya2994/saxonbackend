import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_app(app):
    readonly_db_connection_string = os.getenv("DBAAS_READONLY_CONNECTION_STRING", default="sqlite:///../data/readonly.sqlite")
    writeonly_db_connection_string = os.getenv("DBAAS_WRITEONLY_CONNECTION_STRING", default="sqlite:///../data/writeonly.sqlite")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_BINDS'] = {
        'readonly': readonly_db_connection_string,
        'writeonly': writeonly_db_connection_string,
    }

    db.init_app(app)
    with app.app_context():
        db.create_all(bind=['writeonly'])
