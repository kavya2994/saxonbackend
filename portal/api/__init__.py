from flask import Blueprint
from flask_restplus import Api


api = Api(version='1.0', title='Saxon Pensions API', doc='/doc/')

def init_app(app):
    v1 = Blueprint('api', __name__, url_prefix='/v1', template_folder='templates')
    api.init_app(v1)
    app.register_blueprint(v1)
