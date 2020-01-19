import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_app(app):
    # db_user = os.getenv('DBAAS_USER_NAME', default='SYSTEM')
    # db_password = os.getenv('DBAAS_USER_PASSWORD', default='')
    # db_port = os.getenv('DBAAS_PORT', default='1521')
    # db_host = os.getenv('DBAAS_HOST', default='')
    # db_service_name = os.getenv('DBAAS_SERVICE_NAME', default='')
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'oracle+cx_oracle://{db_user}:{db_password}@{db_host}:{str(db_port)}/?service_name={db_service_name}'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../test.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()
