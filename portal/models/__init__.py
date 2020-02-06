import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_app(app):
    readonly_db_connection_string = app.config['DBAAS_READONLY_CONNECTION_STRING'] \
        if 'DBAAS_READONLY_CONNECTION_STRING' in app.config else "sqlite:///../data/readonly.sqlite"

    writeonly_db_connection_string = app.config['DBAAS_WRITEONLY_CONNECTION_STRING'] \
        if 'DBAAS_WRITEONLY_CONNECTION_STRING' in app.config else "sqlite:///../data/writeonly.sqlite"

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_BINDS'] = {
        'readonly': readonly_db_connection_string,
        'writeonly': writeonly_db_connection_string,
    }

    db.init_app(app)
    with app.app_context():
        from .contributionform import Contributionform
        from .jwttokenblacklist import JWTTokenBlacklist
        from .terminationform import Terminationform
        from .beneficiary import Beneficiary
        from .token import Token
        from .comments import Comments
        from .enrollmentform import Enrollmentform
        from .security_question import SecurityQuestion
        from .users import Users

        db.create_all(bind=['writeonly'])
        db.session.commit()
